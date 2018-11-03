from flask import Flask, jsonify, request
from Dobot import Dobot
import signal
import argparse
import sys

import json

baseZ = 8
upZ = 20

current_position = {
    "x": 200,
    "y": 0
}

baseX = 173
baseY = -75

app = Flask(__name__)


def map_input(x, y):
    diff_x = (291 - 173)
    map_x = diff_x * x

    diff_y = (26 + 75)
    map_y = diff_y * y

    re_x = baseX + map_x
    re_y = baseY + map_y

    return re_x, re_y


@app.route("/", methods=["GET"])
def status():
    return jsonify({"status": "OK"})


@app.route("/init", methods=["GET"])
def init():
    dobot.setHOME()
    return jsonify({"status": "OK"})


@app.route("/stop_all", methods=["GET"])
def stop_all():
    dobot.stopQueue()
    return jsonify({"status": "stop"})


@app.route("/adj_z", methods=["POST"])
def adj_z():
    data = json.loads(request.data)
    z = data["z"]
    global baseZ
    global upZ
    baseZ = z
    upZ = z + 20
    return jsonify({"baseZ": baseZ, "upZ": upZ})


@app.route("/move", methods=["POST"])
def move():
    print(request.data)
    data = json.loads(request.data)
    x = data["x"]
    y = data["y"]

    re_x, re_y = map_input(x, y)
    next_position = {
        "x": re_x,
        "y": re_y
    }
    command_type = data["type"]

    global current_position
    idx = -1

    if command_type == "line":
        round_count = data.get("round_count", 1)
        idx = dobot.drawLine(current_position, next_position, baseZ, round_count)

    if command_type == "up":
        idx = dobot.moveXYZ(next_position["x"], next_position["y"], upZ)

    if command_type == "down":
        idx = dobot.moveXYZ(next_position["x"], next_position["y"], baseZ, mode="jump")

    current_position = next_position

    return jsonify({"index": idx, "current_position": current_position})


@app.route("/get_pose", methods=["GET"])
def get_pose():
    pose = dobot.getPose()
    global current_position
    current_position["x"] = pose[0]
    current_position["y"] = pose[1]

    return jsonify({"current_position": current_position})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", type=str, default="debug")
    args = parser.parse_args()

    production = False
    if args.env == "production":
        production = True

    print("production env: {0}".format(production))

    dobot = Dobot(production=production)


    def defer(signal, frame):
        global dobot
        if production:
            dobot.disconnect()
            print("disconnect")
        else:
            print("disconnect")

        sys.exit(0)


    signal.signal(signal.SIGINT, defer)

    app.run(host="0.0.0.0", port=3001, threaded=False)
