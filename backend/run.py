from app import app
from app.socketio_server import socketio

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=8080, debug=True, allow_unsafe_werkzeug=True)
