from app import app
from app.socketio_server import socketio

if __name__ == "__main__":
    print("正在啟動服務器，監聽端口 8080...")
    socketio.run(app, host="127.0.0.1", port=8080, debug=True, allow_unsafe_werkzeug=True)
