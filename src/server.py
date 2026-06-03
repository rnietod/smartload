"""
SmartLoad - FastAPI Backend Server
----------------------------------
This server loads athlete workload CSV data and the pre-trained ACWR prediction model,
provides APIs to fetch player stats and history, logs new workouts, and performs a 
continuous 15-day forward simulation of the physiological ACWR and the ML model's prediction.

Author: Antigravity
Date: June 2026
License: Apache License, Version 2.0
"""

import os
import joblib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="SmartLoad - ACWR Prediction & Simulation API", version="2.0")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the exact domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "data_acute_vs_chronic.csv")
MODEL_PATH = os.path.join(BASE_DIR, "models", "best_acwr_model.joblib")

# Global data holders
df_raw = None
df_processed = None
model_data = None
model = None

# Realistic player metadata dictionary
PLAYER_PROFILES = {
    37191: {
        "name": "Luka 'El Mago' Modrić",
        "avatar": "/avatars/player1.png",
        "number": 10,
        "nationality": "Croacia"
    },
    88732: {
        "name": "Karim 'El Depredador' Benzema",
        "avatar": "/avatars/player2.png",
        "number": 9,
        "nationality": "Francia"
    },
    82742: {
        "name": "Sergio 'El Capitán' Ramos",
        "avatar": "/avatars/player3.png",
        "number": 4,
        "nationality": "España"
    },
    64878: {
        "name": "Toni 'El Metrónomo' Kroos",
        "avatar": "/avatars/player4.png",
        "number": 8,
        "nationality": "Alemania"
    },
    42978: {
        "name": "Fede 'La Bestia' Valverde",
        "avatar": "/avatars/player5.png",
        "number": 15,
        "nationality": "Uruguay"
    },
    53111: {
        "name": "Vinicius 'El Diablo' Jr.",
        "avatar": "/avatars/player6.png",
        "number": 7,
        "nationality": "Brasil"
    }
}

DEFAULT_PROFILE = {
    "name": "Jugador Sin Nombre",
    "avatar": "/avatars/player3.png",
    "number": 99,
    "nationality": "Desconocida"
}

# --- Core Data Functions (Adapted from data_engineering.py for fast execution) ---

