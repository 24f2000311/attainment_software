import threading
import webview
from waitress import serve
from app import app   # your Flask app file

def start_flask():
    serve(app, host="127.0.0.1", port=5525)

if __name__ == "__main__":
    flask_thread = threading.Thread(target=start_flask)
    flask_thread.daemon = True
    flask_thread.start()

    webview.create_window(
        title="Attainment Software System",
        url="http://127.0.0.1:5525",
        width=1200,
        height=800, # Enabled for debugging
    )
    webview.start(debug=False)
