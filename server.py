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

BASE_POS1 = (190, -40)
BASE_POS2 = (290, 80)
BASE_POS3 = (290, -40)
BASE_POS4 = (190, 80)

app = Flask(__name__)


def map_input(x, y):
    diff_x = BASE_POS2[0] - BASE_POS1[0]
    diff_y = BASE_POS2[1] - BASE_POS1[1]
    re_x = diff_x * x + BASE_POS1[0]
    re_y = diff_y * y + BASE_POS1[1]

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

@app.route("/adj_base_pos", methods=["POST"])
def adj_base_xy():
    data = json.loads(request.data)
    x1 = data["x1"]
    y1 = data["y1"]

    x2 = data["x2"]
    y2 = data["y2"]
    global BASE_POS1, BASE_POS2
    BASE_POS1 = (x1, y1)
    BASE_POS2 = (x2, y2)
    return jsonify({"base_pos1": BASE_POS1, "base_pos2": BASE_POS2})

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
    global baseZ

    return jsonify({"current_position": current_position, "base_z": baseZ})

@app.route("/absolute_move", methods=["POST"])
def absolute_move():
    data = json.loads(request.data)
    next_position = {
        "x": data["x"],
        "y": data["y"]
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


@app.route("/calibrate", methods=["POST"])
def calibrate_pos():
    data = json.loads(request.data)

    pose = dobot.getPose()

    cal_type = data["type"]
    idx = data.get("index", 1)

    global baseZ, upZ, BASE_POS1, BASE_POS2, BASE_POS3, BASE_POS4, current_position

    if cal_type == "z":
        baseZ = pose[2]
        upZ = pose[2] + 30
        return jsonify({"base_z": baseZ, "up_z": upZ})

    if cal_type == "xy":
        if idx == 1:
            BASE_POS1 = tuple(pose[:2])

        if idx == 2:
            BASE_POS2 = tuple(pose[:2])

        if idx == 3:
            BASE_POS3 = tuple(pose[:2])

        if idx == 4:
            BASE_POS4 = tuple(pose[:2])

        return jsonify({"idx": idx, "base_pose": pose[:2]})

    if cal_type == "move":
        for pos in [BASE_POS1, BASE_POS3, BASE_POS2, BASE_POS4]:
            idx = dobot.moveXYZ(pos[0], pos[1], baseZ, mode="jump")
            dobot.sleep(4)
            print(dobot.getPose())

        dobot.moveXYZ(200, 0, upZ, mode="jump")

        p = dobot.getPose()
        current_position["x"] = p[0]
        current_position["y"] = p[1]

        return jsonify({"current_positon": current_position})

    return jsonify({"cal_type": cal_type})



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