def load_and_process_database():
    """Loads raw CSV, runs the data engineering pipeline in-memory, and updates globals."""
    global df_raw, df_processed, model, model_data
    
    print(f"[*] Loading raw database from: {CSV_PATH}")
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"Database CSV not found at {CSV_PATH}")
        
    df_raw = pd.read_csv(CSV_PATH)
    
    # 1. Parsing and cleaning
    df = df_raw.copy()
    df['period_start_time'] = pd.to_datetime(df['period_start_time'])
    df['date'] = df['period_start_time'].dt.date
    df['date'] = pd.to_datetime(df['date'])
    df['date_of_birth'] = pd.to_datetime(df['date_of_birth'])
    df['is_official_match'] = df['is_official_match'].fillna(0).astype(int)
    
    numeric_cols = ['total_distance', 'acc_band7plus_total_effort_count', 
                    'velocity_band6plus7_total_distance', 'height', 'weight']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
        
    # 2. Daily aggregation per player
    agg_funcs = {
        'total_distance': 'sum',
        'acc_band7plus_total_effort_count': 'sum',
        'velocity_band6plus7_total_distance': 'sum',
        'is_official_match': 'max',
        'height': 'mean',
        'weight': 'mean',
        'position_name_en': 'first',
        'date_of_birth': 'first'
    }
    daily_df = df.groupby(['player_id', 'date']).agg(agg_funcs).reset_index()
    
    # 3. Continuous timeline per player (fill rest days with 0)
    players = daily_df['player_id'].unique()
    reindexed_frames = []
    
    for player in players:
        player_df = daily_df[daily_df['player_id'] == player].set_index('date')
        min_date = player_df.index.min()
        max_date = player_df.index.max()
        all_dates = pd.date_range(start=min_date, end=max_date, freq='D')
        
        player_reindexed = player_df.reindex(all_dates)
        player_reindexed.index.name = 'date'
        player_reindexed = player_reindexed.reset_index()
        
        player_reindexed['player_id'] = player
        player_reindexed['position_name_en'] = player_reindexed['position_name_en'].ffill().bfill()
        player_reindexed['date_of_birth'] = player_reindexed['date_of_birth'].ffill().bfill()
        player_reindexed['height'] = player_reindexed['height'].replace(0, np.nan).ffill().bfill()
        player_reindexed['weight'] = player_reindexed['weight'].replace(0, np.nan).ffill().bfill()
        
        workload_cols = ['total_distance', 'acc_band7plus_total_effort_count', 
                         'velocity_band6plus7_total_distance', 'is_official_match']
        for col in workload_cols:
            player_reindexed[col] = player_reindexed[col].fillna(0.0)
            
        reindexed_frames.append(player_reindexed)
        
    df_continuous = pd.concat(reindexed_frames, ignore_index=True)
    
    # 4. Compute ACWR and sliding features
    df_continuous = df_continuous.sort_values(by=['player_id', 'date']).reset_index(drop=True)
    metrics = {
        'total_distance': 'dist',
        'acc_band7plus_total_effort_count': 'accel',
        'velocity_band6plus7_total_distance': 'hi_vel'
    }
    
    for metric, prefix in metrics.items():
        # Acute Load (7-day daily average)
        df_continuous[f'acute_{prefix}'] = df_continuous.groupby('player_id')[metric].transform(
            lambda x: x.rolling(window=7, min_periods=1).mean()
        )
        # Chronic Load (28-day daily average)
        df_continuous[f'chronic_{prefix}'] = df_continuous.groupby('player_id')[metric].transform(
            lambda x: x.rolling(window=28, min_periods=1).mean()
        )
        # ACWR = Acute / (Chronic + epsilon)
        df_continuous[f'acwr_{prefix}'] = df_continuous[f'acute_{prefix}'] / (df_continuous[f'chronic_{prefix}'] + 1e-5)
        df_continuous[f'acwr_{prefix}'] = df_continuous[f'acwr_{prefix}'].replace([np.inf, -np.inf], 0.0).fillna(0.0)
        
        # Optimized Features (lags)
        df_continuous[f'acwr_{prefix}_lag1'] = df_continuous.groupby('player_id')[f'acwr_{prefix}'].shift(1)
        df_continuous[f'acwr_{prefix}_lag2'] = df_continuous.groupby('player_id')[f'acwr_{prefix}'].shift(2)
        df_continuous[f'acwr_{prefix}_lag3'] = df_continuous.groupby('player_id')[f'acwr_{prefix}'].shift(3)
        df_continuous[f'acute_{prefix}_lag1'] = df_continuous.groupby('player_id')[f'acute_{prefix}'].shift(1)
        
        # Momentum
        df_continuous[f'{prefix}_velocity_7d'] = df_continuous[f'acute_{prefix}'] - df_continuous.groupby('player_id')[f'acute_{prefix}'].shift(7)
        df_continuous[f'{prefix}_chronic_diff'] = df_continuous[f'acute_{prefix}'] - df_continuous[f'chronic_{prefix}']
        
    # Fill remaining NaNs from lagging
    lag_cols = [c for c in df_continuous.columns if 'lag' in c or 'velocity' in c or 'diff' in c]
    df_continuous[lag_cols] = df_continuous[lag_cols].fillna(0.0)
    
    # Age calculation
    df_continuous['age_years'] = (df_continuous['date'] - df_continuous['date_of_birth']).dt.days / 365.25
    
    # Fill any remaining NaNs and Infs to prevent JSON serialization errors
    df_continuous = df_continuous.replace([np.inf, -np.inf], 0.0).fillna(0.0)
    
    df_processed = df_continuous
    print(f"[+] Loaded and recalculated continuous database. Shape: {df_processed.shape}")
    
    # Load ML Model
    if os.path.exists(MODEL_PATH):
        print(f"[*] Loading model from: {MODEL_PATH}")
        model_data = joblib.load(MODEL_PATH)
        model = model_data['model']
        print(f"[+] Model '{model_data['model_name']}' loaded successfully.")
    else:
        print("[⚠️] Model file not found. Predictions will use a fast linear simulation fallback.")

# Initialize data on startup
@app.on_event("startup")
def startup_event():
    load_and_process_database()

# --- API Models ---

class WorkoutRecord(BaseModel):
    player_id: int
    date: str  # YYYY-MM-DD
    total_distance: float
    acc_band7plus_total_effort_count: int
    velocity_band6plus7_total_distance: float
    is_official_match: int

