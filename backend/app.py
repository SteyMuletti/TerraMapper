from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import time
from threading import Thread
from djitellopy import Tello

app = Flask(__name__)
socketio = SocketIO(app)

# Global drone instance
drone = Tello()

# Telemetry data update thread
def telemetry():
    while True:
        if drone.is_connected:
            position = drone.get_current_position()  # Get the drone's current position (x, y, z)
            battery = drone.get_battery()
            # Send telemetry data to frontend every 1 second
            socketio.emit('telemetry', {'position': position, 'battery': battery})
            time.sleep(1)

@app.route('/')
def index():
    return render_template('index.html')

# Route to start flight and send waypoints to the drone
@app.route('/api/start_flight', methods=['POST'])
def start_flight():
    data = request.json
    waypoints = data.get('waypoints', [])
    speeds = data.get('speeds', [])
    rotations = data.get('rotations', [])
    
    # Connect to the drone
    drone.connect()
    # Start telemetry thread
    telemetry_thread = Thread(target=telemetry)
    telemetry_thread.daemon = True
    telemetry_thread.start()

    # Take off the drone and set waypoints
    drone.takeoff()
    drone.set_waypoints(waypoints, speeds, rotations)

    return jsonify({"message": "Flight started!"})

@app.route('/api/land', methods=['POST'])
def land():
    drone.land()
    return jsonify({"message": "Drone landing..."})

if __name__ == '__main__':
    app.run(debug=True)
