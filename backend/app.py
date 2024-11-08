from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import time
from threading import Thread
from djitellopy import Tello
from drone_sdk.drone_control import DroneControl

app = Flask(__name__)
socketio = SocketIO(app)

# Initialize drone control
drone_control = DroneControl()

# Global flag to keep the telemetry thread running
telemetry_thread_running = False

def telemetry():
    """Send telemetry data to the frontend via SocketIO"""
    global telemetry_thread_running
    while telemetry_thread_running:
        try:
            if drone_control.is_connected:
                # Get drone position (this is a mock, customize as needed)
                position = drone_control.drone.get_current_position()  # Or other telemetry data
                battery = drone_control.drone.get_battery()

                socketio.emit('telemetry', {'position': position, 'battery': battery})
                time.sleep(1)
            else:
                time.sleep(5)
        except Exception as e:
            print(f"Error during telemetry: {e}")
            telemetry_thread_running = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/start_flight', methods=['POST'])
def start_flight():
    """Start the flight with error handling"""
    try:
        data = request.json
        waypoints = data.get('waypoints', [])
        speeds = data.get('speeds', [])
        rotations = data.get('rotations', [])

        # Connect to the drone
        drone_control.connect()
        if not drone_control.is_connected:
            return jsonify({"message": "Failed to connect to drone"}), 500

        # Start telemetry thread
        global telemetry_thread_running
        telemetry_thread_running = True
        telemetry_thread = Thread(target=telemetry)
        telemetry_thread.daemon = True
        telemetry_thread.start()

        # Take off and set waypoints
        drone_control.takeoff()
        drone_control.set_waypoints(waypoints, speeds, rotations)

        return jsonify({"message": "Flight started!"})

    except Exception as e:
        print(f"Error during flight start: {e}")
        return jsonify({"message": f"Failed to start flight: {str(e)}"}), 500

@app.route('/api/land', methods=['POST'])
def land():
    """Land the drone with error handling"""
    try:
        drone_control.land()
        return jsonify({"message": "Drone landing..."})
    except Exception as e:
        return jsonify({"message": f"Error landing drone: {str(e)}"}), 500

@app.route('/api/disconnect', methods=['POST'])
def disconnect():
    """Disconnect from the drone with error handling"""
    try:
        drone_control.disconnect()
        return jsonify({"message": "Drone disconnected."})
    except Exception as e:
        return jsonify({"message": f"Error disconnecting from drone: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
