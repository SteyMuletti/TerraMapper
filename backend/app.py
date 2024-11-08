from flask import Flask, request, jsonify
from drone_sdk.drone_control import DroneControl
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize DroneControl object
drone_control = DroneControl()

@app.route('/start_flight', methods=['POST'])
def start_flight():
    try:
        data = request.json
        waypoints = data.get('waypoints', [])
        speeds = data.get('speeds', [])
        rotations = data.get('rotations', [])
        
        if not waypoints or not speeds or not rotations:
            return jsonify({"error": "Missing required fields: waypoints, speeds, or rotations"}), 400
        
        # Connect to the drone
        drone_control.connect()

        # Start the flight with waypoints
        drone_control.takeoff()
        drone_control.set_waypoints(waypoints, speeds, rotations)
        drone_control.land()
        
        # Disconnect the drone
        drone_control.disconnect()

        return jsonify({"status": "Flight completed successfully!"}), 200
    
    except Exception as e:
        logging.error(f"Error during flight: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
