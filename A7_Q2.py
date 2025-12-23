from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

# -------------------------
# MySQL Connection
# -------------------------
def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="root",
        database="soil_moisture"
    )

# -------------------------
# CREATE - Insert a record
# -------------------------
@app.route("/moisture", methods=["POST"])
def insert_record():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO soil_moisture (sensor_id, moisture_level, date_time) VALUES (%s, %s, %s)",
        (data["sensor_id"], data["moisture_level"], data["date_time"])
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Record inserted"}), 201

# -------------------------
# READ ALL - Get all records
# -------------------------
@app.route("/moisture", methods=["GET"])
def get_all():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM soil_moisture")
    rows = cur.fetchall()
    conn.close()
    result = []
    for r in rows:
        result.append({
            "sensor_id": r[0],
            "moisture_level": r[1],
            "date_time": str(r[2])
        })
    return jsonify(result)

# -------------------------
# UPDATE - Update a record by sensor_id
# -------------------------
@app.route("/moisture/<int:sensor_id>", methods=["PUT"])
def update(sensor_id):
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE soil_moisture SET moisture_level=%s, date_time=%s WHERE sensor_id=%s",
        (data["moisture_level"], data["date_time"], sensor_id)
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Record updated"})

# -------------------------
# DELETE - Delete a record by sensor_id
# -------------------------
@app.route("/moisture/<int:sensor_id>", methods=["DELETE"])
def delete(sensor_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM soil_moisture WHERE sensor_id=%s", (sensor_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Record deleted"})

# -------------------------
# FILTER - Records below a threshold
# -------------------------
@app.route("/moisture/below/<float:threshold>", methods=["GET"])
def below_threshold(threshold):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM soil_moisture WHERE moisture_level < %s", (threshold,))
    rows = cur.fetchall()
    conn.close()
    result = []
    for r in rows:
        result.append({
            "sensor_id": r[0],
            "moisture_level": r[1],
            "date_time": str(r[2])
        })
    return jsonify(result)

# -------------------------
# Run the Flask server
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)
