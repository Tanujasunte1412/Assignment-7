from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smarthome.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Model
class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    light = db.Column(db.String(10))
    fan = db.Column(db.String(10))
    temperature = db.Column(db.Float)

# Create database
with app.app_context():
    db.create_all()

# Route to update sensor data
@app.route('/update', methods=['POST'])
def update_data():
    data = request.json
    new_data = SensorData(
        light=data['light'],
        fan=data['fan'],
        temperature=data['temperature']
    )
    db.session.add(new_data)
    db.session.commit()

    print("Data Updated:", data)   # OUTPUT IN COMMAND WINDOW
    return jsonify({"message": "Sensor data updated successfully"})

# Route to show status
@app.route('/status', methods=['GET'])
def status():
    latest = SensorData.query.order_by(SensorData.id.desc()).first()
    if latest:
        return jsonify({
            "Light Status": latest.light,
            "Fan Status": latest.fan,
            "Temperature": latest.temperature
        })
    return jsonify({"message": "No data available"})

if __name__ == '__main__':
    app.run(debug=True)
