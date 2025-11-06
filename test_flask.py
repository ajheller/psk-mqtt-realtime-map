from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, async_mode="eventlet", cors_allowed_origins="*")

@app.route("/")
def index():
    return "Hello from Flask!"

if __name__ == "__main__":
    print("Starting test server...")
    socketio.run(app, host="127.0.0.1", port=5000)
