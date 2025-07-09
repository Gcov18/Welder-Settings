import pandas as pd
import numpy as np
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from database.db_manager import DatabaseManager
except ImportError:
    print("Warning: Could not import DatabaseManager")


def generate_sample_weld_data(num_samples=200):
    """Generate sample welding data for training the ML models."""

    # Define parameter ranges based on common welding practices
    processes = ["GMAW", "GTAW", "SMAW", "FCAW"]
    positions = ["1G", "2G", "3G", "4G", "1F", "2F", "3F", "4F"]
    joint_types = ["Butt Joint", "Fillet Joint", "Lap Joint", "Corner Joint"]

    # Material properties (simplified)
    materials = {
        "Mild Steel": {"carbon": 0.25, "thermal": 50, "melting": 1538, "density": 7.85},
        "Stainless Steel 304": {"carbon": 0.08, "thermal": 16, "melting": 1454, "density": 8.00},
        "Aluminum 6061": {"carbon": 0.0, "thermal": 167, "melting": 660, "density": 2.70},
    }

    filler_materials = {
        "ER70S-6": {"carbon": 0.07, "thermal": 50},
        "ER308L": {"carbon": 0.03, "thermal": 16},
        "ER4043": {"carbon": 0.0, "thermal": 155},
    }

    data = []

    for i in range(num_samples):
        # Random selections
        process = np.random.choice(processes)
        position = np.random.choice(positions)
        joint_type = np.random.choice(joint_types)

        base_material = np.random.choice(list(materials.keys()))
        filler_material = np.random.choice(list(filler_materials.keys()))

        # Random thickness (weighted towards common sizes)
        thickness = np.random.choice([1.5, 3.0, 6.0, 10.0, 12.0, 15.0, 20.0], p=[0.1, 0.3, 0.25, 0.15, 0.1, 0.05, 0.05])

        # Generate parameters based on process and thickness
        if process == "GMAW":  # MIG
            voltage = 18 + (thickness * 2) + np.random.normal(0, 2)
            amperage = 100 + (thickness * 30) + np.random.normal(0, 20)
            wire_feed_speed = 200 + (thickness * 50) + np.random.normal(0, 50)
            travel_speed = max(3, 10 - (thickness * 0.5) + np.random.normal(0, 2))

        elif process == "GTAW":  # TIG
            voltage = 12 + (thickness * 1.5) + np.random.normal(0, 1.5)
            amperage = 80 + (thickness * 25) + np.random.normal(0, 15)
            wire_feed_speed = 0  # Manual feed
            travel_speed = max(2, 8 - (thickness * 0.3) + np.random.normal(0, 1.5))

        elif process == "SMAW":  # Stick
            voltage = 20 + (thickness * 1.2) + np.random.normal(0, 2)
            amperage = 90 + (thickness * 35) + np.random.normal(0, 25)
            wire_feed_speed = 0  # Not applicable
            travel_speed = max(2, 6 - (thickness * 0.2) + np.random.normal(0, 1))

        else:  # FCAW
            voltage = 22 + (thickness * 2.2) + np.random.normal(0, 2.5)
            amperage = 120 + (thickness * 35) + np.random.normal(0, 30)
            wire_feed_speed = 150 + (thickness * 60) + np.random.normal(0, 40)
            travel_speed = max(3, 12 - (thickness * 0.6) + np.random.normal(0, 2))

        # Position adjustments
        if "3" in position or "4" in position:  # Vertical or overhead
            amperage *= 0.9  # Reduce for out-of-position
            travel_speed *= 0.8

        # Material adjustments
        if "Aluminum" in base_material:
            voltage *= 0.85
            amperage *= 1.1
            travel_speed *= 1.2
        elif "Stainless" in base_material:
            voltage *= 0.95
            travel_speed *= 0.9

        # Quality rating based on parameter optimization
        quality_score = np.random.normal(7, 1.5)

        # Adjust quality based on parameter reasonableness
        if voltage < 10 or voltage > 40:
            quality_score -= 2
        if amperage < 50 or amperage > 400:
            quality_score -= 2
        if travel_speed < 2 or travel_speed > 20:
            quality_score -= 1

        quality_score = max(1, min(10, quality_score))

        # Success rate
        success_rate = min(100, max(0, (quality_score - 3) * 20 + np.random.normal(0, 10)))

        record = {
            "thickness": round(thickness, 1),
            "base_carbon": materials[base_material]["carbon"],
            "base_thermal": materials[base_material]["thermal"],
            "base_melting_point": materials[base_material]["melting"],
            "base_density": materials[base_material]["density"],
            "filler_carbon": filler_materials[filler_material]["carbon"],
            "filler_thermal": filler_materials[filler_material]["thermal"],
            "process": process,
            "position": position,
            "joint_type": joint_type,
            "voltage": round(max(8, voltage), 1),
            "amperage": round(max(30, amperage), 0),
            "wire_feed_speed": round(max(0, wire_feed_speed), 0),
            "travel_speed": round(max(1, travel_speed), 1),
            "quality_rating": round(quality_score, 1),
            "success_rate": round(success_rate, 1),
        }

        data.append(record)

    return pd.DataFrame(data)


