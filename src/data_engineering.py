"""
SmartLoad - Data Engineering Pipeline
-------------------------------------
This script loads, cleans, and prepares the soccer athlete workload dataset.
It aggregates session/period data to a daily level per player, reindexes the timeline
to ensure continuous days (filling rest days with 0), calculates Acute and Chronic Workloads,
computes the ACWR (Acute:Chronic Workload Ratio), and performs a chronological train/test split.

Author: Antigravity
Date: May 2026
License: Apache License, Version 2.0
"""

import os
import numpy as np
import pandas as pd

def load_data(filepath):
    """Loads the athlete dataset from a CSV file."""
    print(f"[*] Loading raw data from: {filepath}")
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Data file not found at {filepath}")
    
    df = pd.read_csv(filepath)
    print(f"[+] Loaded {df.shape[0]} rows and {df.shape[1]} columns.")
    return df

def preprocess_data(df):
    """Performs initial cleaning and parsing of the data."""
    print("[*] Starting data preprocessing...")
    
    # 1. Parse timestamps and dates
    df['period_start_time'] = pd.to_datetime(df['period_start_time'])
    df['date'] = df['period_start_time'].dt.date
    df['date'] = pd.to_datetime(df['date'])
    
    # 2. Clean profile information
    df['date_of_birth'] = pd.to_datetime(df['date_of_birth'])
    
    # 3. Handle official match indicator (convert nulls to 0, values to 1)
    df['is_official_match'] = df['is_official_match'].fillna(0).astype(int)
    
    # 4. Handle other nulls in numerical metrics
    numeric_cols = [
        'total_distance', 
        'acc_band7plus_total_effort_count', 
        'velocity_band6plus7_total_distance',
        'height',
        'weight'
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
        
    print("[+] Preprocessing completed.")
    return df

def aggregate_daily_per_player(df):
    """
    Aggregates session/period data to a daily level per player.
    Since athletes can have multiple training periods/sessions per day,
    we sum active metrics and average static profile metrics.
    """
    print("[*] Aggregating data to daily level per player...")
    
    agg_funcs = {
        'total_distance': 'sum',
        'acc_band7plus_total_effort_count': 'sum',
        'velocity_band6plus7_total_distance': 'sum',
        'is_official_match': 'max',  # 1 if at least one session is a match
        'height': 'mean',
        'weight': 'mean',
        'position_name_en': 'first',
        'date_of_birth': 'first'
    }
    
    daily_df = df.groupby(['player_id', 'date']).agg(agg_funcs).reset_index()
    print(f"[+] Daily aggregation completed. Shape: {daily_df.shape}")
    return daily_df

def make_timeline_continuous(df):
    """
    Ensures that every player has a row for every calendar day between their first
    and last recorded activity. Rest days (with no training) are filled with 0s
    for activity metrics, while profile metrics (weight, height, position, DoB)
    are forward-filled. This is CRITICAL for accurate rolling ACWR calculations.
    """
    print("[*] Reindexing timeline to be continuous (filling rest days with 0)...")
    
    players = df['player_id'].unique()
    reindexed_frames = []
    
    for player in players:
        player_df = df[df['player_id'] == player].set_index('date')
        
        # Define continuous range of dates for this player
        min_date = player_df.index.min()
        max_date = player_df.index.max()
        all_dates = pd.date_range(start=min_date, end=max_date, freq='D')
        
        # Reindex
        player_reindexed = player_df.reindex(all_dates)
        player_reindexed.index.name = 'date'
        player_reindexed = player_reindexed.reset_index()
        
        # Fill identifier and profile columns
        player_reindexed['player_id'] = player
        player_reindexed['position_name_en'] = player_reindexed['position_name_en'].ffill().bfill()
        player_reindexed['date_of_birth'] = player_reindexed['date_of_birth'].ffill().bfill()
        
        # Profile features
        player_reindexed['height'] = player_reindexed['height'].replace(0, np.nan).ffill().bfill()
        player_reindexed['weight'] = player_reindexed['weight'].replace(0, np.nan).ffill().bfill()
        
        # Workload metrics (rest days = 0 workload)
        workload_cols = [
            'total_distance', 
            'acc_band7plus_total_effort_count', 
            'velocity_band6plus7_total_distance',
            'is_official_match'
        ]
        for col in workload_cols:
            player_reindexed[col] = player_reindexed[col].fillna(0.0)
            
        reindexed_frames.append(player_reindexed)
        
    full_continuous_df = pd.concat(reindexed_frames, ignore_index=True)
    print(f"[+] Reindexed continuous dataset. Shape: {full_continuous_df.shape}")
    return full_continuous_df

def compute_acwr_features(df):
    """
    Computes Acute Load, Chronic Load, and ACWR for key workload metrics.
    
    Definitions:
    - Acute Load: Rolling 7-day average of daily workload.
    - Chronic Load: Rolling 28-day average of daily workload.
    - ACWR: Acute Load / Chronic Load.
    """
    print("[*] Computing ACWR and rolling features...")
    
    # Sort chronologically per player
    df = df.sort_values(by=['player_id', 'date']).reset_index(drop=True)
    
    # Metrics to calculate ACWR for
    metrics = {
        'total_distance': 'dist',
        'acc_band7plus_total_effort_count': 'accel',
        'velocity_band6plus7_total_distance': 'hi_vel'
    }
    
    for metric, prefix in metrics.items():
        # Acute Load (7-day daily average)
        df[f'acute_{prefix}'] = df.groupby('player_id')[metric].transform(
            lambda x: x.rolling(window=7, min_periods=1).mean()
        )
        
        # Chronic Load (28-day daily average)
        df[f'chronic_{prefix}'] = df.groupby('player_id')[metric].transform(
            lambda x: x.rolling(window=28, min_periods=1).mean()
        )
        
        # ACWR = Acute / Chronic
        # We add a small epsilon to avoid division by zero
        df[f'acwr_{prefix}'] = df[f'acute_{prefix}'] / (df[f'chronic_{prefix}'] + 1e-5)
        
        # Clip potential infinity or extreme values
        df[f'acwr_{prefix}'] = df[f'acwr_{prefix}'].replace([np.inf, -np.inf], 0.0).fillna(0.0)
        
        # --- OPTION A OPTIMIZATION FEATURES ---
        # 1. ACWR Lags (1, 2, 3 days)
        df[f'acwr_{prefix}_lag1'] = df.groupby('player_id')[f'acwr_{prefix}'].shift(1)
        df[f'acwr_{prefix}_lag2'] = df.groupby('player_id')[f'acwr_{prefix}'].shift(2)
        df[f'acwr_{prefix}_lag3'] = df.groupby('player_id')[f'acwr_{prefix}'].shift(3)
        
        # 2. Acute Load Lag (1 day)
        df[f'acute_{prefix}_lag1'] = df.groupby('player_id')[f'acute_{prefix}'].shift(1)
        
        # 3. Load Momentum / Trend
        df[f'{prefix}_velocity_7d'] = df[f'acute_{prefix}'] - df.groupby('player_id')[f'acute_{prefix}'].shift(7)
        df[f'{prefix}_chronic_diff'] = df[f'acute_{prefix}'] - df[f'chronic_{prefix}']
        
    # Impute the initial NaN values from shifting with 0.0
    lag_cols = [c for c in df.columns if 'lag' in c or 'velocity' in c or 'diff' in c]
    df[lag_cols] = df[lag_cols].fillna(0.0)
        
    print("[+] ACWR and lag/momentum calculations completed.")
    return df

def create_predictive_target(df, horizon_days=15):
    """
    Creates target variables for predicting future workload states.
    For example, predicting the ACWR or workload 15 days in the future.
    """
    print(f"[*] Creating target variables shifted by {horizon_days} days into the future...")
    
    # Target: ACWR based on distance 15 days from now
    df['target_acwr_dist_15d'] = df.groupby('player_id')['acwr_dist'].shift(-horizon_days)
    
    # Target: High injury risk flag (ACWR > 1.5) 15 days from now
    df['target_high_risk_15d'] = (df['target_acwr_dist_15d'] > 1.5).astype(float)
    
    # Since we shift backward to predict the future, the last `horizon_days` of each player
    # will have NaN targets. We must drop or separate them for actual future inference.
    print("[+] Target creation completed.")
    return df

def split_train_test_chronological(df, test_size=0.10):
    """
    Splits the data chronologically per player.
    For each player, the first (1 - test_size) portion of days goes to Train,
    and the final test_size portion of days goes to Test.
    This respects temporal order and avoids data leakage.
    """
    print(f"[*] Splitting train/test chronologically (Test size: {test_size*100:.1f}%)...")
    
    train_frames = []
    test_frames = []
    
    for player_id, group in df.groupby('player_id'):
        group_sorted = group.sort_values(by='date')
        n_rows = len(group_sorted)
        
        split_idx = int(n_rows * (1 - test_size))
        
        train_part = group_sorted.iloc[:split_idx]
        test_part = group_sorted.iloc[split_idx:]
        
        train_frames.append(train_part)
        test_frames.append(test_part)
        
    train_df = pd.concat(train_frames, ignore_index=True)
    test_df = pd.concat(test_frames, ignore_index=True)
    
    print(f"[+] Split completed.")
    print(f"    - Train dataset shape: {train_df.shape} ({train_df['player_id'].nunique()} players)")
    print(f"    - Test dataset shape:  {test_df.shape} ({test_df['player_id'].nunique()} players)")
    
    return train_df, test_df

def save_dataframes(train_df, test_df, full_df, output_dir=None):
    """Saves the processed datasets as CSV files."""
    if output_dir is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        output_dir = os.path.join(project_root, 'data')
    print(f"[*] Saving processed datasets to folder: {output_dir}")
    os.makedirs(output_dir, exist_ok=True)
    
    train_path = os.path.join(output_dir, 'processed_train.csv')
    test_path = os.path.join(output_dir, 'processed_test.csv')
    full_path = os.path.join(output_dir, 'processed_full.csv')
    
    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)
    full_df.to_csv(full_path, index=False)
    
    print(f"[+] Train dataset saved to: {train_path}")
    print(f"[+] Test dataset saved to:  {test_path}")
    print(f"[+] Full processed dataset saved to: {full_path}")

def run_pipeline():
    """Executes the complete data engineering pipeline."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    raw_filepath = os.path.join(project_root, 'data', 'data_acute_vs_chronic.csv')
    
    try:
        # 1. Load raw data
        raw_df = load_data(raw_filepath)
        
        # 2. Preprocess
        preprocessed_df = preprocess_data(raw_df)
        
        # 3. Aggregate daily per athlete
        daily_df = aggregate_daily_per_player(preprocessed_df)
        
        # 4. Make timeline continuous (crucial for time windows)
        continuous_df = make_timeline_continuous(daily_df)
        
        # 5. Compute ACWR features
        features_df = compute_acwr_features(continuous_df)
        
        # 6. Create future targets (15-day horizon for predictive model)
        features_with_targets = create_predictive_target(features_df, horizon_days=15)
        
        # 7. Split train and test chronologically (10% test)
        train_df, test_df = split_train_test_chronological(features_with_targets, test_size=0.10)
        
        # 8. Save output datasets
        save_dataframes(train_df, test_df, features_with_targets)
        
        print("\n[🎉] SUCCESS: Data engineering pipeline executed successfully!")
        
    except Exception as e:
        print(f"\n[❌] ERROR running pipeline: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    run_pipeline()
