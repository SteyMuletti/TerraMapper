from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

# Route to serve the main page with the map
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle waypoint data (POST request)
@app.route('/api/waypoints', methods=['POST'])
def receive_waypoints():
    data = request.json  # Receiving waypoints data as JSON
    waypoints = data.get('waypoints', [])
    
    # Process the waypoints (e.g., save to file or database)
    # For now, just print them to the console
    print(f"Received waypoints: {waypoints}")

    # Respond with a success message
    return jsonify({"message": "Waypoints received successfully!"})

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
