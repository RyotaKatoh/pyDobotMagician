from flask import Flask, jsonify, request
from Dobot import Dobot
import signal
import argparse
import sys

import json

baseZ = 0
upZ = 20

current_position = {
    "x": 0,
    "y": 0
}

app = Flask(__name__)


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


@app.route("/move", methods=["POST"])
def move():
    data = json.loads(request.data)
    next_position = {
        "x": data["x"],
        "y": data["y"]
    }
    command_type = data["type"]

    global current_position
    idx = -1

    if command_type == "line":
        idx = dobot.drawLine(current_position, next_position, baseZ)

    if command_type == "up":
        idx = dobot.moveXYZ(next_position["x"], next_position["y"], upZ)

    if command_type == "down":
        idx = dobot.moveXYZ(next_position["x"], next_position["y"], baseZ)

    current_position = next_position

    return jsonify({"index": idx, "current_position": current_position})


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

    app.run(host="0.0.0.0", port=3001)
