from modem import SIM7070G
from modem import SIM7600x
import json
import time
import sys


# initialize the modem. Change the port if it does not match.
modem = SIM7070G("COM6")
# modem = SIM7600x("COM6")

# modem.setPreferredMode("lte")
# modem.setPreferredLteMode("catm1")

modem.attachNetwork()

# for specific network
# modem.attachNetwork("Telenor DK")

# for specific network and access technology
# modem.attachNetwork("Telenor DK", "lte")

# get signal quality
modem.AT.getSendAtUntilResp("+CSQ", "OK")

modem.getConnectionType()


####################################
## FOR TESTING TCP STACK ON MODEM ##
####################################

# init TCP stack on modem
# modem.openTCP()
#
# json_string = """
# {
#    "researcher": {
#         "name": "Ford Prefect",
#         "species": "Betelgeusian"
#     }
# }
# """
# payload = json.dumps(json_string)
#
# modem.transmitTCP(payload)
#
# modem.endTCP()

####################################
##          END TCP TEST          ##
####################################

modem.detach()
