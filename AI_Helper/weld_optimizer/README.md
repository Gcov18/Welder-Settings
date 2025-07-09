# Weld Parameter Optimizer

A machine learning-powered tool to optimize welding parameters based on material properties, joint configurations, and environmental factors.

## Features

- **Multi-Process Support**: GMAW/MIG, GTAW/TIG, SMAW/Stick, FCAW
- **Material Database**: Comprehensive material combinations and properties
- **Joint Configuration**: Support for various joint types and positions
- **ML Predictions**: Trained models for parameter optimization
- **Web Interface**: User-friendly web application
- **Continuous Learning**: Feedback system for model improvement

## Project Structure

```
weld_optimizer/
├── database/           # Database models and schemas
├── models/            # Machine learning models
├── web_app/           # Flask web application
├── data/              # Training data and datasets
├── utils/             # Utility functions
└── requirements.txt   # Python dependencies
```

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Initialize the database:
```bash
python database/init_db.py
```

4. Run the application:
```bash
python web_app/app.py
```

## Usage

1. Navigate to `http://localhost:5000`
2. Input your welding parameters (material, thickness, joint type, etc.)
3. Get optimized welding parameter recommendations
4. Provide feedback on results to improve the model

## Data Sources

- AWS Welding Procedure Specifications
- Manufacturer welding guides (Lincoln, Miller, ESAB)
- Welding reference materials
- User feedback and results

## Contributing

1. Add new welding data to improve model accuracy
2. Test parameter recommendations with real welding scenarios
3. Provide feedback through the web interface
4. Report issues or suggest improvements
