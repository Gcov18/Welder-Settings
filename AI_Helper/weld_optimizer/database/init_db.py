import sqlite3
import os


def create_database():
    """Create the weld parameter database with all necessary tables."""

    db_path = os.path.join(os.path.dirname(__file__), "weld_parameters.db")

    # Remove existing database to start fresh
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Materials table
    cursor.execute(
        """
    CREATE TABLE materials (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        type TEXT NOT NULL,  -- 'base' or 'filler'
        carbon_content REAL,
        alloy_type TEXT,
        tensile_strength REAL,
        yield_strength REAL,
        thermal_conductivity REAL,
        melting_point REAL,
        density REAL
    )
    """
    )

    # Joint types table
    cursor.execute(
        """
    CREATE TABLE joint_types (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        typical_preparation TEXT
    )
    """
    )

    # Welding positions table
    cursor.execute(
        """
    CREATE TABLE welding_positions (
        id INTEGER PRIMARY KEY,
        code TEXT NOT NULL,  -- 1G, 2G, 3G, 4G, etc.
        name TEXT NOT NULL,
        description TEXT
    )
    """
    )

    # Welding processes table
    cursor.execute(
        """
    CREATE TABLE welding_processes (
        id INTEGER PRIMARY KEY,
        code TEXT NOT NULL,  -- GMAW, GTAW, SMAW, FCAW
        name TEXT NOT NULL,
        description TEXT,
        typical_applications TEXT
    )
    """
    )

    # Shielding gases table
    cursor.execute(
        """
    CREATE TABLE shielding_gases (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        composition TEXT,
        suitable_materials TEXT,
        flow_rate_range TEXT
    )
    """
    )

    # Main welding parameters table
    cursor.execute(
        """
    CREATE TABLE weld_parameters (
        id INTEGER PRIMARY KEY,
        base_material_id INTEGER,
        filler_material_id INTEGER,
        thickness REAL,
        joint_type_id INTEGER,
        position_id INTEGER,
        process_id INTEGER,
        shielding_gas_id INTEGER,
        voltage REAL,
        amperage REAL,
        wire_feed_speed REAL,
        travel_speed REAL,
        electrode_diameter REAL,
        gas_flow_rate REAL,
        preheat_temp REAL,
        interpass_temp REAL,
        penetration_depth REAL,
        quality_rating INTEGER,  -- 1-10 scale
        success_rate REAL,  -- percentage
        notes TEXT,
        source TEXT,  -- AWS, manufacturer, user, etc.
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (base_material_id) REFERENCES materials (id),
        FOREIGN KEY (filler_material_id) REFERENCES materials (id),
        FOREIGN KEY (joint_type_id) REFERENCES joint_types (id),
        FOREIGN KEY (position_id) REFERENCES welding_positions (id),
        FOREIGN KEY (process_id) REFERENCES welding_processes (id),
        FOREIGN KEY (shielding_gas_id) REFERENCES shielding_gases (id)
    )
    """
    )

    # User feedback table
    cursor.execute(
        """
    CREATE TABLE user_feedback (
        id INTEGER PRIMARY KEY,
        parameter_id INTEGER,
        user_voltage REAL,
        user_amperage REAL,
        user_wire_feed_speed REAL,
        user_travel_speed REAL,
        result_quality INTEGER,  -- 1-10 scale
        weld_success BOOLEAN,
        defects TEXT,
        comments TEXT,
        image_path TEXT,
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (parameter_id) REFERENCES weld_parameters (id)
    )
    """
    )

    # Environmental conditions table
    cursor.execute(
        """
    CREATE TABLE environmental_conditions (
        id INTEGER PRIMARY KEY,
        parameter_id INTEGER,
        temperature REAL,
        humidity REAL,
        wind_speed REAL,
        indoor_outdoor TEXT,
        ventilation_quality TEXT,
        FOREIGN KEY (parameter_id) REFERENCES weld_parameters (id)
    )
    """
    )

    conn.commit()
    conn.close()

    print(f"Database created successfully at: {db_path}")


if __name__ == "__main__":
    create_database()