def populate_database_with_sample_data():
    """Populate the database with generated sample data."""
    try:
        db_manager = DatabaseManager()

        # Generate sample data
        print("Generating sample welding data...")
        df = generate_sample_weld_data(200)

        print(f"Generated {len(df)} sample records")

        # Get material and other IDs from database
        base_materials = db_manager.get_materials("base")
        filler_materials = db_manager.get_materials("filler")
        joint_types = db_manager.get_joint_types()
        positions = db_manager.get_welding_positions()
        processes = db_manager.get_welding_processes()

        # Create mapping dictionaries
        base_material_map = dict(zip(base_materials["name"], base_materials["id"]))
        filler_material_map = dict(zip(filler_materials["name"], filler_materials["id"]))
        joint_type_map = dict(zip(joint_types["name"], joint_types["id"]))
        position_map = dict(zip(positions["code"], positions["id"]))
        process_map = dict(zip(processes["code"], processes["id"]))

        # Add records to database
        added_count = 0
        for _, row in df.iterrows():
            try:
                # Map names to IDs
                base_material_id = base_material_map.get("Mild Steel", 1)  # Default to first material
                filler_material_id = filler_material_map.get("ER70S-6", 7)  # Default
                joint_type_id = joint_type_map.get(row["joint_type"], 1)
                position_id = position_map.get(row["position"], 1)
                process_id = process_map.get(row["process"], 1)

                parameters = (
                    base_material_id,
                    filler_material_id,
                    row["thickness"],
                    joint_type_id,
                    position_id,
                    process_id,
                    1,  # shielding_gas_id
                    row["voltage"],
                    row["amperage"],
                    row["wire_feed_speed"],
                    row["travel_speed"],
                    2.4,  # electrode_diameter
                    25,  # gas_flow_rate
                    None,  # preheat_temp
                    None,  # interpass_temp
                    row["thickness"] * 0.8,  # penetration_depth
                    row["quality_rating"],
                    row["success_rate"],
                    "Generated sample data",
                    "system_generated",
                )

                db_manager.add_weld_parameter(parameters)
                added_count += 1

            except Exception as e:
                print(f"Error adding record: {e}")
                continue

        print(f"Successfully added {added_count} records to the database")

    except Exception as e:
        print(f"Error populating database: {e}")


def export_data_to_excel(filename="weld_parameters_export.xlsx"):
    """Export database data to Excel for analysis."""
    try:
        db_manager = DatabaseManager()

        # Get all data
        parameters = db_manager.get_weld_parameters()
        materials = db_manager.get_materials()
        joint_types = db_manager.get_joint_types()
        positions = db_manager.get_welding_positions()
        processes = db_manager.get_welding_processes()

        # Create Excel writer
        with pd.ExcelWriter(filename, engine="openpyxl") as writer:
            parameters.to_excel(writer, sheet_name="Weld Parameters", index=False)
            materials.to_excel(writer, sheet_name="Materials", index=False)
            joint_types.to_excel(writer, sheet_name="Joint Types", index=False)
            positions.to_excel(writer, sheet_name="Positions", index=False)
            processes.to_excel(writer, sheet_name="Processes", index=False)

        print(f"Data exported to {filename}")

    except Exception as e:
        print(f"Error exporting data: {e}")


if __name__ == "__main__":
    # Run sample data generation
    populate_database_with_sample_data()
