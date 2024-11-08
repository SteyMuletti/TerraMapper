import time
import math
from typing import List, Tuple, Optional
from dataclasses import dataclass
import logging
import threading
from enum import Enum
from djitellopy import Tello

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('drone_operations.log'),
        logging.StreamHandler()
    ]
)

@dataclass
class DroneState:
    """Represents the current state of the drone."""
    battery: int = 0
    temperature: int = 0
    height: int = 0
    flight_time: int = 0
    speed_x: int = 0
    speed_y: int = 0
    speed_z: int = 0

class FlightMode(Enum):
    """Enum for different flight modes."""
    NORMAL = "normal"
    SAFE = "safe"  # More conservative parameters
    SPORT = "sport"  # More aggressive parameters

@dataclass
class FlightParameters:
    """Flight parameters for different modes."""
    max_speed: int
    max_altitude: int
    max_distance: int
    min_battery: int
    rotation_speed: int

class SafetyMonitor:
    """Monitors drone safety parameters and triggers callbacks on violations."""
    
    def __init__(self, parameters: FlightParameters, callback):
        self.parameters = parameters
        self.callback = callback
        self.monitoring = False
        self.monitor_thread = None

    def start_monitoring(self, drone):
        """Start safety monitoring in a separate thread."""
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(drone,),
            daemon=True
        )
        self.monitor_thread.start()

    def stop_monitoring(self):
        """Stop safety monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()

    def _monitor_loop(self, drone):
        """Main monitoring loop."""
        while self.monitoring:
            try:
                # Check battery
                if drone.get_battery() < self.parameters.min_battery:
                    self.callback("LOW_BATTERY")

                # Check height
                if drone.get_height() > self.parameters.max_altitude:
                    self.callback("MAX_ALTITUDE_EXCEEDED")

                # Check temperature
                if drone.get_temperature() > 60:  # Example threshold
                    self.callback("HIGH_TEMPERATURE")

                time.sleep(1)  # Check interval
            except Exception as e:
                logging.error(f"Error in safety monitoring: {e}")

class DroneControl:
    """Enhanced drone control system with safety features and mission planning."""

    FLIGHT_MODES = {
        FlightMode.NORMAL: FlightParameters(
            max_speed=100,
            max_altitude=30,
            max_distance=50,
            min_battery=20,
            rotation_speed=60
        ),
        FlightMode.SAFE: FlightParameters(
            max_speed=50,
            max_altitude=15,
            max_distance=30,
            min_battery=30,
            rotation_speed=45
        ),
        FlightMode.SPORT: FlightParameters(
            max_speed=150,
            max_altitude=50,
            max_distance=100,
            min_battery=25,
            rotation_speed=90
        )
    }

    def __init__(self, flight_mode: FlightMode = FlightMode.NORMAL):
        self.drone = Tello()
        self.is_connected = False
        self.flight_mode = flight_mode
        self.parameters = self.FLIGHT_MODES[flight_mode]
        self.safety_monitor = SafetyMonitor(
            self.parameters,
            self._handle_safety_violation
        )
        self.state = DroneState()
        self._mission_cancelled = False

    def connect(self) -> bool:
        """Connect to the drone with enhanced error handling and setup."""
        try:
            logging.info("Attempting to connect to the drone...")
            self.drone.connect()
            self.is_connected = True
            
            # Initial state update
            self._update_state()
            
            # Start safety monitoring
            self.safety_monitor.start_monitoring(self.drone)
            
            logging.info(f"Drone connected successfully. Battery: {self.state.battery}%")
            return True
            
        except Exception as e:
            logging.error(f"Error while connecting to drone: {e}")
            self.is_connected = False
            return False

    def _update_state(self):
        """Update internal drone state."""
        try:
            self.state.battery = self.drone.get_battery()
            self.state.temperature = self.drone.get_temperature()
            self.state.height = self.drone.get_height()
            self.state.flight_time = self.drone.get_flight_time()
            self.state.speed_x = self.drone.get_speed_x()
            self.state.speed_y = self.drone.get_speed_y()
            self.state.speed_z = self.drone.get_speed_z()
        except Exception as e:
            logging.error(f"Error updating drone state: {e}")

    def _handle_safety_violation(self, violation_type: str):
        """Handle safety violations."""
        logging.warning(f"Safety violation detected: {violation_type}")
        self._mission_cancelled = True
        self.land()

    def set_flight_mode(self, mode: FlightMode):
        """Change flight mode and update parameters."""
        self.flight_mode = mode
        self.parameters = self.FLIGHT_MODES[mode]
        logging.info(f"Flight mode changed to: {mode.value}")

    def takeoff(self) -> bool:
        """Enhanced takeoff with pre-flight checks."""
        try:
            if not self.is_connected:
                raise Exception("Drone is not connected")

            # Pre-flight checks
            self._update_state()
            if self.state.battery < self.parameters.min_battery:
                raise Exception(f"Battery too low for takeoff: {self.state.battery}%")

            logging.info("Initiating takeoff sequence...")
            self.drone.takeoff()
            time.sleep(5)  # Stabilization time
            
            # Post-takeoff checks
            self._update_state()
            if self.state.height < 50:  # Example threshold
                raise Exception("Takeoff may have failed - insufficient altitude")

            logging.info("Takeoff successful")
            return True

        except Exception as e:
            logging.error(f"Takeoff failed: {e}")
            self.land()
            return False

    def land(self) -> bool:
        """Enhanced landing with safety checks."""
        try:
            if not self.is_connected:
                raise Exception("Drone is not connected")

            logging.info("Initiating landing sequence...")
            
            # Gradual descent if high up
            current_height = self.drone.get_height()
            if current_height > 120:  # Example threshold
                logging.info("High altitude detected, performing gradual descent...")
                self.drone.go_xyz_speed(0, 0, 60, 50)  # Move to safer altitude
                time.sleep(3)

            self.drone.land()
            time.sleep(3)  # Wait for landing

            # Verify landing
            if self.drone.get_height() > 10:
                raise Exception("Landing verification failed")

            logging.info("Landing successful")
            return True

        except Exception as e:
            logging.error(f"Error during landing: {e}")
            # Emergency land as last resort
            try:
                self.drone.emergency()
            except:
                pass
            return False

    def execute_mission(self, waypoints: List[Tuple[int, int, int]], 
                       speeds: Optional[List[int]] = None,
                       rotations: Optional[List[int]] = None) -> bool:
        """Execute a complete mission with waypoints."""
        try:
            if not self.is_connected:
                raise Exception("Drone is not connected")

            self._mission_cancelled = False
            num_waypoints = len(waypoints)
            
            # Initialize speeds and rotations if not provided
            if speeds is None:
                speeds = [self.parameters.max_speed] * num_waypoints
            if rotations is None:
                rotations = [0] * num_waypoints

            # Validate mission parameters
            self._validate_mission(waypoints, speeds, rotations)

            # Execute mission
            for i, (waypoint, speed, rotation) in enumerate(zip(waypoints, speeds, rotations)):
                if self._mission_cancelled:
                    logging.warning("Mission cancelled due to safety violation")
                    return False

                logging.info(f"Navigating to waypoint {i+1}/{num_waypoints}")
                success = self._navigate_to_waypoint(waypoint, speed, rotation)
                if not success:
                    return False

            return True

        except Exception as e:
            logging.error(f"Mission execution failed: {e}")
            self.land()
            return False

    def _validate_mission(self, waypoints: List[Tuple[int, int, int]], 
                         speeds: List[int],
                         rotations: List[int]):
        """Validate mission parameters."""
        if not all(len(x) == len(waypoints) for x in [speeds, rotations]):
            raise ValueError("Waypoints, speeds, and rotations must have equal length")

        # Check if any waypoint exceeds maximum distance
        for wp in waypoints:
            distance = math.sqrt(wp[0]**2 + wp[1]**2)
            if distance > self.parameters.max_distance:
                raise ValueError(f"Waypoint {wp} exceeds maximum allowed distance")

        # Validate speeds
        if any(s > self.parameters.max_speed for s in speeds):
            raise ValueError(f"Speed exceeds maximum allowed: {self.parameters.max_speed}")

        # Validate altitudes
        if any(wp[2] > self.parameters.max_altitude for wp in waypoints):
            raise ValueError(f"Altitude exceeds maximum allowed: {self.parameters.max_altitude}")

    def _navigate_to_waypoint(self, waypoint: Tuple[int, int, int], 
                            speed: int,
                            rotation: int) -> bool:
        """Navigate to a single waypoint with enhanced error checking."""
        try:
            # Update state before movement
            self._update_state()
            
            # Rotate to desired orientation
            if rotation != 0:
                self.drone.rotate_clockwise(rotation)
                time.sleep(2)

            # Move to waypoint
            self.drone.go_xyz_speed(waypoint[0], waypoint[1], waypoint[2], speed)
            time.sleep(3)

            # Verify position (if available in your drone's SDK)
            # This is a simplified example
            current_height = self.drone.get_height()
            if abs(current_height - waypoint[2]) > 50:  # Example threshold
                raise Exception("Failed to reach target position")

            return True

        except Exception as e:
            logging.error(f"Navigation error: {e}")
            return False

    def disconnect(self) -> bool:
        """Safely disconnect from the drone."""
        try:
            if self.is_connected:
                logging.info("Initiating disconnect sequence...")
                
                # Stop safety monitoring
                self.safety_monitor.stop_monitoring()
                
                # Land if still in air
                if self.state.height > 10:
                    self.land()
                
                self.drone.end()
                self.is_connected = False
                logging.info("Drone disconnected successfully")
                return True
            
            return False

        except Exception as e:
            logging.error(f"Error during disconnection: {e}")
            return False

    def get_state(self) -> DroneState:
        """Get current drone state."""
        self._update_state()
        return self.state

# Example usage
if __name__ == "__main__":
    # Create drone controller in safe mode
    controller = DroneControl(flight_mode=FlightMode.SAFE)
    
    try:
        # Connect and execute simple mission
        if controller.connect():
            if controller.takeoff():
                waypoints = [
                    (50, 0, 100),   # Forward 50cm at 100cm height
                    (0, 50, 100),   # Right 50cm
                    (0, 0, 100)     # Return to start
                ]
                speeds = [30, 30, 30]  # Conservative speeds
                rotations = [90, -90, 0]  # Rotate at each waypoint
                
                controller.execute_mission(waypoints, speeds, rotations)
                
            controller.land()
    finally:
        controller.disconnect()
