from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB_FILE = "sensors.db"

# Initialize database and table
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS sensor_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temperature REAL NOT NULL,
            humidity REAL NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ------------------ CRUD Endpoints ------------------

# CREATE
@app.route('/sensor', methods=['POST'])
def create_sensor():
    data = request.json
    temp = data.get("temperature")
    hum = data.get("humidity")
    if temp is None or hum is None:
        return jsonify({"error": "Missing temperature or humidity"}), 400

    try:
        temp = float(temp)
        hum = float(hum)
    except ValueError:
        return jsonify({"error": "Invalid number"}), 400

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO sensor_readings (temperature, humidity, timestamp) VALUES (?, ?, ?)",
              (temp, hum, timestamp))
    conn.commit()
    conn.close()
    return jsonify({"message": "Sensor reading added"}), 201

# READ all
@app.route('/sensor', methods=['GET'])
def get_all_sensors():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM sensor_readings")
    rows = c.fetchall()
    conn.close()
    result = [{"id": r[0], "temperature": r[1], "humidity": r[2], "timestamp": r[3]} for r in rows]
    return jsonify(result)

# READ by ID
@app.route('/sensor/<int:id>', methods=['GET'])
def get_sensor(id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM sensor_readings WHERE id=?", (id,))
    row = c.fetchone()
    conn.close()
    if row:
        return jsonify({"id": row[0], "temperature": row[1], "humidity": row[2], "timestamp": row[3]})
    return jsonify({"error": "Not found"}), 404

# UPDATE
@app.route('/sensor/<int:id>', methods=['PUT'])
def update_sensor(id):
    data = request.json
    temp = data.get("temperature")
    hum = data.get("humidity")
    if temp is None and hum is None:
        return jsonify({"error": "No data to update"}), 400

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    if temp is not None:
        c.execute("UPDATE sensor_readings SET temperature=? WHERE id=?", (float(temp), id))
    if hum is not None:
        c.execute("UPDATE sensor_readings SET humidity=? WHERE id=?", (float(hum), id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Sensor reading updated"})

# DELETE
@app.route('/sensor/<int:id>', methods=['DELETE'])
def delete_sensor(id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM sensor_readings WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Sensor reading deleted"})

# Filter readings below threshold
@app.route('/sensor/threshold', methods=['GET'])
def filter_threshold():
    temp_threshold = request.args.get("temperature", type=float)
    hum_threshold = request.args.get("humidity", type=float)

    query = "SELECT * FROM sensor_readings WHERE 1=1"
    params = []

    if temp_threshold is not None:
        query += " AND temperature < ?"
        params.append(temp_threshold)
    if hum_threshold is not None:
        query += " AND humidity < ?"
        params.append(hum_threshold)

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()

    result = [{"id": r[0], "temperature": r[1], "humidity": r[2], "timestamp": r[3]} for r in rows]
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)