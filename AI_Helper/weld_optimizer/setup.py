#!/usr/bin/env python3
"""
Setup script for the Weld Parameter Optimizer
Run this script to initialize the database and set up the system.
"""

import os
import sys
import subprocess


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is adequate."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Python 3.7 or higher is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True


def install_requirements():
    """Install required Python packages."""
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found")
        return False

    return run_command(f"{sys.executable} -m pip install -r requirements.txt", "Installing Python dependencies")


def initialize_database():
    """Initialize the database."""
    db_init_path = os.path.join("database", "init_db.py")
    if not os.path.exists(db_init_path):
        print("❌ Database initialization script not found")
        return False

    return run_command(f"{sys.executable} {db_init_path}", "Initializing database structure")


def populate_initial_data():
    """Populate the database with initial data."""
    populate_path = os.path.join("database", "populate_data.py")
    if not os.path.exists(populate_path):
        print("❌ Data population script not found")
        return False

    return run_command(f"{sys.executable} {populate_path}", "Populating database with initial data")


def generate_sample_data():
    """Generate sample training data."""
    generator_path = os.path.join("utils", "data_generator.py")
    if not os.path.exists(generator_path):
        print("❌ Data generator script not found")
        return False

    return run_command(f"{sys.executable} {generator_path}", "Generating sample training data")


def train_initial_models():
    """Train the initial ML models."""
    model_path = os.path.join("models", "ml_predictor.py")
    if not os.path.exists(model_path):
        print("❌ ML predictor script not found")
        return False

    return run_command(f"{sys.executable} {model_path}", "Training initial machine learning models")


def main():
    """Main setup function."""
    print("🔥 Weld Parameter Optimizer Setup")
    print("=" * 50)

    # Change to the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"Working directory: {script_dir}")

    # Check Python version
    if not check_python_version():
        return False

    # Install requirements
    if not install_requirements():
        print("⚠️  Failed to install requirements. You may need to install them manually.")
        print("Run: pip install -r requirements.txt")

    # Initialize database
    if not initialize_database():
        print("❌ Database initialization failed")
        return False

    # Populate initial data
    if not populate_initial_data():
        print("❌ Failed to populate initial data")
        return False

    # Generate sample data
    if not generate_sample_data():
        print("⚠️  Failed to generate sample data. You can still use the system.")

    # Train models
    if not train_initial_models():
        print("⚠️  Failed to train initial models. The system will use rule-based predictions.")

    print("\n🎉 Setup completed!")
    print("\nNext steps:")
    print("1. Navigate to the web_app directory: cd web_app")
    print("2. Start the web application: python app.py")
    print("3. Open your browser to: http://localhost:5000")
    print("\nEnjoy optimizing your welding parameters! 🔧")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
