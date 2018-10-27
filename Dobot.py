import math
from dobot import DobotDllType as dType

CON_STR = {
    dType.DobotConnect.DobotConnect_NoError: "DobotConnect_NoError",
    dType.DobotConnect.DobotConnect_NotFound: "DobotConnect_NotFound",
    dType.DobotConnect.DobotConnect_Occupied: "DobotConnect_Occupied"
}

DobotAPI = dType.load()


class Dobot():
    def __init__(self, home_x=200, home_y=0, home_z=50):
        self.home_x = home_x
        self.home_y = home_y
        self.home_z = home_z

    def connect(self):
        state = dType.ConnectDobot(DobotAPI, "", 115200)

        if state[0] != dType.DobotConnect.DobotConnect_NoError:
            raise ValueError("Failed to connect dobot. ", CON_STR[state[0]])

        dType.SetQueuedCmdClear(DobotAPI)
        dType.SetHOMEParams(DobotAPI, self.home_x, self.home_y, self.home_z, 0, isQueued=1)
        # self.setHOME()

    def disconnect(self):
        dType.DisconnectDobot(DobotAPI)

    def setHOMEParam(self, x, y, z):
        dType.SetHOMEParams(DobotAPI, x, y, z, 0, isQueued=1)

    def setHOME(self):
        dType.SetHOMECmd(DobotAPI, temp=0, isQueued=1)

    def moveXYZ(self, x, y, z, r=0):
        idx = dType.SetPTPCmd(DobotAPI, dType.PTPMode.PTPMOVLXYZMode, x, y, z, r, isQueued=1)[0]
        return idx

    def emergencyStop(self):
        return

    def startQueue(self):
        dType.SetQueuedCmdStartExec(DobotAPI)

    def stopQueue(self):
        dType.SetQueuedCmdStopExec(DobotAPI)

    def getCurrentIndex(self):
        return dType.GetQueuedCmdCurrentIndex(DobotAPI)

    def getCurrentPosition(self):
        return

    def sleep(self, s):
        dType.dSleep(s)

    def drawLine(self, current_pos, next_pos, z):
        self.moveXYZ(next_pos["x"], next_pos["y"], z)
        self.sleep(0.2)
        self.moveXYZ(current_pos["x"], current_pos["y"], z)
        self.sleep(0.2)
        self.moveXYZ(next_pos["x"], next_pos["y"], z)

    def drawStar(self, z):
        star_points = [[315, 0], [278, 20], [278, 55], [240, 40], [200, 60], [230, 0],
                       [200, -60], [240, -40], [278, -55], [278, -20], [315, 0]]

        for i, point in enumerate(star_points):
            self.moveXYZ(point[0], point[1], z)
            self.sleep(0.2)
            if i < len(star_points) - 1:
                next = star_points[i + 1]
                self.moveXYZ(next[0], next[1], z)
                self.sleep(0.2)
                self.moveXYZ(point[0], point[1], z)
                self.sleep(0.2)
            else:
                self.moveXYZ(point[0], point[1], z + 30)

    def drawSquare(self, size, x, y, z):
        points = [[x, y], [x + size, y], [x + size, y + size], [x, y + size], [x, y]]

        for i, point in enumerate(points):
            self.moveXYZ(point[0], point[1], z)
            self.sleep(0.2)
            if i < len(points) - 1:
                next_point = points[i + 1]
                self.moveXYZ(next_point[0], next_point[1], z)
                self.sleep(0.2)
                self.moveXYZ(point[0], point[1], z)
                self.sleep(0.2)
            else:
                self.moveXYZ(point[0], point[1], z + 30)

    def drawDot(self, dotRadius, x, y, z):
        self.moveXYZ(x, y, z)
        self.sleep(0.1)

        for X in range(-1 * dotRadius, dotRadius, 1):
            for Y in range(-1 * dotRadius, dotRadius, 1):
                if math.sqrt(math.pow(X, 2) + math.pow(Y, 2)) < dotRadius:
                    x_ = x + X
                    y_ = y + Y
                    self.moveXYZ(x_, y_, z)

        self.moveXYZ(x, y, z + 30)


if __name__ == '__main__':
    dobot = Dobot()

    dobot.connect()
    idx = 0
    for i in range(1, 10):
        idx = dobot.moveXYZ(200 - i * 10, 0, 0)

    while idx > dobot.getCurrentIndex():
        dobot.sleep(100)

    dobot.disconnect()
