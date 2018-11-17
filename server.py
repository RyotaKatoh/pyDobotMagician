from flask import Flask, jsonify, request
from Dobot import Dobot
import signal
import argparse
import sys

import os
import pickle
import json
import numpy as np
import datetime

baseZ = 8
upZ = 20

current_position = {
    "x": 200,
    "y": 0
}

BASE_LENGTH = 120

BASE_POS1 = (190, -40)
BASE_POS2 = (290, 80)
BASE_POS3 = (290, -40)
BASE_POS4 = (190, 80)

ROTATION_2 = np.ones([2,2])
ROTATION_3 = np.ones([2,2])
ROTATION_4 = np.ones([2,2])

app = Flask(__name__)

def calc_rot(A, B):
    Ainv = np.linalg.inv(A)
    x = np.dot(Ainv, B)
    return x.reshape([2, 2])

def setup_rotation():
    A2 = np.array([[BASE_POS1[0], BASE_POS1[1], 0, 0],
                  [0, 0, BASE_POS1[0], BASE_POS1[1]],
                  [BASE_POS4[0], BASE_POS4[1], 0, 0],
                  [0, 0, BASE_POS4[0], BASE_POS4[1]]])
    B2 = np.array([BASE_POS2[0] - BASE_LENGTH, BASE_POS2[1] - BASE_LENGTH, BASE_POS3[0] - BASE_LENGTH, BASE_POS3[1] + BASE_LENGTH])
    rot2 = calc_rot(A2, B2)
    global ROTATION_2
    ROTATION_2 = rot2

    A3 = np.array([[BASE_POS1[0], BASE_POS1[1], 0, 0],
                  [0, 0, BASE_POS1[0], BASE_POS1[1]],
                  [BASE_POS4[0], BASE_POS4[1], 0, 0],
                  [0, 0, BASE_POS4[0], BASE_POS4[1]]])
    B3 = np.array([BASE_POS3[0] - BASE_LENGTH, BASE_POS3[1], BASE_POS2[0] - BASE_LENGTH, BASE_POS2[1]])
    rot3 = calc_rot(A3, B3)
    global ROTATION_3
    ROTATION_3 = rot3

    A4 = np.array([[BASE_POS1[0], BASE_POS1[1], 0, 0],
                  [0, 0, BASE_POS1[0], BASE_POS1[1]],
                  [BASE_POS3[0], BASE_POS3[1], 0, 0],
                  [0, 0, BASE_POS3[0], BASE_POS3[1]]])
    B4 = np.array([BASE_POS4[0], BASE_POS4[1] - BASE_LENGTH, BASE_POS2[0], BASE_POS2[1] - BASE_LENGTH])

    rot4 = calc_rot(A4, B4)
    global ROTATION_4
    ROTATION_4 = rot4

    return rot2, rot3, rot4


