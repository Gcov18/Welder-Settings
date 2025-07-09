import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from database.db_manager import DatabaseManager
except ImportError:
    # Fallback for when running as script
    class DatabaseManager:
        def get_training_data(self):
            return pd.DataFrame()


class WeldParameterPredictor:
    """Machine learning model for predicting optimal weld parameters."""

    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.feature_columns = []
        self.db_manager = DatabaseManager()

    def prepare_features(self, df):
        """Prepare features for training."""
        # Create a copy to avoid modifying original data
        df_processed = df.copy()

        # Encode categorical variables
        categorical_columns = ["process", "position", "joint_type"]

        for col in categorical_columns:
            if col not in self.encoders:
                self.encoders[col] = LabelEncoder()
                df_processed[f"{col}_encoded"] = self.encoders[col].fit_transform(df_processed[col].fillna("Unknown"))
            else:
                df_processed[f"{col}_encoded"] = self.encoders[col].transform(df_processed[col].fillna("Unknown"))

        # Select features for model
        feature_columns = [
            "thickness",
            "base_carbon",
            "base_thermal",
            "base_melting_point",
            "base_density",
            "filler_carbon",
            "filler_thermal",
            "process_encoded",
            "position_encoded",
            "joint_type_encoded",
        ]

        # Remove rows with missing critical features
        df_processed = df_processed.dropna(subset=feature_columns)

        self.feature_columns = feature_columns
        return df_processed[feature_columns]

    def train_models(self):
        """Train the prediction models."""
        print("Loading training data...")
        df = self.db_manager.get_training_data()

        if df.empty:
            print("No training data available. Please populate the database first.")
            return

        print(f"Loaded {len(df)} training samples")

        # Prepare features
        X = self.prepare_features(df)

        # Define target variables to predict
        targets = ["voltage", "amperage", "wire_feed_speed", "travel_speed"]

        for target in targets:
            if target in df.columns:
                y = df[target].dropna()
                X_target = X.loc[y.index]

                if len(y) < 10:
                    print(f"Not enough data for {target} (need at least 10 samples, have {len(y)})")
                    continue

                print(f"\nTraining model for {target}...")

                # Split data
                X_train, X_test, y_train, y_test = train_test_split(X_target, y, test_size=0.2, random_state=42)

                # Scale features
                scaler = StandardScaler()
                X_train_scaled = scaler.fit_transform(X_train)
                X_test_scaled = scaler.transform(X_test)

                # Try different models
                models_to_try = {
                    "random_forest": RandomForestRegressor(n_estimators=100, random_state=42),
                    "gradient_boosting": GradientBoostingRegressor(n_estimators=100, random_state=42),
                }

                best_score = -np.inf
                best_model = None

                for model_name, model in models_to_try.items():
                    # Cross-validation
                    cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring="r2")
                    avg_score = np.mean(cv_scores)

                    print(f"  {model_name} CV R2: {avg_score:.3f} (+/- {np.std(cv_scores) * 2:.3f})")

                    if avg_score > best_score:
                        best_score = avg_score
                        best_model = model

                # Train best model on full training set
                best_model.fit(X_train_scaled, y_train)

                # Test performance
                y_pred = best_model.predict(X_test_scaled)
                test_r2 = r2_score(y_test, y_pred)
                test_rmse = np.sqrt(mean_squared_error(y_test, y_pred))

                print(f"  Best model test R2: {test_r2:.3f}")
                print(f"  Best model test RMSE: {test_rmse:.3f}")

                # Store model and scaler
                self.models[target] = best_model
                self.scalers[target] = scaler

        # Save models
        self.save_models()
        print("\nModels trained and saved successfully!")

    def predict_parameters(self, input_data):
        """Predict welding parameters for given input."""
        # Prepare input features
        input_df = pd.DataFrame([input_data])

        # Handle categorical encoding
        for col, encoder in self.encoders.items():
            if col in input_df.columns:
                try:
                    input_df[f"{col}_encoded"] = encoder.transform([input_df[col].iloc[0]])
                except ValueError:
                    # Handle unknown categories
                    input_df[f"{col}_encoded"] = 0

        # Select features
        X = input_df[self.feature_columns].fillna(0)

        predictions = {}
        confidence_scores = {}

        for target, model in self.models.items():
            if target in self.scalers:
                # Scale features
                X_scaled = self.scalers[target].transform(X)

                # Make prediction
                pred = model.predict(X_scaled)[0]
                predictions[target] = pred

                # Calculate confidence (simplified)
                if hasattr(model, "predict_proba"):
                    confidence_scores[target] = 0.8  # Placeholder
                else:
                    confidence_scores[target] = 0.7  # Placeholder

        return predictions, confidence_scores

    def save_models(self):
        """Save trained models to disk."""
        model_dir = os.path.dirname(__file__)

        # Save models
        for target, model in self.models.items():
            joblib.dump(model, os.path.join(model_dir, f"{target}_model.joblib"))

        # Save scalers
        for target, scaler in self.scalers.items():
            joblib.dump(scaler, os.path.join(model_dir, f"{target}_scaler.joblib"))

        # Save encoders
        for col, encoder in self.encoders.items():
            joblib.dump(encoder, os.path.join(model_dir, f"{col}_encoder.joblib"))

        # Save feature columns
        joblib.dump(self.feature_columns, os.path.join(model_dir, "feature_columns.joblib"))

    def load_models(self):
        """Load trained models from disk."""
        model_dir = os.path.dirname(__file__)

        try:
            # Load feature columns
            self.feature_columns = joblib.load(os.path.join(model_dir, "feature_columns.joblib"))

            # Load models
            targets = ["voltage", "amperage", "wire_feed_speed", "travel_speed"]
            for target in targets:
                model_path = os.path.join(model_dir, f"{target}_model.joblib")
                scaler_path = os.path.join(model_dir, f"{target}_scaler.joblib")

                if os.path.exists(model_path) and os.path.exists(scaler_path):
                    self.models[target] = joblib.load(model_path)
                    self.scalers[target] = joblib.load(scaler_path)

            # Load encoders
            categorical_columns = ["process", "position", "joint_type"]
            for col in categorical_columns:
                encoder_path = os.path.join(model_dir, f"{col}_encoder.joblib")
                if os.path.exists(encoder_path):
                    self.encoders[col] = joblib.load(encoder_path)

            print(f"Loaded {len(self.models)} models successfully!")
            return True

        except Exception as e:
            print(f"Error loading models: {e}")
            return False


if __name__ == "__main__":
    predictor = WeldParameterPredictor()
    predictor.train_models()
