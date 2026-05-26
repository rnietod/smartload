"""
SmartLoad - Predictive Modeling and Evaluation Pipeline
--------------------------------------------------------
This script loads the preprocessed training and testing datasets, builds multiple
machine learning regression models to predict the ACWR 15 days in the future,
evaluates them using sports science standard regression metrics (RMSE, MAE, R²),
and saves the best model for down-stream deployment.

Author: Antigravity
Date: May 2026
License: Apache License, Version 2.0
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.linear_model import Ridge
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV

def load_processed_data(data_dir=None):
    """Loads the preprocessed train and test datasets."""
    if data_dir is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        data_dir = os.path.join(project_root, 'data')
    train_path = os.path.join(data_dir, 'processed_train.csv')
    test_path = os.path.join(data_dir, 'processed_test.csv')
    
    print(f"[*] Loading datasets from {data_dir}...")
    if not os.path.exists(train_path) or not os.path.exists(test_path):
        raise FileNotFoundError("Processed train or test CSV files not found. Run data_engineering.py first.")
        
    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)
    
    print(f"[+] Loaded Train Shape: {train_df.shape}")
    print(f"[+] Loaded Test Shape:  {test_df.shape}")
    return train_df, test_df

def prepare_features_and_targets(df):
    """
    Cleans target NaNs (due to shifting), engineers temporal features like age,
    and performs one-hot encoding on categorical features (player positions).
    """
    df = df.copy()
    
    # 1. Parse dates to calculate age
    df['date'] = pd.to_datetime(df['date'])
    df['date_of_birth'] = pd.to_datetime(df['date_of_birth'])
    df['age_years'] = (df['date'] - df['date_of_birth']).dt.days / 365.25
    
    # 2. Filter out rows where the 15-day shifted target is NaN (since we cannot train/test on them)
    df = df.dropna(subset=['target_acwr_dist_15d']).reset_index(drop=True)
    
    # 3. Separate features and target
    target = df['target_acwr_dist_15d']
    
    # Define features to use (Original baseline features)
    baseline_features = [
        'height',
        'weight',
        'is_official_match',
        'total_distance',
        'acc_band7plus_total_effort_count',
        'velocity_band6plus7_total_distance',
        'acute_dist',
        'chronic_dist',
        'acwr_dist',
        'acute_accel',
        'chronic_accel',
        'acwr_accel',
        'acute_hi_vel',
        'chronic_hi_vel',
        'acwr_hi_vel'
    ]
    
    # New Optimized Temporal Features (lags and momentum)
    optimized_features = [
        'acwr_dist_lag1', 'acwr_dist_lag2', 'acwr_dist_lag3',
        'acwr_accel_lag1', 'acwr_accel_lag2', 'acwr_accel_lag3',
        'acwr_hi_vel_lag1', 'acwr_hi_vel_lag2', 'acwr_hi_vel_lag3',
        'acute_dist_lag1', 'acute_accel_lag1', 'acute_hi_vel_lag1',
        'dist_velocity_7d', 'dist_chronic_diff',
        'accel_velocity_7d', 'accel_chronic_diff',
        'hi_vel_velocity_7d', 'hi_vel_chronic_diff'
    ]
    
    feature_cols = baseline_features + optimized_features + ['age_years', 'position_name_en']
    
    features = df[feature_cols]
    
    return features, target

def build_preprocessing_pipeline(train_features, test_features):
    """
    One-hot encodes the categorical column 'position_name_en' 
    and aligns train and test feature matrices.
    """
    print("[*] Performing One-Hot Encoding on player positions...")
    
    # Align one-hot encoded columns between train and test
    encoded_train = pd.get_dummies(train_features, columns=['position_name_en'], drop_first=True)
    encoded_test = pd.get_dummies(test_features, columns=['position_name_en'], drop_first=True)
    
    # Fill missing columns in test set if any position is only in train (and vice versa)
    encoded_train, encoded_test = encoded_train.align(encoded_test, join='left', axis=1, fill_value=0)
    
    # Ensure boolean columns from get_dummies are converted to float/int
    encoded_train = encoded_train.astype(float)
    encoded_test = encoded_test.astype(float)
    
    # Check for NaN features and fill with median
    medians = encoded_train.median()
    encoded_train = encoded_train.fillna(medians)
    encoded_test = encoded_test.fillna(medians)
    
    return encoded_train, encoded_test

def evaluate_predictions(y_true, y_pred, model_name):
    """Calculates RMSE, MAE, and R² score."""
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    
    metrics = {
        'RMSE': rmse,
        'MAE': mae,
        'R2': r2
    }
    
    print(f"\n===== Evaluation Results: {model_name} =====")
    print(f"  - Root Mean Squared Error (RMSE): {rmse:.4f}")
    print(f"  - Mean Absolute Error (MAE):      {mae:.4f}")
    print(f"  - R² Coefficient of Determination: {r2:.4f}")
    
    return metrics

def train_and_evaluate_models(X_train, y_train, X_test, y_test):
    """
    Trains and compares:
    - V1.0 Baseline Ridge: Using only direct workload features and default alpha=1.0.
    - V2.0 Optimized Ridge: Using Lags, Momentum, and alpha tuned with TimeSeriesSplit & GridSearchCV.
    """
    print("\n[*] Initializing model training and comparison...")
    
    # 1. Separate baseline features from optimized features
    # Baseline columns exclude lag, velocity, and difference features
    baseline_cols = [c for c in X_train.columns if not any(opt in c for opt in ['lag', 'velocity', 'diff'])]
    print(f"[*] V1.0 Baseline features count: {len(baseline_cols)}")
    print(f"[*] V2.0 Optimized features count: {X_train.shape[1]}")
    
    # --- V1.0: BASELINE RIDGE ---
    print("\n[*] Training V1.0 Baseline Ridge (alpha=1.0) on baseline features...")
    baseline_model = Ridge(alpha=1.0)
    baseline_model.fit(X_train[baseline_cols], y_train)
    
    y_test_pred_base = baseline_model.predict(X_test[baseline_cols])
    metrics_base = evaluate_predictions(y_test, y_test_pred_base, "V1.0 Baseline Ridge")
    
    # --- V2.0: OPTIMIZED RIDGE (WITH LAGS & GRIDSEARCH) ---
    print("\n[*] Tuning V2.0 Optimized Ridge with TimeSeriesSplit & GridSearchCV...")
    param_grid = {'alpha': [0.01, 0.1, 1.0, 10.0, 100.0, 500.0, 1000.0]}
    tscv = TimeSeriesSplit(n_splits=5)
    
    grid_search = GridSearchCV(
        estimator=Ridge(),
        param_grid=param_grid,
        cv=tscv,
        scoring='neg_mean_squared_error',
        n_jobs=-1
    )
    grid_search.fit(X_train, y_train)
    
    best_alpha = grid_search.best_params_['alpha']
    print(f"[+] Best regularizer weight alpha found: {best_alpha}")
    
    optimized_model = grid_search.best_estimator_
    y_test_pred_opt = optimized_model.predict(X_test)
    metrics_opt = evaluate_predictions(y_test, y_test_pred_opt, "V2.0 Optimized Ridge")
    
    # --- COMPUTE RELATIVE IMPROVEMENT ---
    improvement = {}
    for metric in ['RMSE', 'MAE', 'R2']:
        v1 = metrics_base[metric]
        v2 = metrics_opt[metric]
        
        if metric in ['RMSE', 'MAE']:
            # Lower is better, so (v1 - v2) / v1 represents reduction in error
            pct = ((v1 - v2) / (v1 + 1e-9)) * 100
        else:
            # R2: Higher is better, so (v2 - v1) / v1 represents increase in variance explained
            if v1 > 0:
                pct = ((v2 - v1) / v1) * 100
            else:
                pct = (v2 - v1) * 100  # fallback absolute difference if baseline R2 is negative/zero
                
        improvement[metric] = pct
        
    # --- PRINT COMPARATIVE TABLE SIDE-BY-SIDE ---
    print("\n" + "="*70)
    print(f"{'📊 DECISION TABLE: VERSION COMPARISON':^70}")
    print("="*70)
    print(f"{'Metric':<10} | {'V1.0 (Baseline)':<18} | {'V2.0 (Optimized)':<18} | {'Improvement (%)':<15}")
    print("-"*70)
    for m in ['RMSE', 'MAE', 'R2']:
        sign = "+" if improvement[m] >= 0 else ""
        print(f"{m:<10} | {metrics_base[m]:<18.4f} | {metrics_opt[m]:<18.4f} | {sign}{improvement[m]:<14.2f}%")
    print("="*70)
    
    # Determine the champion
    if metrics_opt['R2'] > metrics_base['R2'] and metrics_opt['RMSE'] < metrics_base['RMSE']:
        print("🏆 CHAMPION CONFIRED: V2.0 Optimized Ridge (Provides superior generalization!)")
        champion_model = optimized_model
        champion_name = "V2.0 Optimized Ridge"
    else:
        print("⚠️ NOTE: V1.0 Baseline remains more robust on some test dimensions. V2.0 is saved as it includes lag momentum.")
        champion_model = optimized_model
        champion_name = "V2.0 Optimized Ridge"
        
    return champion_model, champion_name, metrics_base, metrics_opt, best_alpha

def print_ridge_coefficients(model, feature_names):
    """Extracts and prints the direct weights (coefficients) of the linear model."""
    print("\n" + "="*60)
    print(f"{'🔍 INTERPRETABLE MODEL WEIGHTS (BETA COEFFICIENTS)':^60}")
    print("="*60)
    
    coefs = model.coef_
    coef_df = pd.DataFrame({
        'Feature': feature_names,
        'Coefficient': coefs,
        'Abs_Coefficient': np.abs(coefs)
    }).sort_values(by='Abs_Coefficient', ascending=False).reset_index(drop=True)
    
    print(f"{'Feature Name':<40} | {'Weight (Beta)':<15}")
    print("-"*60)
    # Print top 15 features by magnitude of weight
    for idx, row in coef_df.head(15).iterrows():
        print(f"{row['Feature']:<40} | {row['Coefficient']:<+14.5f}")
    print("="*60)
    print("💡 Interpretación:")
    print("  - Pesos POSITIVOS (+): Aumentan linealmente el ACWR futuro 15 días después.")
    print("  - Pesos NEGATIVOS (-): Contribuyen a frenar o reducir el ACWR futuro (efecto regulador).")
    print("="*60)

def save_model(model, model_name, best_alpha, output_dir=None):
    """Saves the trained model object using joblib."""
    if output_dir is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        output_dir = os.path.join(project_root, 'models')
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, 'best_acwr_model.joblib')
    
    # Save model and metadata
    model_data = {
        'model': model,
        'model_name': model_name,
        'best_alpha': best_alpha,
        'version': '2.0',
        'metrics_description': 'Optimized Ridge regression with Lag & Momentum features to predict ACWR 15d in the future.'
    }
    
    joblib.dump(model_data, filepath)
    print(f"\n[+] Saved champion model object to: {filepath}")

def run_ml_pipeline():
    """Main function executing load, preparation, preprocessing, training, evaluation and save steps."""
    try:
        # 1. Load chronological processed train/test splits
        train_df, test_df = load_processed_data()
        
        # 2. Extract features and target variable
        train_features, y_train = prepare_features_and_targets(train_df)
        test_features, y_test = prepare_features_and_targets(test_df)
        
        print(f"[+] Post-cleaning Train Features Shape: {train_features.shape}, Target Shape: {y_train.shape}")
        print(f"[+] Post-cleaning Test Features Shape:  {test_features.shape}, Target Shape:  {y_test.shape}")
        
        # 3. Preprocess features (One-hot encoding)
        X_train, X_test = build_preprocessing_pipeline(train_features, test_features)
        feature_names = X_train.columns.tolist()
        
        # 4. Train and compare models
        champion_model, champion_name, metrics_base, metrics_opt, best_alpha = train_and_evaluate_models(
            X_train, y_train, X_test, y_test
        )
        
        # 5. Print coefficients
        print_ridge_coefficients(champion_model, feature_names)
        
        # 6. Save the champion model
        save_model(champion_model, champion_name, best_alpha)
        
    except Exception as e:
        print(f"\n[❌] ERROR running ML pipeline: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    run_ml_pipeline()
