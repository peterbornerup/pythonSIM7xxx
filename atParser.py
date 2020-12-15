# simple AT parser
import serial  # COM port
import time  # basic timing utils
import logging

logging.basicConfig(filename="at.log", level=logging.DEBUG)


class ATParser:
    def __init__(self, comport="COM6"):
        self.modem = serial.Serial(comport, 115200, timeout=5)
        self.lastCommand = time.time()

    def current_milli_time(self):
        return int(round(time.time() * 1000))

    def timeSinceLastCommand(self):
        return 1000 * (time.time() - self.lastCommand)

    def readSerial(self, timeout=1000):

        # read the serial port with a timeout
        now = self.current_milli_time()

        # wait for incoming data
        while (self.current_milli_time() - now < timeout) and (
            self.modem.in_waiting == 0
        ):
            # do nothing
            time.sleep(1.0 / 1000.0)

        buffer = bytearray()

        while self.modem.in_waiting:
            buffer.extend(self.modem.read())

        tmp = buffer.decode("utf=8")

        print(tmp)
        logging.info(tmp)
        return tmp

    def sendAtExpectResp(self, at, resp="OK", timeout=1000):

        self.sendSerial(at)

        tmp = self.readSerial(timeout)

        success = tmp.find(resp) >= 0

        return success, tmp

    def sendAtEnforceResp(self, at, resp, timeout):

        self.sendSerial(at)
        start = time.time()
        success = False
        tmp = ""
        elapsed = 0.0
        while not success and elapsed < timeout:
            tmp += self.readSerial(timeout)
            elapsed = (time.time() - start) * 100
            time.sleep(0.01)
            success = tmp.find(resp) >= 0

        return success, tmp

    def sendSerial(self, cmd):
        while self.timeSinceLastCommand() < 300:
            time.sleep(1 / 1000.0)
        self.lastCommand = time.time()
        self.modem.write(str.encode(cmd + "\r"))
        print(">>>>" + cmd)

        logging.info(">>>" + cmd)

    def sendAtGetResp(self, at, timeout=1000):
        self.sendSerial(at)

        return self.readSerial(timeout)

    def sendAtUntilOk(self, at, tries=5, commandTimeout=1000):
        n = 0
        success = False
        while n < tries and not success:
            success, resp = self.sendAtExpectResp("AT" + at, "OK", commandTimeout)
            n += 1
        return success

    def sendAtUntilResp(self, at, resp="OK", tries=5, commandTimeout=1000):
        n = 0
        success = False
        while n < tries and not success:
            success, res = self.sendAtExpectResp("AT" + at, resp, commandTimeout)
            n += 1
        return success

    def getSendAtUntilResp(self, at, resp="OK", tries=5, commandTimeout=1000):
        n = 0
        success = False
        while n < tries and not success:
            success, res = self.sendAtExpectResp("AT" + at, resp, commandTimeout)
            n += 1
        return success, res

    # blindly send AT and get the resp
    def SA(self, at, delay=1000, timeout=1000):
        self.sendAtGetResp("AT+" + at, timeout)
        time.sleep(delay / 1000.0)

