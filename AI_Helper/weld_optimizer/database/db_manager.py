import sqlite3
import os
import pandas as pd


class DatabaseManager:
    """Manages database connections and operations for the weld optimizer."""

    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(__file__), "weld_parameters.db")

    def get_connection(self):
        """Get a database connection."""
        return sqlite3.connect(self.db_path)

    def get_materials(self, material_type=None):
        """Get materials from the database."""
        conn = self.get_connection()

        if material_type:
            query = "SELECT * FROM materials WHERE type = ?"
            df = pd.read_sql_query(query, conn, params=[material_type])
        else:
            query = "SELECT * FROM materials"
            df = pd.read_sql_query(query, conn)

        conn.close()
        return df

    def get_joint_types(self):
        """Get all joint types."""
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM joint_types", conn)
        conn.close()
        return df

    def get_welding_positions(self):
        """Get all welding positions."""
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM welding_positions", conn)
        conn.close()
        return df

    def get_welding_processes(self):
        """Get all welding processes."""
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM welding_processes", conn)
        conn.close()
        return df

    def get_shielding_gases(self):
        """Get all shielding gases."""
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM shielding_gases", conn)
        conn.close()
        return df

    def get_weld_parameters(self, filters=None):
        """Get weld parameters with optional filters."""
        conn = self.get_connection()

        query = """
        SELECT wp.*,
               bm.name as base_material,
               fm.name as filler_material,
               jt.name as joint_type,
               pos.code as position_code,
               proc.code as process_code,
               sg.name as shielding_gas
        FROM weld_parameters wp
        LEFT JOIN materials bm ON wp.base_material_id = bm.id
        LEFT JOIN materials fm ON wp.filler_material_id = fm.id
        LEFT JOIN joint_types jt ON wp.joint_type_id = jt.id
        LEFT JOIN welding_positions pos ON wp.position_id = pos.id
        LEFT JOIN welding_processes proc ON wp.process_id = proc.id
        LEFT JOIN shielding_gases sg ON wp.shielding_gas_id = sg.id
        """

        if filters:
            where_clause = []
            params = []

            for key, value in filters.items():
                if value is not None:
                    where_clause.append(f"wp.{key} = ?")
                    params.append(value)

            if where_clause:
                query += " WHERE " + " AND ".join(where_clause)

        df = pd.read_sql_query(query, conn, params=params if filters else None)
        conn.close()
        return df

    def add_weld_parameter(self, parameters):
        """Add a new weld parameter record."""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO weld_parameters
        (base_material_id, filler_material_id, thickness, joint_type_id, position_id,
         process_id, shielding_gas_id, voltage, amperage, wire_feed_speed, travel_speed,
         electrode_diameter, gas_flow_rate, preheat_temp, interpass_temp,
         penetration_depth, quality_rating, success_rate, notes, source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        cursor.execute(query, parameters)
        conn.commit()
        parameter_id = cursor.lastrowid
        conn.close()

        return parameter_id

    def add_user_feedback(self, feedback):
        """Add user feedback for a weld parameter."""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO user_feedback
        (parameter_id, user_voltage, user_amperage, user_wire_feed_speed,
         user_travel_speed, result_quality, weld_success, defects, comments)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        cursor.execute(query, feedback)
        conn.commit()
        feedback_id = cursor.lastrowid
        conn.close()

        return feedback_id

    def get_training_data(self):
        """Get formatted data for ML training."""
        conn = self.get_connection()

        query = """
        SELECT wp.thickness, wp.voltage, wp.amperage, wp.wire_feed_speed,
               wp.travel_speed, wp.electrode_diameter, wp.gas_flow_rate,
               wp.preheat_temp, wp.interpass_temp, wp.quality_rating,
               bm.carbon_content as base_carbon, bm.thermal_conductivity as base_thermal,
               bm.melting_point as base_melting_point, bm.density as base_density,
               fm.carbon_content as filler_carbon, fm.thermal_conductivity as filler_thermal,
               proc.code as process, pos.code as position, jt.name as joint_type
        FROM weld_parameters wp
        LEFT JOIN materials bm ON wp.base_material_id = bm.id
        LEFT JOIN materials fm ON wp.filler_material_id = fm.id
        LEFT JOIN joint_types jt ON wp.joint_type_id = jt.id
        LEFT JOIN welding_positions pos ON wp.position_id = pos.id
        LEFT JOIN welding_processes proc ON wp.process_id = proc.id
        WHERE wp.quality_rating IS NOT NULL
        """

        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
