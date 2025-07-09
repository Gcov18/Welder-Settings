"""
Configuration settings for the Weld Parameter Optimizer
"""

import os

# Database configuration
DATABASE_NAME = "weld_parameters.db"
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "database", DATABASE_NAME)

# Flask application settings
SECRET_KEY = "your-secret-key-change-in-production"
DEBUG = True
HOST = "0.0.0.0"
PORT = 5000

# Machine Learning settings
MIN_TRAINING_SAMPLES = 10
CV_FOLDS = 5
TEST_SIZE = 0.2
RANDOM_STATE = 42

# Model file paths
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
MODEL_FILES = {
    "voltage": "voltage_model.joblib",
    "amperage": "amperage_model.joblib",
    "wire_feed_speed": "wire_feed_speed_model.joblib",
    "travel_speed": "travel_speed_model.joblib",
}

SCALER_FILES = {
    "voltage": "voltage_scaler.joblib",
    "amperage": "amperage_scaler.joblib",
    "wire_feed_speed": "wire_feed_speed_scaler.joblib",
    "travel_speed": "travel_speed_scaler.joblib",
}

ENCODER_FILES = {
    "process": "process_encoder.joblib",
    "position": "position_encoder.joblib",
    "joint_type": "joint_type_encoder.joblib",
}

# Parameter limits and validation
PARAMETER_LIMITS = {
    "voltage": {"min": 8, "max": 50},
    "amperage": {"min": 30, "max": 500},
    "wire_feed_speed": {"min": 50, "max": 800},
    "travel_speed": {"min": 1, "max": 30},
    "thickness": {"min": 0.5, "max": 100},
}

# Quality thresholds
QUALITY_THRESHOLDS = {"excellent": 9, "good": 7, "acceptable": 5, "poor": 3}

# Default gas flow rates by process (CFH)
DEFAULT_GAS_FLOWS = {"GMAW": 25, "GTAW": 20, "FCAW": 30, "SMAW": 0}  # No shielding gas

# Common electrode diameters by process (mm)
ELECTRODE_DIAMETERS = {
    "GMAW": [0.8, 1.0, 1.2, 1.6],
    "GTAW": [1.6, 2.4, 3.2, 4.0],
    "SMAW": [2.5, 3.2, 4.0, 5.0],
    "FCAW": [1.2, 1.6, 2.0, 2.4],
}

# Material compatibility matrix
MATERIAL_COMPATIBILITY = {
    "Mild Steel": ["ER70S-6", "E6010", "E7018"],
    "Stainless Steel 304": ["ER308L", "E308L-16"],
    "Stainless Steel 316": ["ER316L", "E316L-16"],
    "Aluminum 6061": ["ER4043", "ER5356"],
    "Aluminum 5052": ["ER5356", "ER5183"],
}

# Welding position difficulty multipliers
POSITION_DIFFICULTY = {
    "1G": 1.0,  # Flat - easiest
    "1F": 1.0,
    "2G": 1.1,  # Horizontal
    "2F": 1.1,
    "3G": 1.3,  # Vertical - more difficult
    "3F": 1.3,
    "4G": 1.5,  # Overhead - most difficult
    "4F": 1.5,
    "5G": 1.4,  # Fixed horizontal
    "6G": 1.6,  # Fixed inclined - very difficult
}
