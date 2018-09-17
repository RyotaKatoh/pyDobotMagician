from dobot import DobotDllType as dType

CON_STR = {
    dType.DobotConnect.DobotConnect_NoError: "DobotConnect_NoError",
    dType.DobotConnect.DobotConnect_NotFound: "DobotConnect_NotFound",
    dType.DobotConnect.DobotConnect_Occupied: "DobotConnect_Occupied"
}


class Dobot():
    def __init__(self, home_x=200, home_y=0, home_z=0):
        self.api = dType.load()

        self.home_x = home_x
        self.home_y = home_y
        self.home_z = home_z

    def connect(self):
        state = dType.ConnectDobot(self.api, "", 115200)

        if state != dType.DobotConnect.DobotConnect_NoError:
            raise ValueError("Failed to connect dobot. ", CON_STR[state])

        dType.SetQueuedCmdClear(self.api)
        dType.SetHOMEParams(self.api, self.home_x, self.home_y, self.home_z, 0, isQueued=1)
        self.setHOME()

    def disconnect(self):
        dType.DisconnectDobot(self.api)

    def setHOME(self):
        dType.SetHOMECmd(self.api, temp=0, isQueued=1)

    def moveXYZ(self, x, y, z, r=0):
        idx = dType.SetPTPCmd(self.api, dType.PTPMode.PTPMOVLXYZMode, x, y, z, r, isQueued=1)[0]
        return idx

    def startQueue(self):
        dType.SetQueuedCmdStartExec(self.api)

    def stopQueue(self):
        dType.SetQueuedCmdStopExec(self.api)

    def getCurrentIndex(self):
        return dType.GetQueuedCmdCurrentIndex(self.api)

    def sleep(self, ms):
        dType.dSleep(ms)


if __name__ == '__main__':
    dobot = Dobot()

    dobot.connect()
    idx = 0
    for i in range(1, 10):
        idx = dobot.moveXYZ(200 - i*10, 0, 0)

    while idx > dobot.getCurrentIndex():
        dobot.sleep(100)

    dobot.disconnect()
