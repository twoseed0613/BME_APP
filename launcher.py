import subprocess
import threading
import webbrowser
import sys
import os
import socket
import time

def wait_for_server(host="localhost", port=8501, timeout=20):
    """檢查 Streamlit 是否啟動成功"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            time.sleep(1)
    return False

def main():
    if not os.environ.get("STREAMLIT_BROWSER_OPENED"):
        os.environ["STREAMLIT_BROWSER_OPENED"] = "1"

        # app.py 路徑
        script_path = os.path.join(os.path.dirname(sys.executable), "app.py")
        if not os.path.exists(script_path):
            script_path = "app.py"

        # 啟動 Streamlit
        subprocess.Popen([sys.executable, "-m", "streamlit", "run", script_path])

        # 等 Streamlit 完全啟動，再開瀏覽器
        def open_browser_when_ready():
            if wait_for_server():
                webbrowser.open("http://localhost:8501")
            else:
                print("Streamlit 啟動超時，請手動打開 http://localhost:8501")

        threading.Thread(target=open_browser_when_ready).start()

if __name__ == "__main__":
    main()