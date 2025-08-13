from app import app
from app.socketio_server import socketio, init_socketio

if __name__ == "__main__":
    print("正在啟動服務器，監聽端口 8080...")
    
    # 暫時跳過重置功能
    # print("重置所有使用者線上狀態...")
    # init_socketio()
    
    socketio.run(app, host="127.0.0.1", port=8080, debug=True, allow_unsafe_werkzeug=True)
