import time
import logging
from dji_sdk.dji_drone import DJIDrone  # Direct import if your DJI SDK is installed properly

# Set up logging for troubleshooting and monitoring
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DroneControl:
    def __init__(self, app_key):
        """Initialize the DJI SDK Drone with App Key for authentication."""
        self.drone = DJIDrone(app_key=app_key)  # Initialize with app key
        self.is_connected = False

    def connect(self):
        """Connect to the DJI drone with error handling."""
        try:
            logging.info("Attempting to connect to the drone...")
            self.drone.connect()
            self.is_connected = True
            battery_level = self.drone.get_battery_percentage()  # Get battery level as feedback
            logging.info(f"Drone connected: {battery_level}% battery")
        except Exception as e:
            logging.error(f"Error connecting to the drone: {e}")
            self.is_connected = False

    def takeoff(self):
        """Take off the drone with error handling."""
        try:
            if not self.is_connected:
                raise Exception("Drone not connected.")
            logging.info("Initiating takeoff...")
            self.drone.takeoff()
            time.sleep(5)  # Wait for the drone to stabilize
            logging.info("Drone has successfully taken off.")
        except Exception as e:
            logging.error(f"Takeoff error: {e}")
            self.land()  # Ensure safety by landing if any error occurs

    def land(self):
        """Land the drone safely with error handling."""
        try:
            if not self.is_connected:
                raise Exception("Drone not connected.")
            logging.info("Initiating landing...")
            self.drone.land()
            time.sleep(5)  # Ensure safe landing
            logging.info("Drone has successfully landed.")
        except Exception as e:
            logging.error(f"Landing error: {e}")

    def set_waypoints(self, waypoints):
        """Set waypoints and navigate with error handling."""
        try:
            if not self.is_connected:
                raise Exception("Drone not connected.")
            for i, (x, y, z) in enumerate(waypoints):
                logging.info(f"Navigating to waypoint {i + 1}: x={x}, y={y}, z={z}")
                self.drone.go_to_location(x, y, z)  # Assuming this command exists in the DJI SDK
                time.sleep(5)  # Adjust time as necessary based on waypoint distance
                logging.info(f"Reached waypoint {i + 1}")
        except Exception as e:
            logging.error(f"Error in waypoint navigation: {e}")
            self.land()  # Safely land in case of error

    def disconnect(self):
        """Safely disconnect from the drone."""
        try:
            if self.is_connected:
                logging.info("Disconnecting from the drone...")
                self.drone.disconnect()
                self.is_connected = False
                logging.info("Drone successfully disconnected.")
            else:
                logging.warning("Drone is not currently connected.")
        except Exception as e:
            logging.error(f"Disconnection error: {e}")
