print("0: app.py file executing")

import os, re
from threading import Thread
from flask import Flask, render_template
from flask_socketio import SocketIO
import folium
from mqtt_stream import mqtt_line_stream, parse_spot

BIND_HOST = os.environ.get("BIND_HOST", "127.0.0.1")
BIND_PORT = int(os.environ.get("BIND_PORT", "5000"))
MAX_MARKERS = int(os.environ.get("MAX_MARKERS", "2000"))

app = Flask(__name__, static_folder="static", template_folder="templates")
socketio = SocketIO(app, async_mode="eventlet", cors_allowed_origins="*")

@socketio.on("connect")
def handle_connect():
    print("⚡ Client connected via Socket.IO")

# @socketio.on("connect")
# def handle_connect():
#     print("⚡ Client connected via Socket.IO")
#     # Test spot (San Francisco)
#     socketio.emit("spot", {
#         "label": "TEST · Hello world",
#         "lat": 37.7749,
#         "lon": -122.4194,
#         "rx_lat": None, "rx_lon": None,
#         "tx_lat": None, "tx_lon": None
#     })
@socketio.on("connect")
def handle_connect():
    print("⚡ Client connected via Socket.IO")
    # keep the TEST emit if you like:
    socketio.emit("spot", {
        "label": "TEST · Hello world",
        "lat": 37.7749, "lon": -122.4194,
        "rx_lat": None, "rx_lon": None, "tx_lat": None, "tx_lon": None
    }, namespace="/")


def build_map_html():
    m = folium.Map(location=[20, 0], zoom_start=2, tiles="CartoDB positron")
    html = m.get_root().render()
    mname = re.search(r"var\s+(map_[a-f0-9]+)\s*=\s*L\.map", html)
    if mname:
        var = mname.group(1)
        html = html.replace("</body>", f"<script>window._folium_map={var};</script></body>")
    return html

FOLIUM_HTML = build_map_html()

@app.route("/")
def index():
#    return "Flask route reached OK"
    import os
    print("Looking for template in:", os.path.abspath(app.template_folder))
    return render_template("index.html", folium_map=FOLIUM_HTML, max_markers=MAX_MARKERS)

# def reader():
#     print("R0: reader function entered")
#     host = os.environ.get("MQTT_HOST", "mqtt.pskreporter.info")
#     port = os.environ.get("MQTT_PORT", "1883")
#     topic = os.environ.get("MQTT_TOPIC", "#")
#     cmd = os.environ.get("MOSQUITTO_SUB_CMD", "mosquitto_sub")
#     print(f"R1: spawning {cmd} -h {host} -p {port} -t {topic}")
#     for raw in mqtt_line_stream(cmd, host, port, topic):
#         print("R2: got line from mqtt_line_stream")
#         spot = parse_spot(raw)
#         print(f"R3: spot={spot}")
#         if spot:
#             socketio.emit("spot", spot)

# # def reader():
# #     host = os.environ.get("MQTT_HOST", "mqtt.pskreporter.info")
# #     port = os.environ.get("MQTT_PORT", "1883")
# #     topic = os.environ.get("MQTT_TOPIC", "#")
# #     cmd = os.environ.get("MOSQUITTO_SUB_CMD", "mosquitto_sub")
# #     for raw in mqtt_line_stream(cmd, host, port, topic):
# #         spot = parse_spot(raw)
# #         print(f"{spot=}")
# #         if spot:
# #             socketio.emit("spot", spot)

# if __name__ == "__main__":
#     print("A: entered main")
#     t = Thread(target=reader, daemon=True)
#     t.start()
#     print("B: started reader thread")
#     socketio.run(app, host=BIND_HOST, port=BIND_PORT, log_output=True)
#     print("C: socketio.run returned")

# def reader():
#     print("R0: reader function entered")
#     host = os.environ.get("MQTT_HOST", "mqtt.pskreporter.info")
#     port = os.environ.get("MQTT_PORT", "1883")
#     topic = os.environ.get("MQTT_TOPIC", "#")
#     cmd = os.environ.get("MOSQUITTO_SUB_CMD", "mosquitto_sub")
#     print(f"R1: spawning {cmd} -h {host} -p {port} -t {topic}")
#     for raw in mqtt_line_stream(cmd, host, port, topic):
#         print("R2: got line from mqtt_line_stream")
#         spot = parse_spot(raw)
#         print(f"R3: spot={spot}")
#         if spot:
#             # 2) emit with explicit namespace and broadcast (safe), and yield
#             socketio.emit("spot", spot, namespace="/", broadcast=True)
#             socketio.sleep(0)  # give the eventlet loop a tick

# if __name__ == "__main__":
#     print("A: entered main")
#     # 3) use SocketIO’s own background task helper
#     socketio.start_background_task(reader)
#     print("B: started reader task")
#     socketio.run(app, host=BIND_HOST, port=BIND_PORT, log_output=True)
#     print("C: socketio.run returned")

@socketio.on("connect")
def handle_connect():
    print("⚡ Client connected via Socket.IO")
    socketio.emit("spot", {
        "label": "TEST · Hello world",
        "lat": 37.7749, "lon": -122.4194,
        "rx_lat": None, "rx_lon": None, "tx_lat": None, "tx_lon": None
    }, namespace="/")  # no 'broadcast' arg

def reader():
    print("R0: reader function entered")
    host = os.environ.get("MQTT_HOST", "mqtt.pskreporter.info")
    port = os.environ.get("MQTT_PORT", "1883")
    topic = os.environ.get("MQTT_TOPIC", "#")
    cmd = os.environ.get("MOSQUITTO_SUB_CMD", "mosquitto_sub")
    print(f"R1: spawning {cmd} -h {host} -p {port} -t {topic}")
    for raw in mqtt_line_stream(cmd, host, port, topic):
        print("R2: got line from mqtt_line_stream")
        spot = parse_spot(raw)
        print(f"R3: spot={spot}")
        if spot:
            # send to all connected clients on default namespace
            socketio.emit("spot", spot, namespace="/")  # <-- remove broadcast
            socketio.sleep(0)  # yield to the eventlet loop

if __name__ == "__main__":
    print("A: entered main")
    socketio.start_background_task(reader)   # use SocketIO’s background task helper
    print("B: started reader task")
    socketio.run(app, host=BIND_HOST, port=BIND_PORT, log_output=True)
    print("C: socketio.run returned")