def map_input(x, y):
    diff_x = (BASE_POS3[0] - BASE_POS1[0], BASE_POS3[1] - BASE_POS1[1])
    diff_y = (BASE_POS4[0] - BASE_POS1[0], BASE_POS4[1] - BASE_POS1[1])

    re_pos = (diff_x[0] * x + diff_y[0] * y, diff_x[1] * x + diff_y[1] * y)

    return re_pos[0] + BASE_POS1[0], re_pos[1] + BASE_POS1[1]


    # diff_x = BASE_POS2[0] - BASE_POS1[0]
    # diff_y = BASE_POS2[1] - BASE_POS1[1]
    # re_x = diff_x * x + BASE_POS1[0]
    # re_y = diff_y * y + BASE_POS1[1]
    #
    # print("BASE_POS1: {0}".format(BASE_POS1))
    # print("BASE_POS2: {0}".format(BASE_POS2))
    # print("BASE_POS3: {0}".format(BASE_POS3))
    # print("BASE_POS4: {0}".format(BASE_POS4))
    # print('=======')
    # print((x, y))
    # print((re_x, re_y))

    # return re_x, re_y
    #
    # diff = np.array([BASE_LENGTH * x, BASE_LENGTH * y])
    #
    # print('=====base pos======')
    # print(BASE_POS1)
    # print(BASE_POS2)
    # print(BASE_POS3)
    # print(BASE_POS4)
    # print("=============")
    # print("")
    #
    #
    # rotation2 = np.dot(ROTATION_2, np.array(BASE_POS1))
    # rotation3 = np.dot(ROTATION_3, np.array(BASE_POS1))
    # rotation4 = np.dot(ROTATION_4, np.array(BASE_POS1))
    #
    # print(rotation2)
    # print(rotation3)
    # print(rotation4)
    #
    # print("=====ROTATION=====")
    # print(ROTATION_2)
    # print(ROTATION_3)
    # print(ROTATION_4)
    #
    # re_x = (rotation2[0] + rotation3[0] + rotation4[0]) / 3.0 + diff[0]
    # re_y = (rotation2[1] + rotation3[1] + rotation4[1]) / 3.0 + diff[1]
    #
    # print((x, y))
    # print("=======")
    # print((re_x, re_y))
    #
    # print("fuck")
    # return re_x, re_y


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
        sleep_sec = data.get("sleep_sec", 0.4)
        idx = dobot.drawLine(current_position, next_position, baseZ, round_count, sleep_sec=sleep_sec)

    if command_type == "up":
        idx = dobot.moveXYZ(next_position["x"], next_position["y"], upZ)

    if command_type == "down":
        idx = dobot.moveXYZ(next_position["x"], next_position["y"], baseZ, mode="jump")

    current_position = next_position

    return jsonify({"index": idx, "current_position": current_position})


@app.route("/multi_move", methods=["POST"])
def multi_move():
    data = json.loads(request.data)

    command_filename = "commands_{0}.json".format(datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d%H%M%S"))
    with open(os.path.join("./commands", command_filename), "w") as f:
        json.dump(data, f)

    commands = data.get("commands", [])

    global current_position
    idx = -1
    total_command = 0
    received_commands = len(commands)

    for i, cmd in enumerate(commands):
        print("({i}/{n}) {cmd}".format(i=i, n=received_commands, cmd=cmd))
        x = cmd["x"]
        y = cmd["y"]

        re_x, re_y = map_input(x, y)
        next_position = {
            "x": re_x,
            "y": re_y
        }
        command_type = cmd["type"]

        if command_type == "line":
            round_count = cmd.get("round_count", 1)
            sleep_sec = cmd.get("sleep_sec", 0.4)
            idx = dobot.drawLine(current_position, next_position, baseZ, round_count, sleep_sec=sleep_sec)

        if command_type == "up":
            idx = dobot.moveXYZ(next_position["x"], next_position["y"], upZ)

        if command_type == "down":
            idx = dobot.moveXYZ(next_position["x"], next_position["y"], baseZ, mode="jump")

        current_position = next_position
        total_command += 1

    return jsonify({"index": idx, "current_position": current_position, "received_commands": received_commands,
                    "total_commands": total_command})


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
        sleep_sec = data.get("sleep_sec", 0.4)
        idx = dobot.drawLine(current_position, next_position, baseZ, round_count, sleep_sec=sleep_sec)

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

        setup_rotation()

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

    setting_path = "./setting.pickle"
    if os.path.exists(setting_path):
        with open(setting_path, "rb") as f:
            settings = pickle.load(f)

            BASE_POS1 = settings["base_pos1"]
            BASE_POS2 = settings["base_pos2"]
            BASE_POS3 = settings["base_pos3"]
            BASE_POS4 = settings["base_pos4"]
            baseZ = settings["base_z"]
            upz = baseZ + 30

            setup_rotation()

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

        params = {
            "base_pos1": BASE_POS1,
            "base_pos2": BASE_POS2,
            "base_pos3": BASE_POS3,
            "base_pos4": BASE_POS4,
            "base_z": baseZ,
        }

        with open(setting_path, "wb") as f:
            pickle.dump(params, f)

        sys.exit(0)


    signal.signal(signal.SIGINT, defer)

    app.run(host="0.0.0.0", port=3001, threaded=True)
