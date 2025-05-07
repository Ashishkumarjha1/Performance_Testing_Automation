import base64
import hashlib
import hmac
import json
import logging
import os

import requests

# Setting environment variables
# If specific variables are set then its read from them separately
# otherwise its set from BASE_DIR envvariable
# if (os.getenv("LOGGING_LEVEL")):
#     logLevel = os.environ['LOGGING_LEVEL']
# else:
#     # setting default logging level to default
#     logLevel = "DEBUG"

# if (os.getenv("LOGS_DIR")):
#     logs_dir = os.environ["LOGS_DIR"]
#     print(logs_dir)
# elif (os.getenv("BASE_DIR")):
#     logs_dir = os.environ["BASE_DIR"]+"/Main/Logs"
#     print(logs_dir)
# else:
#     script_directory = os.path.abspath(os.path.dirname(__file__))
#     parent_directory = os.path.abspath(
#         os.path.join(script_directory, os.pardir))
#     grandparent_directory = os.path.abspath(
#         os.path.join(parent_directory, os.pardir))
#     os.environ['BASE_DIR'] = grandparent_directory
#     logs_dir = grandparent_directory+"/Main/Logs"

# logFile = logs_dir + '/config.log'

# # Logging levels
# if (logLevel == "DEBUG"):
#     logging.basicConfig(filename=logFile, level=logging.DEBUG,
#                         format='%(asctime)s - %(levelname)s - %(message)s')
# elif (logLevel == "INFO"):
#     logging.basicConfig(filename=logFile, level=logging.INFO,
#                         format='%(asctime)s - %(levelname)s - %(message)s')
# elif (logLevel == "WARNING"):
#     logging.basicConfig(filename=logFile, level=logging.WARNING,
#                         format='%(asctime)s - %(levelname)s - %(message)s')
# elif (logLevel == "ERROR"):
#     logging.basicConfig(filename=logFile, level=logging.ERROR,
#                         format='%(asctime)s - %(levelname)s - %(message)s')
# elif (logLevel == "CRITICAL"):
#     logging.basicConfig(filename=logFile, level=logging.CRITICAL,
#                         format='%(asctime)s - %(levelname)s - %(message)s')

# api commands
api_url = {
    "login": "/api/v1/login",
    "logout": "/api/v1/logout",
    "createenterprise": "/api/v1/enterprise",
    "createuser": "/api/v1/centraluser",
    "site": "/api/v1/site",
    "linkuserandsite": "/api/v1/site/user",
    "resetpassword": "/api/v1/resetpassword",
    "addfileascamera": "/api/v1/channel",
    "getallchannel": "/api/v1/channel",
    "license": "/api/v1/license",
    "searchchannel": "/api/v1/channel/search",
    "addonvifcamera": "/api/v1/channel",
    "getprofile": "/api/v1/channel/test",
    "addserver": "/api/v1/vas",
    "startfrserver": "/api/v1/callFRServer?flag=1",
    "config": "/api/v1/config",
    "addVms": "/api/v1/addVms",
    "getVmsList": "/api/v1/vmsList",
    "addVmsCamera": "/api/v1/channel",
    "getVms": "/api/v1/vms",
    "saveVms": "/api/v1/vms",
    "connectDvm": "/api/v1/vms/dvm/channel",
    "authenticateDvm": "/api/v1/vms/dvm/authenticate"
}

# command for api url construction of run and stop analytics
api_url_RunStopAnalytics = {
    "runanalytics": "/runAnalytics?startFlag=1",
    "stopanalytics": "/stopAnalytics?startFlag=1"
}


key = "F8378550-38BE-11E8-BEE9-8101A52E5AE9"


