import math
from dobot import DobotDllType as dType

CON_STR = {
    dType.DobotConnect.DobotConnect_NoError: "DobotConnect_NoError",
    dType.DobotConnect.DobotConnect_NotFound: "DobotConnect_NotFound",
    dType.DobotConnect.DobotConnect_Occupied: "DobotConnect_Occupied"
}


class Dobot():
    def __init__(self, home_x=200, home_y=0, home_z=50, production=False):
        self.production = production

        if production:
            self.DobotAPI = dType.load()

        self.home_x = home_x
        self.home_y = home_y
        self.home_z = home_z

        if production:
            self.connect()

    def connect(self):
        state = dType.ConnectDobot(self.DobotAPI, "", 115200)

        if state[0] != dType.DobotConnect.DobotConnect_NoError:
            raise ValueError("Failed to connect dobot. ", CON_STR[state[0]])

        dType.SetQueuedCmdClear(self.DobotAPI)
        dType.SetHOMEParams(self.DobotAPI, self.home_x, self.home_y, self.home_z, 0, isQueued=1)

    def disconnect(self):
        dType.DisconnectDobot(self.DobotAPI)

    def setHOMEParam(self, x, y, z):
        dType.SetHOMEParams(self.DobotAPI, x, y, z, 0, isQueued=1)

    def setHOME(self):
        dType.SetHOMECmd(self.DobotAPI, temp=0, isQueued=1)

    def moveXYZ(self, x, y, z, r=0, mode="movl"):
        if self.production:
            y_offset = 20.0 / 22.5

            ptp_mode = dType.PTPMode.PTPMOVLXYZMode
            if mode == 'jump':
                ptp_mode = dType.PTPMode.PTPJUMPXYZMode

            idx = dType.SetPTPCmd(self.DobotAPI, ptp_mode, x, y*y_offset, z, r, isQueued=1)[0]
            self.sleep(0.2)
        else:
            print("try to move ({x}, {y}, {z})".format(x=x, y=y, z=z))
            idx = -1
        return idx

    def getPose(self):
        if self.production:
            pose = dType.GetPose(self.DobotAPI)
        else:
            pose = [200, 0, 0]

        return pose[:2]


    def startQueue(self):
        dType.SetQueuedCmdStartExec(self.DobotAPI)

    def stopQueue(self):
        dType.SetQueuedCmdStopExec(self.DobotAPI)

    def getCurrentIndex(self):
        return dType.GetQueuedCmdCurrentIndex(self.DobotAPI)

    def getCurrentPosition(self):
        return

    def sleep(self, s):
        if self.production:
            dType.dSleep(s)

    def drawLine(self, current_pos, next_pos, z):
        self.moveXYZ(next_pos["x"], next_pos["y"], z)
        self.moveXYZ(current_pos["x"], current_pos["y"], z)
        idx = self.moveXYZ(next_pos["x"], next_pos["y"], z)
        return idx


    def drawSquare(self, size, x, y, z):
        points = [[x, y], [x + size, y], [x + size, y + size], [x, y + size], [x, y]]

        for i, point in enumerate(points):
            self.moveXYZ(point[0], point[1], z)
            if i < len(points) - 1:
                next_point = points[i + 1]
                self.moveXYZ(next_point[0], next_point[1], z)
                self.moveXYZ(point[0], point[1], z)
            else:
                self.moveXYZ(point[0], point[1], z + 30)


if __name__ == '__main__':
    dobot = Dobot()

    dobot.connect()
    idx = 0
    for i in range(1, 10):
        idx = dobot.moveXYZ(200 - i * 10, 0, 0)

    while idx > dobot.getCurrentIndex():
        dobot.sleep(100)

    dobot.disconnect()
