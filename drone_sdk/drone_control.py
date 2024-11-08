import time
from djitellopy import Tello

class DroneControl:
    def __init__(self):
        self.drone = Tello()

    def connect(self):
        """Connect to the drone"""
        print("Connecting to drone...")
        self.drone.connect()
        print("Drone connected: ", self.drone.get_battery(), " % battery")

    def takeoff(self):
        """Take off the drone"""
        print("Taking off...")
        self.drone.takeoff()
        time.sleep(5)

    def land(self):
        """Land the drone"""
        print("Landing...")
        self.drone.land()
        time.sleep(5)

    def set_waypoints(self, waypoints, speeds, rotations):
        """
        Set advanced waypoints with speed control and rotation.
        waypoints: List of tuples (x, y, z) coordinates for each waypoint.
        speeds: List of speeds corresponding to each waypoint (cm/s).
        rotations: List of rotations (degrees) corresponding to each waypoint.
        """
        for i, wp in enumerate(waypoints):
            speed = speeds[i]  # Speed at the current waypoint
            rotation = rotations[i]  # Rotation in degrees at the current waypoint

            print(f"Flying to waypoint {i + 1}: {wp}, Speed: {speed} cm/s, Rotation: {rotation}°")

            # Rotate to the target angle before flying
            self.drone.rotate_clockwise(rotation)
            time.sleep(2)  # Wait for rotation to complete

            # Fly to the waypoint with the given speed
            self.drone.go_xyz_speed(wp[0], wp[1], wp[2], speed)
            time.sleep(3)  # Wait for the drone to reach the waypoint

            print(f"Arrived at waypoint {i + 1}: {wp}")

    def disconnect(self):
        """Disconnect from the drone"""
        print("Disconnecting from drone...")
        self.drone.end()

# Example usage
if __name__ == '__main__':
    drone_control = DroneControl()

    # Connect to the drone
    drone_control.connect()

    # Take off the drone
    drone_control.takeoff()

    # Define waypoints with speed and rotation for each waypoint
    waypoints = [(50, 0, 100), (100, 0, 100), (100, 50, 150), (0, 50, 150)]
    speeds = [30, 40, 35, 25]  # Speed for each waypoint in cm/s
    rotations = [0, 90, 180, 270]  # Rotation at each waypoint in degrees

    # Set the waypoints with speed and rotation
    drone_control.set_waypoints(waypoints, speeds, rotations)

    # Land the drone
    drone_control.land()

    # Disconnect the drone
    drone_control.disconnect()
