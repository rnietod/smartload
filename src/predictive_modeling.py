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
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor

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
    
    # Define features to use
    feature_cols = [
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
        'acwr_hi_vel',
        'age_years',
        'position_name_en'  # Will be one-hot encoded
    ]
    
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
    """Trains Ridge Regression, Random Forest, and Gradient Boosting models and compares them."""
    print("\n[*] Initializing model training...")
    
    models = {
        'Ridge Linear Regression': Ridge(alpha=1.0),
        'Random Forest Regressor': RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1),
        'Gradient Boosting Regressor': GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=4, random_state=42)
    }
    
    results = {}
    best_model_name = None
    best_r2 = -float('inf')
    best_model_obj = None
    
    for name, model in models.items():
        print(f"\n[*] Training {name}...")
        model.fit(X_train, y_train)
        
        # Predict on train and test
        y_train_pred = model.predict(X_train)
        y_test_pred = model.predict(X_test)
        
        # Evaluate on test set
        test_metrics = evaluate_predictions(y_test, y_test_pred, name)
        results[name] = {
            'model_object': model,
            'metrics': test_metrics,
            'predictions': y_test_pred
        }
        
        # Select best model based on R2 score on test set
        if test_metrics['R2'] > best_r2:
            best_r2 = test_metrics['R2']
            best_model_name = name
            best_model_obj = model
            
    print("\n" + "="*50)
    print(f"🏆 Best Performing Model: {best_model_name}")
    print(f"   Test R²: {best_r2:.4f}")
    print("="*50)
    
    return results, best_model_name, best_model_obj

def print_feature_importance(model, feature_names, model_name):
    """Extracts and prints feature importances for ensemble models."""
    if hasattr(model, 'feature_importances_'):
        print(f"\n[*] Top Feature Importances for {model_name}:")
        importances = model.feature_importances_
        indices = np.argsort(importances)[::-1]
        
        # Display top 10 features
        top_n = min(10, len(feature_names))
        for i in range(top_n):
            idx = indices[i]
            print(f"  {i+1}. {feature_names[idx]:<40}: {importances[idx]:.4f}")
    else:
        print(f"\n[*] Model {model_name} does not support feature importances.")

def save_model(model, model_name, output_dir=None):
    """Saves the trained model object using joblib."""
    if output_dir is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        output_dir = os.path.join(project_root, 'models')
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, 'best_acwr_model.joblib')
    
    # Save both model and model metadata
    model_data = {
        'model': model,
        'model_name': model_name,
        'version': '1.0',
        'metrics_description': 'Trained to predict ACWR total distance 15 days in the future.'
    }
    
    joblib.dump(model_data, filepath)
    print(f"\n[+] Saved best model object to: {filepath}")

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
        
        # 4. Train, evaluate and compare multiple models
        results, best_name, best_model = train_and_evaluate_models(X_train, y_train, X_test, y_test)
        
        # 5. Print best model feature importances
        print_feature_importance(best_model, feature_names, best_name)
        
        # 6. Save the champion model for the dashboard app
        save_model(best_model, best_name)
        
        # 7. Print summary evaluation comparison table
        print("\n" + "="*60)
        print(f"{'MODEL COMPARISON SUMMARY':^60}")
        print("="*60)
        print(f"{'Model Name':<30} | {'RMSE':<8} | {'MAE':<8} | {'R2':<8}")
        print("-"*60)
        for name, data in results.items():
            m = data['metrics']
            print(f"{name:<30} | {m['RMSE']:<8.4f} | {m['MAE']:<8.4f} | {m['R2']:<8.4f}")
        print("="*60)
        
    except Exception as e:
        print(f"\n[❌] ERROR running ML pipeline: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    run_ml_pipeline()
