#!/usr/bin/python3
from flask import Flask, jsonify, request, send_from_directory
from threading import Thread
from railway import Track
from run import run_track
from defaults import *
import yaml
import textwrap

app = Flask(__name__)

# --- init Track similar to model_track.main() ---

def read_config_file():
    try:
        with open(config_file_name, 'r') as config_file:
            config_dict = yaml.safe_load(config_file)
        new_config = default_args.copy()
        for key in config_dict[script_name].keys():
            new_config[key] = config_dict[script_name][key]
        return new_config
    except:
        return default_args

cfg = read_config_file()
t = Track(
    name=cfg['name'],
    host=cfg['host'], port=cfg['port'],
    pin_enable=cfg['pin_enable'],
    pin_fwd=cfg['pin_fwd'],
    pin_rev=cfg['pin_rev'],
    tracks=cfg['tracks'],
    steps=cfg['steps'],
    ctime=cfg['ctime'],
    sensor_pins=cfg['sensor_pins'],
    point_pins=cfg['point_pins'],
    servos=cfg['servos'],
    debug=cfg['debug'],
)

runner = run_track()

# --- REST-style endpoints ---

@app.get("/")
def index():
    return send_from_directory("static", "index.html")

@app.get("/state")
def get_state():
    """Current track, tracks, sensors, points, stats."""
    if not t.is_ok():
        return jsonify({"ok": False})

    return jsonify({
        "ok": True,
        "active_track": t.active_track,
        "tracks": t.tracks,           # list of dicts from get_track_status
        "sensors": t.sensors,         # as in railway.Track
        "points": t.points,           # list of {GPIO,status}
        "speed": t.speed,
        "direction": t.direction,
        "direction_str": t.direction_str,
    })

@app.post("/command")
def post_command():
    """
    Accept commands similar to cTrack.__process_command:
    {
      "cmd": "set_speed" | "stop" | "force_stop" | "set_track" | "point_toggle",
      "args": [...]
    }
    """
    data = request.get_json(force=True)
    cmd = data.get("cmd")
    args = data.get("args", [])

    # runner.process_commands expects [[idx, cmd, *args]]
    cmd_list = [[0, cmd] + args]
    runner.process_commands(t, cmd_list, cfg['debug'])
    return jsonify({"status": "ok"})

# convenience wrappers that map directly to your old keybindings
@app.post("/api/set_speed")
def api_set_speed():
    speed = float(request.json.get("speed", 0.0))
    direction = int(request.json.get("direction", 1))
    cmd_list = [[0, "set_speed", speed, direction]]
    runner.process_commands(t, cmd_list, cfg['debug'])
    return jsonify({"status": "ok"})

@app.post("/api/stop")
def api_stop():
    cmd_list = [[0, "stop"]]
    runner.process_commands(t, cmd_list, cfg['debug'])
    return jsonify({"status": "ok"})

@app.post("/api/force_stop")
def api_force_stop():
    cmd_list = [[0, "force_stop"]]
    runner.process_commands(t, cmd_list, cfg['debug'])
    return jsonify({"status": "ok"})

@app.post("/api/set_track")
def api_set_track():
    idx = int(request.json.get("track", 0))
    cmd_list = [[0, "set_track", idx]]
    runner.process_commands(t, cmd_list, cfg['debug'])
    return jsonify({"status": "ok"})

@app.post("/api/point_toggle")
def api_point_toggle():
    idx = int(request.json.get("point", 0))
    cmd_list = [[0, "point_toggle", idx]]
    runner.process_commands(t, cmd_list, cfg['debug'])
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    # run on e.g. http://0.0.0.0:5000
    app.run(host="0.0.0.0", port=5000, debug=True)
