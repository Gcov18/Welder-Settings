from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from database.db_manager import DatabaseManager
    from models.ml_predictor import WeldParameterPredictor
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure the database and models modules are available")

app = Flask(__name__)
app.secret_key = "your-secret-key-here"  # Change this in production

# Initialize components
db_manager = DatabaseManager()
predictor = WeldParameterPredictor()

# Try to load pre-trained models
predictor.load_models()


@app.route("/")
def index():
    """Main page for parameter prediction."""
    try:
        # Get dropdown options from database
        base_materials = db_manager.get_materials("base").to_dict("records")
        filler_materials = db_manager.get_materials("filler").to_dict("records")
        joint_types = db_manager.get_joint_types().to_dict("records")
        positions = db_manager.get_welding_positions().to_dict("records")
        processes = db_manager.get_welding_processes().to_dict("records")
        shielding_gases = db_manager.get_shielding_gases().to_dict("records")

        return render_template(
            "index.html",
            base_materials=base_materials,
            filler_materials=filler_materials,
            joint_types=joint_types,
            positions=positions,
            processes=processes,
            shielding_gases=shielding_gases,
        )
    except Exception as e:
        flash(f"Error loading data: {str(e)}", "error")
        return render_template(
            "index.html",
            base_materials=[],
            filler_materials=[],
            joint_types=[],
            positions=[],
            processes=[],
            shielding_gases=[],
        )


@app.route("/predict", methods=["POST"])
def predict():
    """Generate parameter predictions."""
    try:
        # Get form data
        form_data = request.get_json() if request.is_json else request.form.to_dict()

        # Prepare input for prediction
        input_data = {
            "thickness": float(form_data.get("thickness", 0)),
            "base_carbon": float(form_data.get("base_carbon", 0)),
            "base_thermal": float(form_data.get("base_thermal", 0)),
            "base_melting_point": float(form_data.get("base_melting_point", 0)),
            "base_density": float(form_data.get("base_density", 0)),
            "filler_carbon": float(form_data.get("filler_carbon", 0)),
            "filler_thermal": float(form_data.get("filler_thermal", 0)),
            "process": form_data.get("process", ""),
            "position": form_data.get("position", ""),
            "joint_type": form_data.get("joint_type", ""),
        }

        if not predictor.models:
            # Fallback to rule-based predictions if no models are trained
            predictions = generate_rule_based_predictions(input_data)
            confidence = {k: 0.6 for k in predictions.keys()}
        else:
            # Use ML predictions
            predictions, confidence = predictor.predict_parameters(input_data)

        # Format predictions
        formatted_predictions = {
            "voltage": f"{predictions.get('voltage', 20):.1f} V",
            "amperage": f"{predictions.get('amperage', 150):.0f} A",
            "wire_feed_speed": f"{predictions.get('wire_feed_speed', 300):.0f} IPM",
            "travel_speed": f"{predictions.get('travel_speed', 8):.1f} IPM",
            "confidence": confidence,
        }

        if request.is_json:
            return jsonify({"success": True, "predictions": formatted_predictions})
        else:
            flash("Predictions generated successfully!", "success")
            return render_template("results.html", predictions=formatted_predictions)

    except Exception as e:
        error_msg = f"Error generating predictions: {str(e)}"
        if request.is_json:
            return jsonify({"success": False, "error": error_msg})
        else:
            flash(error_msg, "error")
            return redirect(url_for("index"))


def generate_rule_based_predictions(input_data):
    """Generate rule-based predictions when ML models aren't available."""
    thickness = input_data.get("thickness", 3.0)
    process = input_data.get("process", "GMAW")

    # Basic rule-based predictions
    if process == "GMAW":  # MIG
        voltage = 18 + (thickness * 2)
        amperage = 100 + (thickness * 30)
        wire_feed_speed = 200 + (thickness * 50)
        travel_speed = 10 - (thickness * 0.5)
    elif process == "GTAW":  # TIG
        voltage = 12 + (thickness * 1.5)
        amperage = 80 + (thickness * 25)
        wire_feed_speed = 0  # Manual feed
        travel_speed = 8 - (thickness * 0.3)
    else:  # Default
        voltage = 20 + (thickness * 1.8)
        amperage = 120 + (thickness * 28)
        wire_feed_speed = 250 + (thickness * 40)
        travel_speed = 9 - (thickness * 0.4)

    return {
        "voltage": max(voltage, 10),
        "amperage": max(amperage, 50),
        "wire_feed_speed": max(wire_feed_speed, 100),
        "travel_speed": max(travel_speed, 3),
    }


@app.route("/feedback", methods=["GET", "POST"])
def feedback():
    """Handle user feedback on predictions."""
    if request.method == "POST":
        try:
            feedback_data = (
                None,  # parameter_id - would need to track this
                float(request.form.get("user_voltage", 0)),
                float(request.form.get("user_amperage", 0)),
                float(request.form.get("user_wire_feed_speed", 0)),
                float(request.form.get("user_travel_speed", 0)),
                int(request.form.get("result_quality", 5)),
                request.form.get("weld_success") == "on",
                request.form.get("defects", ""),
                request.form.get("comments", ""),
            )

            db_manager.add_user_feedback(feedback_data)
            flash("Thank you for your feedback!", "success")

        except Exception as e:
            flash(f"Error saving feedback: {str(e)}", "error")

    return render_template("feedback.html")


@app.route("/database")
def database_view():
    """View database contents."""
    try:
        parameters = db_manager.get_weld_parameters()
        return render_template("database.html", parameters=parameters.to_dict("records"))
    except Exception as e:
        flash(f"Error loading database: {str(e)}", "error")
        return render_template("database.html", parameters=[])


@app.route("/api/materials/<material_type>")
def api_materials(material_type):
    """API endpoint for getting materials."""
    try:
        materials = db_manager.get_materials(material_type)
        return jsonify(materials.to_dict("records"))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/train_models")
def train_models():
    """Trigger model training."""
    try:
        predictor.train_models()
        flash("Models trained successfully!", "success")
    except Exception as e:
        flash(f"Error training models: {str(e)}", "error")

    return redirect(url_for("index"))


if __name__ == "__main__":
    # Ensure database exists
    try:
        # Test database connection
        db_manager.get_materials()
        print("Database connection successful")
    except Exception as e:
        print(f"Database connection failed: {e}")
        print("Please run database/init_db.py and database/populate_data.py first")

    app.run(debug=True, host="0.0.0.0", port=5000)
