import sqlite3
import os


def populate_initial_data():
    """Populate the database with initial welding data."""

    db_path = os.path.join(os.path.dirname(__file__), "weld_parameters.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Insert base materials
    base_materials = [
        ("Mild Steel", "base", 0.25, "Carbon Steel", 400, 250, 50, 1538, 7.85),
        ("Stainless Steel 304", "base", 0.08, "Austenitic SS", 515, 205, 16, 1454, 8.00),
        ("Stainless Steel 316", "base", 0.08, "Austenitic SS", 515, 205, 16, 1375, 8.00),
        ("Aluminum 6061", "base", 0.0, "Aluminum", 310, 276, 167, 660, 2.70),
        ("Aluminum 5052", "base", 0.0, "Aluminum", 228, 90, 138, 650, 2.68),
        ("Cast Iron", "base", 3.5, "Cast Iron", 200, 120, 50, 1150, 7.20),
    ]

    cursor.executemany(
        """
    INSERT INTO materials (name, type, carbon_content, alloy_type, tensile_strength,
                          yield_strength, thermal_conductivity, melting_point, density)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        base_materials,
    )

    # Insert filler materials
    filler_materials = [
        ("ER70S-6", "filler", 0.07, "Carbon Steel", 500, 420, 50, 1520, 7.85),
        ("ER308L", "filler", 0.03, "Stainless Steel", 550, 400, 16, 1400, 8.00),
        ("ER316L", "filler", 0.03, "Stainless Steel", 550, 400, 16, 1375, 8.00),
        ("ER4043", "filler", 0.0, "Aluminum", 145, 69, 155, 580, 2.69),
        ("ER5356", "filler", 0.0, "Aluminum", 310, 160, 117, 630, 2.64),
        ("E6010", "filler", 0.15, "Carbon Steel", 430, 330, 50, 1520, 7.85),
        ("E7018", "filler", 0.05, "Carbon Steel", 500, 400, 50, 1520, 7.85),
    ]

    cursor.executemany(
        """
    INSERT INTO materials (name, type, carbon_content, alloy_type, tensile_strength,
                          yield_strength, thermal_conductivity, melting_point, density)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        filler_materials,
    )

    # Insert joint types
    joint_types = [
        ("Butt Joint", "Square edge or beveled plates joined end to end", "Square or V-groove"),
        ("Fillet Joint", "L-shaped joint between two pieces", "No preparation needed"),
        ("Lap Joint", "Overlapping plates", "Clean surfaces"),
        ("Corner Joint", "Two pieces at right angles", "Square or beveled edges"),
        ("Edge Joint", "Plates joined at their edges", "Square edges"),
        ("T-Joint", "One piece perpendicular to another", "Clean surfaces"),
    ]

    cursor.executemany(
        """
    INSERT INTO joint_types (name, description, typical_preparation)
    VALUES (?, ?, ?)
    """,
        joint_types,
    )

    # Insert welding positions
    positions = [
        ("1G", "Flat Position", "Pipe horizontal, rotated during welding"),
        ("2G", "Horizontal Position", "Pipe vertical, welding horizontal"),
        ("3G", "Vertical Position", "Pipe horizontal, welding vertical"),
        ("4G", "Overhead Position", "Pipe horizontal overhead"),
        ("5G", "Horizontal Fixed", "Pipe horizontal, cannot be rotated"),
        ("6G", "Inclined Fixed", "Pipe at 45° angle, cannot be rotated"),
        ("1F", "Flat Fillet", "Flat fillet welding position"),
        ("2F", "Horizontal Fillet", "Horizontal fillet welding position"),
        ("3F", "Vertical Fillet", "Vertical fillet welding position"),
        ("4F", "Overhead Fillet", "Overhead fillet welding position"),
    ]

    cursor.executemany(
        """
    INSERT INTO welding_positions (code, name, description)
    VALUES (?, ?, ?)
    """,
        positions,
    )

    # Insert welding processes
    processes = [
        ("GMAW", "Gas Metal Arc Welding (MIG)", "Continuous wire feed with shielding gas"),
        ("GTAW", "Gas Tungsten Arc Welding (TIG)", "Tungsten electrode with shielding gas"),
        ("SMAW", "Shielded Metal Arc Welding (Stick)", "Consumable coated electrode"),
        ("FCAW", "Flux Cored Arc Welding", "Tubular wire with flux core"),
        ("SAW", "Submerged Arc Welding", "Wire electrode under granular flux"),
    ]

    cursor.executemany(
        """
    INSERT INTO welding_processes (code, name, description)
    VALUES (?, ?, ?)
    """,
        processes,
    )

    # Insert shielding gases
    gases = [
        ("100% CO2", "100% Carbon Dioxide", "Carbon Steel", "15-25 CFH"),
        ("75/25 Ar/CO2", "75% Argon, 25% CO2", "Carbon Steel, Low Alloy", "20-30 CFH"),
        ("90/10 Ar/CO2", "90% Argon, 10% CO2", "Stainless Steel", "20-30 CFH"),
        ("100% Argon", "100% Argon", "Aluminum, Stainless Steel", "15-25 CFH"),
        ("98/2 Ar/O2", "98% Argon, 2% Oxygen", "Stainless Steel", "20-30 CFH"),
        ("Tri-Mix", "Helium/Argon/CO2", "Thick Stainless Steel", "25-35 CFH"),
    ]

    cursor.executemany(
        """
    INSERT INTO shielding_gases (name, composition, suitable_materials, flow_rate_range)
    VALUES (?, ?, ?, ?)
    """,
        gases,
    )

    conn.commit()
    conn.close()

    print("Initial data populated successfully!")


if __name__ == "__main__":
    populate_initial_data()