class ScheduledWorkout(BaseModel):
    day_idx: int  # 0 to 14 (representing day + 1 to day + 15 in future)
    type: str  # "Descanso", "Sesión Ligera", "Entrenamiento Normal", "Fuerza", "Partido"
    total_distance: float
    acc_band7plus_total_effort_count: int
    velocity_band6plus7_total_distance: float
    is_official_match: int

class SimulationRequest(BaseModel):
    player_id: int
    plan: list[ScheduledWorkout]

# --- Helper functions ---

def calculate_acwr_zone(acwr):
    """Classifies ACWR into green (optimal), yellow (caution), and red (danger) zones."""
    if acwr < 0.8:
        return "Subcarga (Desentrenamiento)"
    elif 0.8 <= acwr <= 1.3:
        return "Óptimo (Bajo Riesgo)"
    elif 1.3 < acwr <= 1.5:
        return "Precaución (Fatiga Moderada)"
    else:
        return "Peligro (Alto Riesgo de Lesión)"

def calculate_acwr_color(acwr):
    """Returns color theme for zones."""
    if acwr < 0.8:
        return "danger"  # Subcarga is danger too
    elif 0.8 <= acwr <= 1.3:
        return "success"
    elif 1.3 < acwr <= 1.5:
        return "warning"
    else:
        return "danger"

# --- Endpoints ---

@app.get("/api/players")
def get_players():
    """Lists all players with their profiles, positions, latest records and ACWR status."""
    global df_processed
    if df_processed is None:
        raise HTTPException(status_code=500, detail="Data is not loaded.")
        
    players_list = []
    
    # Group by player and get the latest chronological row
    for player_id, group in df_processed.groupby("player_id"):
        latest_row = group.sort_values("date").iloc[-1]
        profile = PLAYER_PROFILES.get(player_id, DEFAULT_PROFILE)
        
        acwr_val = float(latest_row["acwr_dist"])
        
        players_list.append({
            "player_id": int(player_id),
            "name": profile["name"],
            "avatar": profile["avatar"],
            "number": profile["number"],
            "nationality": profile["nationality"],
            "position": latest_row["position_name_en"],
            "height": float(latest_row["height"]),
            "weight": float(latest_row["weight"]),
            "age": round(float(latest_row["age_years"]), 1),
            "latest_date": latest_row["date"].strftime("%Y-%m-%d"),
            "acwr_dist": round(acwr_val, 2),
            "acwr_accel": round(float(latest_row["acwr_accel"]), 2),
            "acwr_hi_vel": round(float(latest_row["acwr_hi_vel"]), 2),
            "acute_dist": round(float(latest_row["acute_dist"]), 1),
            "chronic_dist": round(float(latest_row["chronic_dist"]), 1),
            "zone": calculate_acwr_zone(acwr_val),
            "color": calculate_acwr_color(acwr_val)
        })
        
    return players_list

@app.get("/api/players/{player_id}/history")
def get_player_history(player_id: int):
    """Returns the full chronological workload history of a specific player."""
    global df_processed
    if df_processed is None:
        raise HTTPException(status_code=500, detail="Data is not loaded.")
        
    player_data = df_processed[df_processed["player_id"] == player_id]
    if player_data.empty:
        raise HTTPException(status_code=404, detail="Player not found")
        
    player_data = player_data.sort_values("date")
    profile = PLAYER_PROFILES.get(player_id, DEFAULT_PROFILE)
    
    history = []
    for _, row in player_data.iterrows():
        acwr_val = float(row["acwr_dist"])
        history.append({
            "date": row["date"].strftime("%Y-%m-%d"),
            "total_distance": float(row["total_distance"]),
            "acc_band7plus_total_effort_count": int(row["acc_band7plus_total_effort_count"]),
            "velocity_band6plus7_total_distance": float(row["velocity_band6plus7_total_distance"]),
            "acute_dist": round(float(row["acute_dist"]), 1),
            "chronic_dist": round(float(row["chronic_dist"]), 1),
            "acwr_dist": round(acwr_val, 2),
            "acwr_accel": round(float(row["acwr_accel"]), 2),
            "acwr_hi_vel": round(float(row["acwr_hi_vel"]), 2),
            "zone": calculate_acwr_zone(acwr_val),
            "color": calculate_acwr_color(acwr_val)
        })
        
    return {
        "player_id": player_id,
        "name": profile["name"],
        "profile": {**profile, "position": player_data.iloc[-1]["position_name_en"]},
        "history": history
    }

