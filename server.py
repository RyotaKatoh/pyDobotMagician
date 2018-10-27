from flask import Flask, jsonify, request
from Dobot import Dobot

import json

dobot = Dobot()

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

@app.route("/move", methods=["POST"])
def move():
    data = json.loads(request.data)
    next_position = {
        "x": data["x"],
        "y": data["y"]
    }
    command_type = data["type"]

    global current_position

    if command_type == "line":
        dobot.drawLine(current_position, next_position, baseZ)

    if command_type == "up":
        dobot.moveXYZ(next_position["x"], next_position["y"], upZ)

    if command_type == "down":
        dobot.moveXYZ(next_position["x"], next_position["y"], baseZ)

    current_position = next_position

    return jsonify({"current_position": current_position})



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3001)