class configSession:

    # Generate encrpted password
    def encryptpassword(value):
        n = hmac.new(key.encode(encoding='utf-8'),
                     value.encode(encoding='utf-8'), hashlib.sha256).digest()
        new_password = base64.b64encode(
            (bytearray(n))).decode(encoding='utf-8')
        return new_password

    def __init__(self, url, username, password):
        self.baseurl = url
        self.username = username
        self.password = password
        self.resetToken = None
        self.userid = None
        self.session = requests.session()
        self.sessionid = None
        self.jwtToken = None

    def geturl(self, command):
        url = self.baseurl + api_url[command]
        return url

    # To ping server status
    def geturlPingServer(self, ip, port):
        url = self.baseurl + "/api/v1/serverstatus/ip/" + \
            str(ip) + "/port/" + str(port)
        return url

    # SiteID and ChannelID will be given from function call and api is constructed
    def geturl_ChannelFunctions(self, SiteID, ChannelID):
        url = self.baseurl + "/api/v1/site/" + \
            str(SiteID) + "/analytic/channel/" + str(ChannelID) + "/vas/1"
        return url

    # here command is from api_urlRunStopAnalytics and api is constructed based on command from function call
    def geturlRunStopAnalytics(self, command, SiteID):
        url = self.baseurl + "/api/v1/site/" + \
            str(SiteID) + api_url_RunStopAnalytics[command]
        return url

    def geturlChannelConfig(self, ChannelID):
        url = self.baseurl + "/api/v1/channel/" + str(ChannelID) + "?config=1"
        return url

    def geturlLicense(self, LicenseID, ChannelID):
        url = self.baseurl + "/api/v1/license/" + \
            str(LicenseID) + "/channel/" + str(ChannelID)
        return url

    def geturlGetServerID(self, SiteID):
        url = self.baseurl + "/api/v1/site/" + str(SiteID) + "/vas"
        return url

    def geturlUser(self, userid):
        url = self.baseurl + "/api/v1/centraluser/" + str(userid)
        return url

    def getlogindata(self):
        login = {"email": self.username, "password": configSession.encryptpassword(
            self.password), "profileId": [1, 2, 3, 4]}
        login_info = json.dumps(login)
        return login_info

    def getlogindata1(self):
        login = {"email": self.username, "password": self.password}
        login_info = json.dumps(login)
        return login_info

    def geturlConnectVms(self, VmsID):
        url = self.baseurl+"/api/v1/vmsConnection/"+str(VmsID)
        return url

    def geturlVmsCameraList(self, VmsID):
        url = self.baseurl+"/api/v1/cameraList/"+str(VmsID)
        return url

    def getheader(self):
        if (self.sessionid == None):
            header = {'Content-type': 'application/json'}
        elif (self.jwtToken != None):
            header = {
                'Content-type': 'application/json',
                'JSESSIONID': self.sessionid,
                'authorization': 'authorization ' + self.jwtToken}
        else:
            header = {
                'Content-type': 'application/json',
                'JSESSIONID': self.sessionid}
        return header

    def resetpassword(self, password):
        body = {"id": self.userid,
                "password": configSession.encryptpassword(password),
                "confirmPassword": configSession.encryptpassword(password),
                "token": self.resetToken}
        response = self.session.put(self.geturl("resetpassword"), data=json.dumps(
            body), headers=self.getheader(), verify=False)
        if (response.status_code == 200):
            self.password = password
            self.resetToken = None
            return True
        else:
            return False

    def login(self):
        response = self.session.post(self.geturl(
            "login"), data=self.getlogindata(), headers=self.getheader(), verify=False)
        if (response.status_code == 200):
            # Login is successful
            # Store the JWToken for future interactions
            self.sessionid = self.session.cookies['JSESSIONID']
            content = json.loads((response.content).decode())
            logging.info(content["message"])
            # Check if this is the first login and password needs to be reset
            centraluser = content["result"][0]["centraluser"]
            self.userid = centraluser["id"]
            self.jwtToken = content["jwtToken"]

            if ("resetToken" in centraluser):
                self.resetToken = centraluser["resetToken"]
                logging.info('Need to reset password')
            else:
                logging.info(
                    'Not the first attempt, password reset is not needed')
                self.resetToken = None

            return True
        else:
            logging.error('Login failed')
            # content = json.loads((response.content).decode())
            logging.error(response.content)
            raise Exception(response.content)
            return False

    def login1(self):
        response = self.session.post(self.geturl(
            "login"), data=self.getlogindata1(), headers=self.getheader(), verify=False)
        if (response.status_code == 200):
            # Login is successful
            # Store the JWToken for future interactions
            self.sessionid = self.session.cookies['JSESSIONID']
            content = json.loads((response.content).decode())
            centraluser = content["result"][0]["centraluser"]
            self.userid = centraluser["id"]
            self.jwtToken = content["jwtToken"]

            return True
        else:
            return False

    def logout(self):
        # Send the Logout command.
        response = self.session.get(self.geturl(
            "logout"), data=None, headers=self.getheader(), verify=False)
        if (response.status_code == 200):
            return True
        else:
            logging.error('Logout failed')
            raise Exception('Logout failed')
            return False

    # Add file type of camera
    def add_file_as_camera(self, fileascamera):
        # print(self.geturl("addfileascamera"))
        response = self.session.post(self.geturl("addfileascamera"), data=json.dumps(
            fileascamera), headers=self.getheader(), verify=False)
        # print(self.geturl("addfileascamera"))
        # print(fileascamera)

        if (response.status_code == 200):
            # Camera addition successful
            content = json.loads(response.content)
            camera_id = content["result"]["id"]
            logging.info(
                'File camera '+fileascamera["name"]+' added successfully and channelID is '+str(camera_id))
        else:
            logging.error('File camera ' +
                          fileascamera["name"]+' addition failed')
            raise Exception(
                'File camera '+fileascamera["name"]+' addition failed')
            content = json.loads(response.content)
            camera_id = None

        return camera_id

    # Get all site info from server
    def getsitelist(self):
        response = self.session.get(self.geturl(
            "site"), data=None, headers=self.getheader(), verify=False)
        if (response.status_code == 200):
            # site list fetched successfully
            logging.info('Site list fetched successfull')
            content = json.loads(response.content)
            return content["result"]
        else:
            logging.error('Unable to get users')
            raise Exception('Unable to get users')
            return False

    # Get all channel info from server
    def getallchannel(self):
        response = self.session.get(self.geturl(
            "getallchannel"), data=None, headers=self.getheader(), verify=False)
        if (response.status_code == 200):
            content = json.loads(response.content)
            return content["result"]
        else:
            content = json.loads(response.content)
            logging.error('Unable to get channel info')
            raise Exception('Unable to get channel info')
            return content["result"]

    # get specific channel's config
    def getchannelconfig(self, ChannelID):
        response = self.session.get(self.geturlChannelConfig(
            ChannelID), data=None, headers=self.getheader(), verify=False)
        if (response.status_code == 200):
            content = json.loads(response.content)
            return (content["result"])
        else:
            return False

    # add all license
    def add_license(self, licenseinfo):
        response = self.session.post(self.geturl("license"), data=json.dumps(
            licenseinfo), headers=self.getheader(), verify=False)
        if (response.status_code == 200):
            lincode = response.status_code
        else:
            # logging.error('License addition failed')
            # raise Exception('License addition failed')
            lincode = None
        return lincode

    # Get license info from server
    def getlicenseconfig(self):
        response = self.session.get(self.geturl(
            "license"), data=None, headers=self.getheader(), verify=False)
        if (response.status_code == 200):
            logging.info('License config fetched successfull')
            content = json.loads(response.content)
            licenseData = []
            licenseData = content["result"]
            return licenseData
        else:
            logging.error('Unable to get license config')
            raise Exception('Unable to get license config')
            return False

    # function to map license with channel
    def mapLicense(self, LicenseID, ChannelID):
        # print("@@@")
        # print(LicenseID)
        # print(str(ChannelID))
        # print(self.geturlLicense(LicenseID, ChannelID))
        response = self.session.get(self.geturlLicense(
            LicenseID, ChannelID), data=None, headers=self.getheader(), verify=False)
        if (response.status_code == 200):
            logging.info('License '+str(LicenseID) +
                         ' mapped to channelID '+str(ChannelID))
            content = json.loads(response.content)
            return content["code"]
        else:
            logging.error('Mapping License to channelID ' +
                          str(ChannelID)+' failed')
            raise Exception('Mapping License to channelID ' +
                            str(ChannelID)+' failed')
            return False

    # Get all present servers's id
    def getAllServerInfo(self, SiteID):
        response = self.session.get(self.geturlGetServerID(
            SiteID), data=None, headers=self.getheader(), verify=False)
        if (response.status_code == 200):
            content = json.loads(response.content)

            return (content["result"])
        else:
            return False

    # Configure feature
    def enable_features(self, featuresinfo, SiteID, ChannelID, svgPath):
        regiondata = featuresinfo["Region"]

        basePath = os.environ["BASE_DIR"]
        FeatureData = {"zoneList": []}

        # Tripwire feature
        if (regiondata["analyticType"] == 204):
            FeatureData["CameraName"] = featuresinfo["CameraName"]
            FeatureData["referenceWidth"] = featuresinfo["referenceWidth"]
            FeatureData["referenceHeight"] = featuresinfo["referenceHeight"]
            ZoneListData = {"pointList": [], "TripwireRefPoint": {
                "x": 0, "y": 0}, "analyticType": [204]}
            ZoneListData["IndexRegion"] = regiondata["IndexRegion"]
            ZoneListData["RegionSpecificName"] = regiondata["RegionSpecificName"]
            ZoneListData["RegionSpecificPriority"] = regiondata["RegionSpecificPriority"]
            points = regiondata["pointList"]
            RefPoint = regiondata["TripwireRefPoint"]
            pointListinfo1 = {}
            pointListinfo1["x"] = points[0]
            pointListinfo1["y"] = points[1]
            ZoneListData["pointList"].append(pointListinfo1)
            pointListinfo2 = {}
            pointListinfo2["x"] = points[2]
            pointListinfo2["y"] = points[3]
            ZoneListData["pointList"].append(pointListinfo2)
            ZoneListData["TripwireRefPoint"]["x"] = RefPoint[0]
            ZoneListData["TripwireRefPoint"]["y"] = RefPoint[1]
            ZoneListData["TripwireLineType"] = regiondata["TripwireLineType"]
            ZoneListData["TripwireDirection"] = regiondata["TripwireDirection"]
            ZoneListData["RegionName"] = regiondata["RegionSpecificName"]
            ZoneListData["CompleteFrame"] = "3"
            # canvasFilePath = basePath+"/Main/canvas/"+featuresinfo["CameraName"]+".svg"
            canvasFilePath = svgPath
            if (os.path.isfile(canvasFilePath) == True):
                with open(canvasFilePath) as f:
                    svgdata = f.read()
            else:
                svgdata = ""
            FeatureData["linesOnCanvas"] = svgdata
            FeatureData["zoneList"].append(ZoneListData)

        # Face Recognition Feature
        elif (regiondata["analyticType"] == 419):
            FeatureData["CameraName"] = featuresinfo["CameraName"]
            FeatureData["referenceWidth"] = featuresinfo["referenceWidth"]
            FeatureData["referenceHeight"] = featuresinfo["referenceHeight"]

            ZoneListData = {"pointList": [], "analyticType": [419]}
            ZoneListData["EnableFaceRecognition"] = regiondata["EnableFaceRecognition"]
            ZoneListData["EnableFaceVerification"] = regiondata["EnableFaceVerification"]
            ZoneListData["EnableFaceAuthentication"] = regiondata["EnableFaceAuthentication"]

            allServerList = self.getAllServerInfo(SiteID)
            for i in range(len(allServerList)):
                if (allServerList[i]["ip"] == regiondata["FRServerIP"] and allServerList[i]["name"] == regiondata["FRServerName"]):
                    ZoneListData["FRServerID"] = allServerList[i]["id"]

            ZoneListData["FRServerName"] = regiondata["FRServerName"]
            ZoneListData["FRServerIP"] = regiondata["FRServerIP"]
            ZoneListData["FRServerRegistrationPort"] = regiondata["FRServerRegistrationPort"]
            ZoneListData["FRServerRecognitionPort"] = regiondata["FRServerRecognitionPort"]
            ZoneListData["EnableGenderDetection"] = regiondata["EnableGenderDetection"]
            ZoneListData["EnableAgeDetection"] = regiondata["EnableAgeDetection"]
            ZoneListData["FaceForensicAnalysisMaxRanks"] = regiondata["FaceForensicAnalysisMaxRanks"]
            ZoneListData["FRDatabaseSelected"] = regiondata["FRDatabaseSelected"]
            ZoneListData["EnableAutoFaceSaving"] = regiondata["EnableAutoFaceSaving"]
            ZoneListData["ServerFDMinConfidence"] = regiondata["ServerFDMinConfidence"]
            ZoneListData["FRPredictionConfidence"] = regiondata["FRPredictionConfidence"]
            ZoneListData["IndexRegion"] = regiondata["IndexRegion"]
            ZoneListData["RegionSpecificName"] = regiondata["RegionSpecificName"]
            ZoneListData["RegionSpecificPriority"] = regiondata["RegionSpecificPriority"]
            points = regiondata["pointList"]
            pointListinfo1 = {}
            pointListinfo1["x"] = points[0]
            pointListinfo1["y"] = points[1]
            ZoneListData["pointList"].append(pointListinfo1)
            pointListinfo2 = {}
            pointListinfo2["x"] = points[2]
            pointListinfo2["y"] = points[3]
            ZoneListData["pointList"].append(pointListinfo2)
            pointListinfo3 = {}
            pointListinfo1["x"] = points[4]
            pointListinfo1["y"] = points[5]
            ZoneListData["pointList"].append(pointListinfo3)
            pointListinfo4 = {}
            pointListinfo2["x"] = points[6]
            pointListinfo2["y"] = points[7]
            ZoneListData["pointList"].append(pointListinfo4)
            ZoneListData["RegionName"] = regiondata["RegionSpecificName"]
            ZoneListData["CompleteFrame"] = regiondata["CompleteFrame"]
            # canvasFilePath = basePath+"/Main/canvas/"+featuresinfo["CameraName"]+".svg"
            canvasFilePath = svgPath
            if (os.path.isfile(canvasFilePath) == True):
                with open(canvasFilePath) as f:
                    svgdata = f.read()
            else:
                svgdata = ""
            FeatureData["linesOnCanvas"] = svgdata
            FeatureData["zoneList"].append(ZoneListData)

        # Trespass Feature
        elif (regiondata["analyticType"] == 201):
            FeatureData["CameraName"] = featuresinfo["CameraName"]
            FeatureData["referenceWidth"] = featuresinfo["referenceWidth"]
            FeatureData["referenceHeight"] = featuresinfo["referenceHeight"]
            ZoneListData = {"pointList": [], "analyticType": [201]}
            ZoneListData["IndexRegion"] = regiondata["IndexRegion"]
            ZoneListData["RegionSpecificName"] = regiondata["RegionSpecificName"]
            ZoneListData["RegionSpecificPriority"] = regiondata["RegionSpecificPriority"]
            points = regiondata["pointList"]
            pointList = {}
            for i in range(len(points)):
                if (i % 2) == 0:
                    pointList["x"] = points[i]
                if (i % 2) != 0:
                    pointList["y"] = points[i]
                    ZoneListData["pointList"].append(pointList)
                    pointList = {}
            ZoneListData["RegionName"] = regiondata["RegionSpecificName"]
            ZoneListData["CompleteFrame"] = regiondata["CompleteFrame"]
            # canvasFilePath = basePath+"/Main/canvas/"+featuresinfo["CameraName"]+".svg"
            canvasFilePath = svgPath
            if (os.path.isfile(canvasFilePath) == True):
                with open(canvasFilePath) as f:
                    svgdata = f.read()
            else:
                svgdata = ""
            FeatureData["linesOnCanvas"] = svgdata
            FeatureData["zoneList"].append(ZoneListData)

        # Loitering feature
        elif (regiondata["analyticType"] == 202):
            FeatureData["CameraName"] = featuresinfo["CameraName"]
            FeatureData["referenceWidth"] = featuresinfo["referenceWidth"]
            FeatureData["referenceHeight"] = featuresinfo["referenceHeight"]
            ZoneListData = {"pointList": [], "analyticType": [202]}
            ZoneListData["LoiteringTimeMin"] = regiondata["LoiteringTimeMin"]
            ZoneListData["IndexRegion"] = regiondata["IndexRegion"]
            ZoneListData["RegionSpecificName"] = regiondata["RegionSpecificName"]
            ZoneListData["RegionSpecificPriority"] = regiondata["RegionSpecificPriority"]
            points = regiondata["pointList"]
            pointList = {}
            for i in range(len(points)):
                if (i % 2) == 0:
                    pointList["x"] = points[i]
                if (i % 2) != 0:
                    pointList["y"] = points[i]
                    ZoneListData["pointList"].append(pointList)
                    pointList = {}
            ZoneListData["RegionName"] = regiondata["RegionSpecificName"]
            ZoneListData["CompleteFrame"] = regiondata["CompleteFrame"]
            # canvasFilePath = basePath+"/Main/canvas/"+featuresinfo["CameraName"]+".svg"
            canvasFilePath = svgPath
            if (os.path.isfile(canvasFilePath) == True):
                with open(canvasFilePath) as f:
                    svgdata = f.read()
            else:
                svgdata = ""
            FeatureData["linesOnCanvas"] = svgdata
            FeatureData["zoneList"].append(ZoneListData)

        # Missing Object Detection Feature
        elif (regiondata["analyticType"] == 213):
            FeatureData["CameraName"] = featuresinfo["CameraName"]
            FeatureData["referenceWidth"] = featuresinfo["referenceWidth"]
            FeatureData["referenceHeight"] = featuresinfo["referenceHeight"]
            ZoneListData = {"pointList": [], "analyticType": [213]}
            ZoneListData["UnattendedTimeMin"] = regiondata["UnattendedTimeMin"]
            ZoneListData["IndexRegion"] = regiondata["IndexRegion"]
            ZoneListData["RegionSpecificName"] = regiondata["RegionSpecificName"]
            ZoneListData["RegionSpecificPriority"] = regiondata["RegionSpecificPriority"]
            points = regiondata["pointList"]
            pointList = {}
            for i in range(len(points)):
                if (i % 2) == 0:
                    pointList["x"] = points[i]
                if (i % 2) != 0:
                    pointList["y"] = points[i]
                    ZoneListData["pointList"].append(pointList)
                    pointList = {}
            ZoneListData["RegionName"] = regiondata["RegionSpecificName"]
            ZoneListData["CompleteFrame"] = regiondata["CompleteFrame"]
            # canvasFilePath = basePath+"/Main/canvas/"+featuresinfo["CameraName"]+".svg"
            canvasFilePath = svgPath
            if (os.path.isfile(canvasFilePath) == True):
                with open(canvasFilePath) as f:
                    svgdata = f.read()
            else:
                svgdata = ""
            FeatureData["linesOnCanvas"] = svgdata
            FeatureData["zoneList"].append(ZoneListData)

        # left baggage detection feature
        elif (regiondata["analyticType"] == 208):
            FeatureData["CameraName"] = featuresinfo["CameraName"]
            FeatureData["referenceWidth"] = featuresinfo["referenceWidth"]
            FeatureData["referenceHeight"] = featuresinfo["referenceHeight"]
            ZoneListData = {"pointList": [], "analyticType": [208]}
            ZoneListData["Alert_LeftObject_string"] = regiondata["Alert_LeftObject_string"]
            ZoneListData["UnattendedTimeMin"] = regiondata["UnattendedTimeMin"]
            ZoneListData["LBDSensitivity"] = regiondata["LBDSensitivity"]
            ZoneListData["IndexRegion"] = regiondata["IndexRegion"]
            ZoneListData["RegionSpecificName"] = regiondata["RegionSpecificName"]
            ZoneListData["RegionSpecificPriority"] = regiondata["RegionSpecificPriority"]
            points = regiondata["pointList"]
            pointList = {}
            for i in range(len(points)):
                if (i % 2) == 0:
                    pointList["x"] = points[i]
                if (i % 2) != 0:
                    pointList["y"] = points[i]
                    ZoneListData["pointList"].append(pointList)
                    pointList = {}
            ZoneListData["RegionName"] = regiondata["RegionSpecificName"]
            ZoneListData["CompleteFrame"] = regiondata["CompleteFrame"]
            # canvasFilePath = basePath+"/Main/canvas/"+featuresinfo["CameraName"]+".svg"
            canvasFilePath = svgPath
            if (os.path.isfile(canvasFilePath) == True):
                with open(canvasFilePath) as f:
                    svgdata = f.read()
            else:
                svgdata = ""
            FeatureData["linesOnCanvas"] = svgdata
            FeatureData["zoneList"].append(ZoneListData)

        # crowd detection feature
        elif (regiondata["analyticType"] == 402):
            FeatureData["CameraName"] = featuresinfo["CameraName"]
            FeatureData["referenceWidth"] = featuresinfo["referenceWidth"]
            FeatureData["referenceHeight"] = featuresinfo["referenceHeight"]
            ZoneListData = {"pointList": [], "analyticType": [402]}
            ZoneListData["CrowdCapacityMin"] = regiondata["CrowdCapacityMin"]
            ZoneListData["CrowdCapacityMax"] = regiondata["CrowdCapacityMax"]
            ZoneListData["CrowdCountOffset"] = regiondata["CrowdCountOffset"]
            ZoneListData["CrowdDetectionMethod"] = regiondata["CrowdDetectionMethod"]
            ZoneListData["CrowdingAlarmInterval"] = regiondata["CrowdingAlarmInterval"]
            ZoneListData["IndexRegion"] = regiondata["IndexRegion"]
            ZoneListData["RegionSpecificName"] = regiondata["RegionSpecificName"]
            ZoneListData["RegionSpecificPriority"] = regiondata["RegionSpecificPriority"]
            points = regiondata["pointList"]
            pointList = {}
            for i in range(len(points)):
                if (i % 2) == 0:
                    pointList["x"] = points[i]
                if (i % 2) != 0:
                    pointList["y"] = points[i]
                    ZoneListData["pointList"].append(pointList)
                    pointList = {}
            ZoneListData["RegionName"] = regiondata["RegionSpecificName"]
            ZoneListData["CompleteFrame"] = regiondata["CompleteFrame"]
            # canvasFilePath = basePath+"/Main/canvas/"+featuresinfo["CameraName"]+".svg"
            canvasFilePath = svgPath
            if (os.path.isfile(canvasFilePath) == True):
                with open(canvasFilePath) as f:
                    svgdata = f.read()
            else:
                svgdata = ""
            FeatureData["linesOnCanvas"] = svgdata
            FeatureData["zoneList"].append(ZoneListData)

        # counter flow feature
        elif (regiondata["analyticType"] == 403):
            FeatureData["CameraName"] = featuresinfo["CameraName"]
            FeatureData["referenceWidth"] = featuresinfo["referenceWidth"]
            FeatureData["referenceHeight"] = featuresinfo["referenceHeight"]
            ZoneListData = {"CounterFlowPoints": [],
                            "pointList": [], "analyticType": [403]}
            ZoneListData["CounterFlowTolerance"] = regiondata["CounterFlowTolerance"]
            ZoneListData["CounterFlowThreshold"] = regiondata["CounterFlowThreshold"]
            ZoneListData["CounterFlowSpeedup"] = regiondata["CounterFlowSpeedup"]
            ZoneListData["CounterFlowMethod"] = regiondata["CounterFlowMethod"]
            ZoneListData["Alert_Wrongway_string"] = regiondata["Alert_Wrongway_string"]
            cfPoints = regiondata["CounterFlowPoints"]
            cfPointList = {}
            for i in range(len(cfPoints)):
                if (i % 2) == 0:
                    cfPointList["x"] = cfPoints[i]
                if (i % 2) != 0:
                    cfPointList["y"] = cfPoints[i]
                    ZoneListData["CounterFlowPoints"].append(cfPointList)
                    cfPointList = {}
            ZoneListData["CounterFlowDirection"] = regiondata["CounterFlowDirection"]
            ZoneListData["IndexRegion"] = regiondata["IndexRegion"]
            ZoneListData["RegionSpecificName"] = regiondata["RegionSpecificName"]
            ZoneListData["RegionSpecificPriority"] = regiondata["RegionSpecificPriority"]
            points = regiondata["pointList"]
            pointList = {}
            for j in range(len(points)):
                if (j % 2) == 0:
                    pointList["x"] = points[j]
                if (j % 2) != 0:
                    pointList["y"] = points[j]
                    ZoneListData["pointList"].append(pointList)
                    pointList = {}
            ZoneListData["RegionName"] = regiondata["RegionSpecificName"]
            ZoneListData["CompleteFrame"] = regiondata["CompleteFrame"]
            # canvasFilePath = basePath+"/Main/canvas/"+featuresinfo["CameraName"]+".svg"
            canvasFilePath = svgPath
            if (os.path.isfile(canvasFilePath) == True):
                with open(canvasFilePath) as f:
                    svgdata = f.read()
            else:
                svgdata = ""
            FeatureData["linesOnCanvas"] = svgdata
            FeatureData["zoneList"].append(ZoneListData)

        # Camera Tampering and Video loss alarm feature
        elif (regiondata["analyticType"] == 212 or regiondata["analyticType"] == ['212', '425']):
            FeatureData["CameraName"] = featuresinfo["CameraName"]
            FeatureData["referenceWidth"] = featuresinfo["referenceWidth"]
            FeatureData["referenceHeight"] = featuresinfo["referenceHeight"]
            if regiondata["analyticType"] == 212:
                ZoneListData = {"pointList": [], "analyticType": [212]}
            elif regiondata["analyticType"] == ['212', '425']:
                ZoneListData = {"pointList": [],
                                "analyticType": ['212', '425']}
            ZoneListData["AnalyticsType"] = regiondata["AnalyticsType"]
            ZoneListData["IndexRegion"] = regiondata["IndexRegion"]
            ZoneListData["RegionSpecificName"] = regiondata["RegionSpecificName"]
            ZoneListData["RegionSpecificPriority"] = regiondata["RegionSpecificPriority"]
            points = regiondata["pointList"]
            pointList = {}
            for i in range(len(points)):
                if (i % 2) == 0:
                    pointList["x"] = points[i]
                if (i % 2) != 0:
                    pointList["y"] = points[i]
                    ZoneListData["pointList"].append(pointList)
                    pointList = {}
            ZoneListData["RegionName"] = regiondata["RegionSpecificName"]
            ZoneListData["CompleteFrame"] = regiondata["CompleteFrame"]
            # canvasFilePath = basePath+"/Main/canvas/"+featuresinfo["CameraName"]+".svg"
            canvasFilePath = svgPath
            if (os.path.isfile(canvasFilePath) == True):
                with open(canvasFilePath) as f:
                    svgdata = f.read()
            else:
                svgdata = ""
            FeatureData["linesOnCanvas"] = svgdata
            FeatureData["zoneList"].append(ZoneListData)

        # vehicle counting feature
        elif (regiondata["analyticType"] == 409):
            FeatureData["CameraName"] = featuresinfo["CameraName"]
            FeatureData["referenceWidth"] = featuresinfo["referenceWidth"]
            FeatureData["referenceHeight"] = featuresinfo["referenceHeight"]
            ZoneListData = {"TripwireRefPoint": {"x": 0, "y": 0},
                            "pointList": [], "analyticType": [409]}
            ZoneListData["AnalyticsType"] = regiondata["AnalyticsType"]
            ZoneListData["Alert_Counting_string"] = regiondata["Alert_Counting_string"]
            ZoneListData["VCEntryEdgesList"] = regiondata["VCEntryEdgesList"]
            ZoneListData["VCExitEdgesList"] = regiondata["VCExitEdgesList"]
            ZoneListData["VehicleCountingMethod"] = regiondata["VehicleCountingMethod"]
            ZoneListData["EnableVehicleCounting"] = regiondata["EnableVehicleCounting"]
            ZoneListData["IndexRegion"] = regiondata["IndexRegion"]
            ZoneListData["RegionName"] = regiondata["RegionSpecificName"]
            ZoneListData["RegionSpecificName"] = regiondata["RegionSpecificName"]
            ZoneListData["RegionSpecificPriority"] = regiondata["RegionSpecificPriority"]
            ZoneListData["TripwireDirection"] = regiondata["TripwireDirection"]
            ZoneListData["TripwireLineType"] = regiondata["TripwireLineType"]
            RefPoint = regiondata["TripwireRefPoint"]
            ZoneListData["TripwireRefPoint"]["x"] = RefPoint[0]
            ZoneListData["TripwireRefPoint"]["y"] = RefPoint[1]
            points = regiondata["pointList"]
            pointList = {}
            for j in range(len(points)):
                if (j % 2) == 0:
                    pointList["x"] = points[j]
                if (j % 2) != 0:
                    pointList["y"] = points[j]
                    ZoneListData["pointList"].append(pointList)
                    pointList = {}
            # canvasFilePath = basePath+"/Main/canvas/"+featuresinfo["CameraName"]+".svg"
            canvasFilePath = svgPath
            if (os.path.isfile(canvasFilePath) == True):
                with open(canvasFilePath) as f:
                    svgdata = f.read()
            else:
                svgdata = ""
            FeatureData["linesOnCanvas"] = svgdata
            FeatureData["zoneList"].append(ZoneListData)

        # illegal parking feature
        elif (regiondata["analyticType"] == 220):
            FeatureData["CameraName"] = featuresinfo["CameraName"]
            FeatureData["referenceWidth"] = featuresinfo["referenceWidth"]
            FeatureData["referenceHeight"] = featuresinfo["referenceHeight"]
            ZoneListData = {"pointList": [], "analyticType": [220]}
            ZoneListData["IllegalParkingMethod"] = regiondata["IllegalParkingMethod"]
            ZoneListData["IllegalParkingSensitivity"] = regiondata["IllegalParkingSensitivity"]
            ZoneListData["IllegalParkingTimeMin"] = regiondata["IllegalParkingTimeMin"]
            ZoneListData["IndexRegion"] = regiondata["IndexRegion"]
            ZoneListData["RegionName"] = regiondata["RegionSpecificName"]
            ZoneListData["RegionSpecificName"] = regiondata["RegionSpecificName"]
            ZoneListData["RegionSpecificPriority"] = regiondata["RegionSpecificPriority"]
            points = regiondata["pointList"]
            pointList = {}
            for i in range(len(points)):
                if (i % 2) == 0:
                    pointList["x"] = points[i]
                if (i % 2) != 0:
                    pointList["y"] = points[i]
                    ZoneListData["pointList"].append(pointList)
                    pointList = {}

            ZoneListData["CompleteFrame"] = regiondata["CompleteFrame"]
            # canvasFilePath = basePath+"/Main/canvas/"+featuresinfo["CameraName"]+".svg"
            canvasFilePath = svgPath
            if (os.path.isfile(canvasFilePath) == True):
                with open(canvasFilePath) as f:
                    svgdata = f.read()
            else:
                svgdata = ""
            FeatureData["linesOnCanvas"] = svgdata
            FeatureData["zoneList"].append(ZoneListData)

        # vehicle congestion feature
        elif (regiondata["analyticType"] == 224):
            FeatureData["CameraName"] = featuresinfo["CameraName"]
            FeatureData["referenceWidth"] = featuresinfo["referenceWidth"]
            FeatureData["referenceHeight"] = featuresinfo["referenceHeight"]
            ZoneListData = {"pointList": [], "analyticType": [224]}
            ZoneListData["Alert_Congestion_string"] = regiondata["Alert_Congestion_string"]
            ZoneListData["TrafficCongestionAlarmInterval"] = regiondata["TrafficCongestionAlarmInterval"]
            ZoneListData["TrafficCongestionMethod"] = regiondata["TrafficCongestionMethod"]
            ZoneListData["TrafficCongestionRefreshInterval"] = regiondata["TrafficCongestionRefreshInterval"]
            ZoneListData["CrowdCapacityMax"] = regiondata["CrowdCapacityMax"]
            ZoneListData["CrowdCapacityMin"] = regiondata["CrowdCapacityMin"]
            ZoneListData["IndexRegion"] = regiondata["IndexRegion"]
            ZoneListData["RegionName"] = regiondata["RegionSpecificName"]
            ZoneListData["RegionSpecificName"] = regiondata["RegionSpecificName"]
            ZoneListData["RegionSpecificPriority"] = regiondata["RegionSpecificPriority"]
            points = regiondata["pointList"]
            pointList = {}
            for i in range(len(points)):
                if (i % 2) == 0:
                    pointList["x"] = points[i]
                if (i % 2) != 0:
                    pointList["y"] = points[i]
                    ZoneListData["pointList"].append(pointList)
                    pointList = {}

            ZoneListData["CompleteFrame"] = regiondata["CompleteFrame"]
            # canvasFilePath = basePath+"/Main/canvas/"+featuresinfo["CameraName"]+".svg"
            canvasFilePath = svgPath
            if (os.path.isfile(canvasFilePath) == True):
                with open(canvasFilePath) as f:
                    svgdata = f.read()
            else:
                svgdata = ""
            FeatureData["linesOnCanvas"] = svgdata
            FeatureData["zoneList"].append(ZoneListData)

        # wrong way detection feature
        elif (regiondata["analyticType"] == 410):
            FeatureData["CameraName"] = featuresinfo["CameraName"]
            FeatureData["referenceWidth"] = featuresinfo["referenceWidth"]
            FeatureData["referenceHeight"] = featuresinfo["referenceHeight"]
            ZoneListData = {"WrongwayPoints": [],
                            "pointList": [], "analyticType": [410]}
            ZoneListData["Alert_Wrongway_string"] = regiondata["Alert_Wrongway_string"]
            ZoneListData["WrongwayDirection"] = regiondata["WrongwayDirection"]
            ZoneListData["WrongwayTolerance"] = regiondata["WrongwayTolerance"]
            ZoneListData["IndexRegion"] = regiondata["IndexRegion"]
            ZoneListData["RegionSpecificName"] = regiondata["RegionSpecificName"]
            ZoneListData["RegionSpecificPriority"] = regiondata["RegionSpecificPriority"]
            ZoneListData["RegionName"] = regiondata["RegionSpecificName"]
            wwdPoints = regiondata["WrongwayPoints"]
            wwdPointList = {}
            for i in range(len(wwdPoints)):
                if (i % 2) == 0:
                    wwdPointList["x"] = wwdPoints[i]
                if (i % 2) != 0:
                    wwdPointList["y"] = wwdPoints[i]
                    ZoneListData["WrongwayPoints"].append(wwdPointList)
                    wwdPointList = {}

            points = regiondata["pointList"]
            pointList = {}
            for j in range(len(points)):
                if (j % 2) == 0:
                    pointList["x"] = points[j]
                if (j % 2) != 0:
                    pointList["y"] = points[j]
                    ZoneListData["pointList"].append(pointList)
                    pointList = {}
            ZoneListData["CompleteFrame"] = regiondata["CompleteFrame"]
            # canvasFilePath = basePath+"/Main/canvas/"+featuresinfo["CameraName"]+".svg"
            canvasFilePath = svgPath
            if (os.path.isfile(canvasFilePath) == True):
                with open(canvasFilePath) as f:
                    svgdata = f.read()
            else:
                svgdata = ""
            FeatureData["linesOnCanvas"] = svgdata
            FeatureData["zoneList"].append(ZoneListData)

        response = self.session.post(self.geturl_ChannelFunctions(
            SiteID, ChannelID), data=json.dumps(FeatureData), headers=self.getheader(), verify=False)
        if (response.status_code == 200):
            # features enabled
            logging.info('Features enabled to channelID '+str(ChannelID))
            content = json.loads(response.content)
            return content["code"]
        else:
            logging.error('Enabling features to channelID ' +
                          str(ChannelID)+' failed')
            raise Exception('Enabling features to channelID ' +
                            str(ChannelID)+' failed')
            return False

    # To run analytics
    def run_analytics(self, runanalyticsinfo, SiteID):
        response = self.session.post(self.geturlRunStopAnalytics("runanalytics", SiteID), data=json.dumps(
            runanalyticsinfo), headers=self.getheader(), verify=False)
        if (response.status_code == 200):
            content = json.loads(response.content)
            return content["code"]

        else:
            # logging.error('Starting analytics to channelID '+str(runanalyticsinfo["channelid"])+' failed')
            # raise Exception('Starting analytics to channelID '+str(runanalyticsinfo["channelid"])+' failed')
            return False

    # To stop already running analytics on given channel
    def stop_analytics(self, stopanalyticsinfo, SiteID):
        response = self.session.post(self.geturlRunStopAnalytics("stopanalytics", SiteID), data=json.dumps(
            stopanalyticsinfo), headers=self.getheader(), verify=False)
        if (response.status_code == 200):
            content = json.loads(response.content)
            return content["code"]
        else:

            # logging.error('Analytics failed to stop for channelID '+str(stopanalyticsinfo["channelid"]))
            # raise Exception('Analytics failed to stop for channelID '+str(stopanalyticsinfo["channelid"]))
            return False

    # To save general setup configuration on particular channel
    def save_general_setup(self, generalsetupinfo, SiteID, ChannelID):
        response = self.session.post(self.geturl_ChannelFunctions(SiteID, ChannelID), data=json.dumps(
            generalsetupinfo), headers=self.getheader(), verify=False)
        if (response.status_code == 200):
            logging.info('General setup saved for channelID '+str(ChannelID))
            content = json.loads(response.content)
        else:
            logging.error('General setup failed for channelID '+str(ChannelID))
            raise Exception(
                'General setup failed for channelID '+str(ChannelID))

    # To save advanced setup configuration on particular channel
    def save_advanced_setup(self, advancedsetupinfo, SiteID, ChannelID):
        response = self.session.post(self.geturl_ChannelFunctions(SiteID, ChannelID), data=json.dumps(
            advancedsetupinfo), headers=self.getheader(), verify=False)
        if (response.status_code == 200):
            logging.info('Advance setup saved for channelID '+str(ChannelID))
            content = json.loads(response.content)
        else:
            logging.error('Advance setup failed for channelID '+str(ChannelID))
            raise Exception(
                'Advance setup failed for channelID '+str(ChannelID))

    # Gets all onvif camera info
    def getOnvifCamera(self, searchchannelinfo):
        response = self.session.post(self.geturl("searchchannel"), data=json.dumps(
            searchchannelinfo), headers=self.getheader(), verify=False)
        if (response.status_code == 200):
            logging.info('Onvif cameras fetched successfully')
            content = json.loads((response.content).decode())
            return content["result"]
        else:
            logging.error('Onvif search failed')
            raise Exception('Onvif search failed')
            content = json.loads(response.content)
            return False

    # adds onvif camera
    def addOnvifCamera(self, OnvifCameraInfo):
        response = self.session.post(self.geturl("addonvifcamera"), data=json.dumps(
            OnvifCameraInfo), headers=self.getheader(), verify=False)
        if (response.status_code == 200):
            content = json.loads((response.content).decode())
            camera_id = content["result"]["id"]
            logging.info('Onvif channel '+str(
                OnvifCameraInfo["name"])+' added successfully and channelID is '+str(camera_id))
        else:
            logging.error('Onvif channel ' +
                          str(OnvifCameraInfo["name"])+' addition failed')
            raise Exception('Onvif channel ' +
                            str(OnvifCameraInfo["name"])+' addition failed')
            content = json.loads((response.content).decode())
            camera_id = None

        return camera_id

    # gets profile of onvif type of cameras
    def getProfile(self, getprofileinfo):
        response = self.session.post(self.geturl("getprofile"), data=json.dumps(
            getprofileinfo), headers=self.getheader(), verify=False)
        if (response.status_code == 200):
            logging.info(
                'Connection successful and profiles fetched successfully')
            content = json.loads((response.content).decode())
            return content["result"]
        else:
            logging.error('Connection failed')
            raise Exception('Connection failed')
            content = json.loads((response.content).decode())
            return False

    # adds server
    def addServer(self, serverinfo):
        response = self.session.post(self.geturl("addserver"), data=json.dumps(
            serverinfo), headers=self.getheader(), verify=False)
        if (response.status_code == 200):
            logging.info(serverinfo["name"]+' server added')
            content = json.loads(response.content)
            return content["result"][0]["id"]
        else:
            logging.error(serverinfo["name"]+' server addition failed')
            raise Exception(serverinfo["name"]+' server addition failed')
            content = json.loads(response.content)
            return False

    # starts fr server
    def startFRServer(self, ip):
        response = requests.get(
            "http://" + ip + ":9020/api/v1/callFRServer?flag=1")
        if (response.status_code == 200):
            logging.info('FR server started')
            content = json.loads(response.content)
        else:
            logging.error('FR server failed')
            raise Exception('FR server failed')
            return False

    # gets the server status
    def getPingServer(self, ip, port):
        response = self.session.get(self.geturlPingServer(
            ip, port), data=None, headers=self.getheader(), verify=False)
        if (response.status_code == 200):
            logging.info('Server with '+str(ip)+' is reachable')
            content = json.loads(response.content)
            return content["code"]
        else:
            logging.error('Server with '+str(ip)+' is not reachable')
            content = json.loads(response.content)
            return content["code"]

    # gets server settings config
    def getConfig(self):
        response = self.session.get(self.geturl(
            "config"), data=None, headers=self.getheader(), verify=False)
        if (response.status_code == 200):
            logging.info('Server Settings fetched successfully')
            content = json.loads(response.content)
            return content["result"]
        else:
            logging.error('Unable to get server settings')
            raise Exception('Unable to get server settings')
            return False

    # sets server settings
    def postConfig(self, configInfo):
        response = self.session.post(self.geturl("config"), data=json.dumps(
            configInfo), headers=self.getheader(), verify=False)
        if (response.status_code == 200):
            logging.info('Updated Server Settings')
            content = json.loads((response.content))
            return content["result"]
        else:
            logging.error('Failed to update server settings')
            raise Exception('Failed to update server settings')
            return False

    # Gets the oc server config from 9050 port
    def ocGetConfig(self, ip):
        response = requests.get(
            "http://"+str(ip)+":9050/api/v1/getConfigDetails")
        if (response.status_code == 200):
            content = json.loads(response.content)
            return content
        else:
            logging.error(response.content)
            raise Exception(response.content)
            return None

    # gets the modules/files added for OC server
    def ocGetFileList(self, ip):
        response = requests.get("http://"+str(ip)+":9050/api/v1/getFileList")
        if (response.status_code == 200):
            content = json.loads(response.content)
            return content
        else:
            logging.error(response.content)
            raise Exception(response.content)
            return None

    def ocGetHeader(self):
        header = {'Content-type': 'application/x-www-form-urlencoded'}
        return header

    # Saving OC server's config
    def ocSaveConfig(self, ip, payload):
        response = requests.post("http://"+str(ip)+":9050/api/v1/saveConfig",
                                 data=payload, headers=self.ocGetHeader(), verify=False)
        if (response.status_code == 200):
            logging.info('OC Config saved successfully')
        else:
            logging.error('OC Config saving failed')
            raise Exception('OC Config saving failed')

    # Stops OC server
    def ocStopServer(self, ip):
        response = requests.get(
            "http://"+str(ip)+":9050/api/v1/callOCServer?flag=0")
        if (response.status_code == 200):
            logging.info('OC Server stopped successfully')
        else:
            logging.error('OC Server failed to stop')
            raise Exception('OC Server failed to stop')

    # Starts OC server
    def ocStartServer(self, ip, port):
        logging.info('Starting OC server .............')
        response = requests.get(
            "http://"+str(ip)+":9050/api/v1/callOCServer?flag=1&ip="+str(ip)+"&port="+str(port))
        if (response.status_code == 200):
            logging.info('OC Server started and is reachable')
        else:
            logging.error('OC Server failed and is not reachable')
            raise Exception('OC Server failed and is not reachable')

    # Gets vms list
    def getVmsList(self):
        response = self.session.get(self.geturl(
            "getVmsList"), data=None, headers=self.getheader(), verify=False)
        if (response.status_code == 200):
            logging.info('VmsInfo fetched successful')
            content = json.loads(response.content)
            return (content["result"])
        else:
            logging.error('VMS Connection failed')
            raise Exception('VMS Connection failed')

    # add vms
    def addVms(self, addVmsInfo):
        response = self.session.post(self.geturl("addVms"), data=json.dumps(
            addVmsInfo), headers=self.getheader(), verify=False)
        if (response.status_code == 200):
            content = json.loads(response.content)
            logging.info('VMS added successfully')
            return content["result"]["VmsID"][0]
        else:
            logging.error('VMS addition failed')
            raise Exception('VMS addition failed')

    # Connect vms
    def addConnectVms(self, VmsID, connectVmsInfo):
        response = self.session.post(self.geturlConnectVms(VmsID), data=json.dumps(
            connectVmsInfo), headers=self.getheader(), verify=False)
        if (response.status_code == 200):
            content = json.loads(response.content)
            return content["result"]["Status"]
        else:
            logging.error('VMS connection failed')
            raise Exception('VMS connection failed')

    # gets cameras available in vms
    def getVmsCameraList(self, VmsID):
        response = self.session.get(self.geturlVmsCameraList(
            VmsID), data=None, headers=self.getheader(), verify=False)
        if (response.status_code == 200):
            logging.info('CameraList fetched successfully from VMS')
            content = json.loads(response.content)
            return (content["result"])
        else:
            logging.error('Getting CameraList from VMS failed')
            raise Exception('Getting CameraList from VMS failed')

    # add vms camera
    def addVmsCamera(self, VmsCameraInfo):
        response = self.session.post(self.geturl("addVmsCamera"), data=json.dumps(
            VmsCameraInfo), headers=self.getheader(), verify=False)
        if (response.status_code == 200):
            content = json.loads((response.content).decode())
            logging.info(
                'VMS Camera '+str(VmsCameraInfo["model"])+' added successfully and channelID is '+str(content["result"]["id"]))
            return content["result"]["id"]
        else:
            logging.error(
                'VMS Camera '+str(VmsCameraInfo["model"])+' addition failed')
            # raise Exception('VMS Camera '+str(VmsCameraInfo["model"])+' addition failed')
            return None

    # gets vms info
    def getVms(self):
        response = self.session.get(self.geturl(
            "getVms"), data=None, headers=self.getheader(), verify=False)
        if (response.status_code == 200):
            logging.info("Vms info fetched successfully")
            content = json.loads(response.content)
            return content["result"]
        else:
            logging.error("Unable to get Vms info")
            raise Exception("Unable to get Vms info")
            return False

    # Authenticate DVM vms
    def authenticateDvm(self, aunthenticateDvmInfo):
        response = self.session.post(self.geturl("authenticateDvm"), data=json.dumps(
            aunthenticateDvmInfo), headers=self.getheader(), verify=False)
        if (response.status_code == 200):
            logging.info("DVM vms authentication successful")
        else:
            logging.error("DVM vms connection failed")
            raise Exception("DVM vms connection failed")

    # Saving vms
    def saveVms(self, saveVmsInfo):
        response = self.session.post(self.geturl("saveVms"), data=json.dumps(
            saveVmsInfo), headers=self.getheader(), verify=False)
        if (response.status_code == 200):
            logging.info("Successfully Saved Vms")
            content = json.loads((response.content).decode())
            return content["result"]["id"]
        else:
            logging.error("Vms saving failed")
            raise Exception("Vms saving failed")
            return None

    # Connect DVM
    def connectDvm(self, connectVmsInfo):
        response = self.session.post(self.geturl("connectDvm"), data=json.dumps(
            connectVmsInfo), headers=self.getheader(), verify=False)
        if (response.status_code == 200):
            logging.error("Successfully connectecd DVM")
            content = json.loads((response.content).decode())
            return content["result"]
        else:
            logging.error("DVM connection failed")
            raise Exception("DVM connection failed")
            return False

    # Function to create an enterprise account
    # If successful, the function returns enterprise_id
    # If failure, function returns Status Code
    def create_enterprise(self, enterprisedata):
        # Create an enterprise account
        response = self.session.post(self.geturl("createenterprise"), data=json.dumps(
            enterprisedata), headers=self.getheader(), verify=False)
        if (response.status_code == 200):
            logging.info(
                'Enterprise '+enterprisedata["name"]+' creation successful')
            content = json.loads(response.content)
            enterprise_id = content["result"][0]["id"]
        else:
            logging.error(
                'Enterprise '+enterprisedata["name"]+' creation failed')
            raise Exception(
                'Enterprise '+enterprisedata["name"]+' creation failed')
            content = json.loads(response.content)
            enterprise_id = None

        return enterprise_id, content

    # Gets enterprise info
    def getEnterprise(self):
        response = self.session.get(self.geturl(
            "createenterprise"), data=None, headers=self.getheader(), verify=False)
        if (response.status_code == 200):
            logging.info('Enterprise info fetched successfully')
            content = json.loads(response.content)
            return (content["result"])
        else:
            logging.error('Unable to get Enterprise info')
            raise Exception('Unable to get Enterprise info')
            return False

    # link user with site
    def linkuserandsite(self, userid, siteid):
        body = {"userid": userid, "siteid": [siteid]}
        response = self.session.post(self.geturl("linkuserandsite"), data=json.dumps(
            body), headers=self.getheader(), verify=False)
        if (response.status_code == 200):
            content = json.loads(response.content)
            return True
        else:
            content = json.loads(response.content)
            return False

    # links enterprise with site
    def linkenterpriseandsite(self, enterpriseid, siteid):
        body = {"siteid": siteid}
        url = self.geturl("createenterprise") + "/" + \
            str(enterpriseid) + "/site"
        response = self.session.post(url, data=json.dumps(
            body), headers=self.getheader(), verify=False)
        content = json.loads(response.request)

    # create and add user
    def create_user(self, info):
        userinfo = info.copy()
        # Encrypt the password
        userinfo["password"] = configSession.encryptpassword(
            userinfo["firsttimepassword"])

        # Make the Request
        response = self.session.post(self.geturl("createuser"), data=json.dumps(
            userinfo), headers=self.getheader(), verify=False)

        # Check the response
        if (response.status_code == 200):
            # User Creation is successful
            content = json.loads(response.content)
            userid = content["result"]["userId"]
        else:
            # User creation has failed
            content = json.loads(response.content)
            userid = None

        return userid

    # gets all users
    def getUsers(self):
        response = self.session.get(self.geturl(
            "createuser"), data=None, headers=self.getheader(), verify=False)
        if (response.status_code == 200):
            logging.info('Users info fetched successfully')
            content = json.loads(response.content)
            return (content["result"])
        else:
            logging.error('Unable to get Users info')
            raise Exception('Unable to get Users info')
            return False

    # gets specific user
    def getSpecificUser(self, userid):
        response = self.session.get(self.geturlUser(
            userid), data=None, headers=self.getheader(), verify=False)
        if (response.status_code == 200):
            logging.info('User info fetched successfully')
            content = json.loads(response.content)
            return (content["result"])
        else:
            logging.error('Unable to get User info')
            raise Exception('Unable to get User info')
            return False

    # adds and create site
    def create_site(self, siteinfo):
        url = self.baseurl + api_url["site"]
        response = self.session.post(url, data=json.dumps(
            siteinfo), headers=self.getheader(), verify=False)
        if (response.status_code == 200):
            content = json.loads(response.content)
            siteid = content["result"][0]["id"]
        else:
            content = json.loads(response.content)
            siteid = None

        return siteid

    # Delete user
    def delete_user(self, userid):
        url = self.baseurl + api_url["createuser"] + "/" + str(userid)
        response = self.session.delete(
            url, headers=self.getheader(), verify=False)
        content = json.loads(response.content)

    # delete site
    def delete_site(self, siteid):
        url = self.baseurl + api_url["site"] + "/" + str(siteid)
        response = self.session.delete(
            url, headers=self.getheader(), verify=False)
        content = json.loads(response.content)
