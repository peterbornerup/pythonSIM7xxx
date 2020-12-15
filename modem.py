from atParser import ATParser
from parse import *
import time

# class handling the modem connectivity and common AT commands


class SIM7070G:
    def __init__(self, port="COM6"):
        self.AT = ATParser(port)

        # wait for modem to repond
        self.AT.sendAtUntilOk("", 100, 300)

        # turn off radio
        self.AT.sendAtUntilResp("+CFUN=0", "OK")

        self.AT.sendAtUntilResp('+CGDCONT=1,"IP","onomondo"')

        # enable full functionality
        self.AT.sendAtUntilResp("+CFUN=1", "OK")

        # get sim ready
        self.AT.sendAtUntilResp("+CPIN?", "READY")

        # error codes
        self.AT.sendAtUntilResp("+CMEE=2")

        # Enable network registration unsolicited result code with location information
        self.AT.sendAtUntilResp("+CREG=2")

    def turnRFOff(self):
        self.AT.sendAtUntilResp("+CFUN=0", "OK")

    def turnRFOn(self):
        self.AT.sendAtUntilResp("+CFUN=1", "OK")

    def getSignalQuality(self):
        success, resp = self.AT.getSendAtUntilResp("+CSQ")
        res = search("+CSQ: {:d},{:d}", resp)
        if res:
            return res.fixed[0]

        return 99  # error

    def setPreferredMode(self, mode="lte"):
        at = "+CNMP="
        if mode == "lte":
            at += "38"
        elif mode == "gsm":
            at += "13"
        else:  # auto
            at += "2"

        self.AT.sendAtUntilResp(at)

    def attachNetwork(self, network="auto", technology="lte"):

        self.detach()

        if technology == "gsm":
            self.setPreferredMode("gsm")  # probably not needed
        else:
            self.setPreferredMode("lte")

        at = 'AT+COPS=1,0,"' + network + '"'

        if technology != "gsm":
            at += ",7"
        # else:
        #     at += ",0"

        if network == "auto":
            at = "AT+COPS=0"

        success = self.AT.sendAtEnforceResp(at, "+CREG: 5", 20000)

        if not success:
            return success

        n = 0
        maxTries = 100
        success = False
        while n < maxTries and not success:
            success = self.AT.sendAtUntilResp("+CGREG?", "+CGREG: 0,5", 1)
            time.sleep(0.5)
            n += 1

        self.getConnectionType()

        self.AT.sendAtUntilResp("+CGATT=1", "OK", 1, 5000)

        # wait untill we have attached
        # self.AT.sendAtUntilResp("+CGPADDR", "OK")

        self.setPDPContext()

        # self.AT.sendAtUntilResp("+CNACT?")

    def setPreferredLteMode(self, mode="both"):
        at = "+CMNB="
        if mode == "catm1":
            at += "1"
        elif mode == "nbiot":
            at += "2"
        else:  # auto
            at += "3"

        self.AT.sendAtUntilResp(at)

    def checkAttach(self):
        self.AT.sendAtUntilResp("+COPS?")

    def register(self):
        print("auto select")
        print(self.AT.sendAtUntilResp("+COPS=0"))

        n = 0
        maxTries = 100
        success = False
        while n < maxTries and not success:
            success = self.AT.sendAtUntilResp("+CGREG?", "5", 1)
            time.sleep(0.5)
            n += 1

    def detach(self):
        ok, res = self.AT.getSendAtUntilResp("+COPS?", "OK", 1)
        status = search("+COPS: {:d}", res)

        if status:
            if status.fixed[0] == 1:
                self.AT.sendAtUntilResp("+COPS=2", "OK", 1, 3000)
            elif status.fixed[0] != 2:  # check if we have detached already.
                self.AT.sendAtEnforceResp("AT+COPS=2", "+CREG: 0", 5000)

    def getAvailableNetworks(self):

        self.detach()
        success, resp = self.AT.sendAtEnforceResp(
            "AT+COPS=?", "OK", 200 * 1000
        )  # search for networks
        # parse the response... or just read it and attach specific network

    def getConnectionType(self):
        self.AT.sendAtUntilResp("+CPSI?")

    def setPDPContext(self):
        self.AT.sendAtUntilResp('+CNCFG=0,1,"onomondo"')  # configure PDP context

        self.AT.sendAtEnforceResp(
            "AT+CNACT=0,1", "ACTIVE", 10000
        )  # activate pdp context

        return self.AT.sendAtUntilResp("+CNACT?", "OK", 1, 5000)

    def openTCP(self, address="1.2.3.4", port=4321):
        # assuming everyting is ok until this point

        # disconnect if existing connection exist
        # self.endTCP()

        self.AT.sendAtUntilResp(
            '+CASSLCFG=0,"SSL",0', "OK", 3
        )  # deactivate ssl support on pdp context 0

        self.AT.sendAtExpectResp(
            'AT+CAOPEN=0,0,"TCP","' + address + '",' + str(port), "OK"
        )

    def disablePSMandEDRX(self):
        self.AT.sendAtUntilResp("+CEDRXS=0", "OK")
        self.AT.sendAtUntilResp("+CPSMS=0", "OK")

    def transmitTCP(self, payload):
        tmp = str.encode(payload)
        self.AT.sendAtUntilResp(
            "+CASEND=0," + str(len(tmp)), ">"
        )  # wait for ready to send

        self.AT.sendAtExpectResp(payload)

    def endTCP(self):
        self.AT.sendAtUntilResp("+CACLOSE=0", "OK", 1)


