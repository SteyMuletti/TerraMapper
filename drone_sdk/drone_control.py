import time
from djitellopy import Tello
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DroneControl:
    def __init__(self):
        self.drone = Tello()
        self.is_connected = False

    def connect(self):
        """Connect to the drone with error handling"""
        try:
            logging.info("Attempting to connect to the drone...")
            self.drone.connect()
            self.is_connected = True
            logging.info(f"Drone connected: {self.drone.get_battery()}% battery")
        except Exception as e:
            logging.error(f"Error while connecting to drone: {e}")
            self.is_connected = False

    def takeoff(self):
        """Take off the drone with error handling"""
        try:
            if not self.is_connected:
                raise Exception("Drone is not connected.")
            logging.info("Taking off...")
            self.drone.takeoff()
            time.sleep(5)  # Wait for the drone to stabilize
            logging.info("Drone has taken off.")
        except Exception as e:
            logging.error(f"Error during takeoff: {e}")
            self.land()

    def land(self):
        """Land the drone with error handling"""
        try:
            if not self.is_connected:
                raise Exception("Drone is not connected.")
            logging.info("Landing the drone...")
            self.drone.land()
            time.sleep(5)  # Wait for landing
            logging.info("Drone has landed.")
        except Exception as e:
            logging.error(f"Error during landing: {e}")
            self.drone.end()

    def set_waypoints(self, waypoints, speeds, rotations):
        """Set waypoints with speed and rotation, with error handling"""
        try:
            if not self.is_connected:
                raise Exception("Drone is not connected.")
            if len(waypoints) != len(speeds) or len(speeds) != len(rotations):
                raise ValueError("Waypoints, speeds, and rotations must be the same length.")

            for i, wp in enumerate(waypoints):
                speed = speeds[i]
                rotation = rotations[i]

                logging.info(f"Flying to waypoint {i + 1}: {wp}, Speed: {speed} cm/s, Rotation: {rotation}°")
                
                # Rotate to the target angle
                self.drone.rotate_clockwise(rotation)
                time.sleep(2)

                # Fly to the waypoint
                self.drone.go_xyz_speed(wp[0], wp[1], wp[2], speed)
                time.sleep(3)  # Wait for drone to reach the waypoint

                logging.info(f"Arrived at waypoint {i + 1}: {wp}")

        except Exception as e:
            logging.error(f"Error in waypoint navigation: {e}")
            self.land()

    def disconnect(self):
        """Disconnect from the drone safely"""
        try:
            if self.is_connected:
                logging.info("Disconnecting from the drone...")
                self.drone.end()
                self.is_connected = False
                logging.info("Drone disconnected.")
            else:
                logging.warning("Drone is not connected.")
        except Exception as e:
            logging.error(f"Error during disconnection: {e}")