@app.post("/api/exercises")
def log_workout(record: WorkoutRecord):
    """
    Logs a new actual session/workout to the raw CSV database, 
    re-runs pipeline, and updates in-memory states.
    """
    global df_raw
    try:
        # Create new record row
        new_row = {
            "player_id": record.player_id,
            "period_id": f"period_{int(datetime.now().timestamp())}",
            "period_name": "Logged Session",
            "activity_id": f"activity_{int(datetime.now().timestamp() + 10)}",
            "period_start_time": f"{record.date}T09:00:00Z",  # Assume morning workout
            "position_name_en": df_raw[df_raw["player_id"] == record.player_id]["position_name_en"].iloc[0] if not df_raw[df_raw["player_id"] == record.player_id].empty else "Central Midfielder",
            "is_official_match": record.is_official_match,
            "total_distance": record.total_distance,
            "acc_band7plus_total_effort_count": record.acc_band7plus_total_effort_count,
            "velocity_band6plus7_total_distance": record.velocity_band6plus7_total_distance,
            "height": df_raw[df_raw["player_id"] == record.player_id]["height"].iloc[0] if not df_raw[df_raw["player_id"] == record.player_id].empty else 180,
            "weight": df_raw[df_raw["player_id"] == record.player_id]["weight"].iloc[0] if not df_raw[df_raw["player_id"] == record.player_id].empty else 75,
            "date_of_birth": df_raw[df_raw["player_id"] == record.player_id]["date_of_birth"].iloc[0] if not df_raw[df_raw["player_id"] == record.player_id].empty else "2000-01-01"
        }
        
        # Append to CSV
        df_new = pd.DataFrame([new_row])
        df_new.to_csv(CSV_PATH, mode='a', header=False, index=False)
        
        # Reload database
        load_and_process_database()
        
        return {"status": "success", "message": "Workout successfully logged & ACWR metrics recalculated."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save workout: {str(e)}")

@app.post("/api/simulate")
def simulate_trajectory(req: SimulationRequest):
    """
    Simulates a continuous 15-day training sequence.
    Recalculates the exact physiological ACWR step-by-step for the next 15 days,
    and runs the ML Ridge Model to predict the ACWR curve day-by-day.
    """
    global df_processed, model, model_data
    
    player_id = req.player_id
    plan_dict = {p.day_idx: p for p in req.plan}
    
    # 1. Fetch player recent 28-day history to seat promedies mobiles
    player_history = df_processed[df_processed["player_id"] == player_id].sort_values("date")
    if player_history.empty:
        raise HTTPException(status_code=404, detail="Player history not found")
        
    latest_row = player_history.iloc[-1]
    latest_date = latest_row["date"]
    
    # We need the last 28 days of raw workouts to seed the rolling calculation
    raw_history = player_history.tail(28).copy()
    
    # 2. Iterate day by day for the next 15 days
    simulated_trajectory = []
    
    current_df = raw_history.copy()
    
    for day_idx in range(15):
        sim_date = latest_date + timedelta(days=day_idx + 1)
        
        # Get simulated plan workout for this day
        plan_workout = plan_dict.get(day_idx)
        if plan_workout:
            dist = plan_workout.total_distance
            accel = plan_workout.acc_band7plus_total_effort_count
            hi_vel = plan_workout.velocity_band6plus7_total_distance
            match = plan_workout.is_official_match
        else:
            # Default to rest
            dist = 0.0
            accel = 0
            hi_vel = 0.0
            match = 0
            
        # Append simulated row to current context
        new_sim_row = {
            "player_id": player_id,
            "date": sim_date,
            "total_distance": dist,
            "acc_band7plus_total_effort_count": accel,
            "velocity_band6plus7_total_distance": hi_vel,
            "is_official_match": match,
            "height": latest_row["height"],
            "weight": latest_row["weight"],
            "position_name_en": latest_row["position_name_en"],
            "date_of_birth": latest_row["date_of_birth"],
            "age_years": (sim_date - pd.to_datetime(latest_row["date_of_birth"])).days / 365.25
        }
        
        current_df = pd.concat([current_df, pd.DataFrame([new_sim_row])], ignore_index=True)
        
        # Compute exact mathematical rolling metrics for this simulated day
        # (Rolls over previous real history + new simulated days)
        for metric, prefix in {"total_distance": "dist", 
                               "acc_band7plus_total_effort_count": "accel", 
                               "velocity_band6plus7_total_distance": "hi_vel"}.items():
            
            # 7-day and 28-day rolling average on distance, accelerations, high velocity
            acute_val = current_df[metric].tail(7).mean()
            chronic_val = current_df[metric].tail(28).mean()
            acwr_val = acute_val / (chronic_val + 1e-5)
            
            current_df.loc[current_df.index[-1], f"acute_{prefix}"] = acute_val
            current_df.loc[current_df.index[-1], f"chronic_{prefix}"] = chronic_val
            current_df.loc[current_df.index[-1], f"acwr_{prefix}"] = acwr_val
            
            # Lag features (up to 3 steps back)
            for lag in [1, 2, 3]:
                if len(current_df) > lag:
                    current_df.loc[current_df.index[-1], f"acwr_{prefix}_lag{lag}"] = current_df.loc[current_df.index[-1 - lag], f"acwr_{prefix}"]
                else:
                    current_df.loc[current_df.index[-1], f"acwr_{prefix}_lag{lag}"] = 0.0
            
            # Acute lag
            if len(current_df) > 1:
                current_df.loc[current_df.index[-1], f"acute_{prefix}_lag1"] = current_df.loc[current_df.index[-2], f"acute_{prefix}"]
            else:
                current_df.loc[current_df.index[-1], f"acute_{prefix}_lag1"] = 0.0
                
            # Velocity and diff
            lag7_idx = len(current_df) - 8
            acute_lag7 = current_df.loc[current_df.index[lag7_idx], f"acute_{prefix}"] if lag7_idx >= 0 else acute_val
            current_df.loc[current_df.index[-1], f"{prefix}_velocity_7d"] = acute_val - acute_lag7
            current_df.loc[current_df.index[-1], f"{prefix}_chronic_diff"] = acute_val - chronic_val

        # Get latest active row with all computed variables
        row_features = current_df.iloc[-1].copy()
        
        # 3. Predict ACWR using the ML Ridge model
        predicted_acwr = float(row_features["acwr_dist"])  # Fallback to pure math
        
        if model is not None:
            try:
                # Prepare features dict matching training columns
                # Need to convert player positions to dummy columns or handle appropriately
                # We extract the features exact columns used by Scikit-Learn
                feat_names = model.feature_names_in_ if hasattr(model, "feature_names_in_") else []
                
                if len(feat_names) > 0:
                    input_row = {}
                    for col in feat_names:
                        # Handle One-Hot Encoded Position column (e.g. position_name_en_Full Back)
                        if col.startswith("position_name_en_"):
                            pos_class = col.replace("position_name_en_", "")
                            input_row[col] = 1.0 if row_features["position_name_en"] == pos_class else 0.0
                        elif col in row_features:
                            input_row[col] = float(row_features[col])
                        else:
                            input_row[col] = 0.0  # default fallback
                            
                    X_input = pd.DataFrame([input_row])[feat_names]
                    # Make ML prediction
                    predicted_acwr = float(model.predict(X_input)[0])
            except Exception as ml_err:
                print(f"[⚠️] ML Prediction failed: {str(ml_err)}. Falling back to physiological math.")
                
        # Clamps to avoid negative or extreme predictions
        predicted_acwr = max(0.0, predicted_acwr)
        
        # Mathematical exact values
        math_acwr = float(row_features["acwr_dist"])
        
        simulated_trajectory.append({
            "day_idx": day_idx,
            "date": sim_date.strftime("%Y-%m-%d"),
            "simulated_workout": {
                "total_distance": dist,
                "acc_band7plus_total_effort_count": accel,
                "velocity_band6plus7_total_distance": hi_vel,
                "is_official_match": match
            },
            "math_acwr_dist": round(math_acwr, 2),
            "predicted_acwr_dist": round(predicted_acwr, 2),
            "math_zone": calculate_acwr_zone(math_acwr),
            "math_color": calculate_acwr_color(math_acwr),
            "predicted_zone": calculate_acwr_zone(predicted_acwr),
            "predicted_color": calculate_acwr_color(predicted_acwr)
        })
        
    return {
        "player_id": player_id,
        "name": latest_row["position_name_en"],  # dummy
        "trajectory": simulated_trajectory
    }

if __name__ == "__main__":
    import uvicorn
    # In production, run on all interfaces or 127.0.0.1
    uvicorn.run(app, host="127.0.0.1", port=8000)