class SIM7600x:
    def __init__(self, port="COM6"):
        self.AT = ATParser(port)

        # wait for modem to repond
        self.AT.sendAtUntilOk("", 100, 300)

        # turn off radio
        self.AT.sendAtUntilResp("+CFUN=0", "OK")

        self.AT.sendAtUntilResp('+CGDCONT=1,"IP","onomondo"')

        # enable full functionality
        self.AT.sendAtUntilResp("+CFUN=1", "OK")

        # get sim ready
        self.AT.sendAtUntilResp("+CPIN?", "READY")

        # error codes
        self.AT.sendAtUntilResp("+CMEE=2")

        # Enable network registration unsolicited result code with location information
        self.AT.sendAtUntilResp("+CREG=2")

    def turnRFOff(self):
        self.AT.sendAtUntilResp("+CFUN=0", "OK")

    def turnRFOn(self):
        self.AT.sendAtUntilResp("+CFUN=1", "OK")

    def getSignalQuality(self):
        success, resp = self.AT.getSendAtUntilResp("+CSQ")
        res = search("+CSQ: {:d},{:d}", resp)
        if res:
            return res.fixed[0]

        return 99  # error

    def setPreferredMode(self, mode="lte"):
        at = "+CNMP="
        if mode == "lte":
            at += "38"
        elif mode == "gsm":
            at += "13"
        else:  # auto
            at += "2"

        self.AT.sendAtUntilResp(at)

    def attachNetwork(self, network="auto", technology="lte"):

        self.detach()

        if technology == "gsm":
            self.setPreferredMode("gsm")  # probably not needed
        else:
            self.setPreferredMode("lte")

        at = 'AT+COPS=1,0,"' + network + '"'

        if technology != "gsm":
            at += ",7"
        # else:
        #     at += ",0"

        if network == "auto":
            at = "AT+COPS=0"

        success = self.AT.sendAtEnforceResp(at, "+CREG: 5", 20000)

        if not success:
            return success

        n = 0
        maxTries = 100
        success = False
        while n < maxTries and not success:
            success = self.AT.sendAtUntilResp("+CGREG?", "+CGREG: 0,5", 1)
            time.sleep(0.5)
            n += 1

        self.getConnectionType()

        self.AT.sendAtUntilResp("+CGATT=1", "OK", 1, 5000)

        # wait untill we have attached
        # self.AT.sendAtUntilResp("+CGPADDR", "OK")

        self.setPDPContext()

        # self.AT.sendAtUntilResp("+CNACT?")

    def setPreferredLteMode(self, mode="both"):
        return  # not implemented

    def checkAttach(self):
        self.AT.sendAtUntilResp("+COPS?")

    def detach(self):
        ok, res = self.AT.getSendAtUntilResp("+COPS?", "OK", 1)
        status = search("+COPS: {:d}", res)

        if status:
            if status.fixed[0] == 1:
                self.AT.sendAtUntilResp("+COPS=2", "OK", 1, 3000)
            elif status.fixed[0] != 2:  # check if we have detached already.
                self.AT.sendAtEnforceResp("AT+COPS=2", "+CREG: 0", 5000)

    def getAvailableNetworks(self):

        self.detach()
        success, resp = self.AT.sendAtEnforceResp(
            "AT+COPS=?", "OK", 200 * 1000
        )  # search for networks
        # parse the response...

    def getConnectionType(self):
        self.AT.sendAtUntilResp("+CPSI?")

    def setPDPContext(self):
        self.AT.sendAtUntilResp('+CNCFG=0,1,"onomondo"')  # configure PDP context

        self.AT.sendAtEnforceResp(
            "AT+CNACT=0,1", "ACTIVE", 10000
        )  # activate pdp context

        return self.AT.sendAtUntilResp("+CNACT?", "OK", 1, 5000)

    def openTCP(self, address="1.2.3.4", port=4321):
        # assuming everyting is ok until this point

        # disconnect if existing connection exist
        # self.endTCP()

        self.AT.sendAtUntilResp(
            '+CASSLCFG=0,"SSL",0', "OK", 3
        )  # deactivate ssl support on pdp context 0

        self.AT.sendAtExpectResp(
            'AT+CAOPEN=0,0,"TCP","' + address + '",' + str(port), "OK"
        )

    def disablePSMandEDRX(self):
        return  # not implemented

    def transmitTCP(self, payload):
        tmp = str.encode(payload)
        self.AT.sendAtUntilResp(
            "+CASEND=0," + str(len(tmp)), ">"
        )  # wait for ready to send

        self.AT.sendAtExpectResp(payload)

    def endTCP(self):
        self.AT.sendAtUntilResp("+CACLOSE=0", "OK", 1)

