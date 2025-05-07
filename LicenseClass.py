import json
import logging
import os.path
from telnetlib import STATUS


class License:

    def __init__(self, licenseDir, configInfo):
        self.licenseDir = licenseDir
        self.dictionary = configInfo["License"]
        self.payload = {"licenses": []}
        if (os.listdir(self.licenseDir)):
            for i in os.listdir(self.licenseDir):
                with open(self.licenseDir+"/"+i) as json_file:
                    licData = json.load(json_file)
                    for j in range(len(licData["licenses"])):
                        self.payload["licenses"].append(licData["licenses"][j])
        else:
            self.payload = []
            logging.error('No license file found')
            raise Exception('No license file found')

        payloadDump = json.dumps(self.payload, sort_keys=False, indent=4)
        with open(self.licenseDir+"/allLicense.json", 'w', encoding='utf-8') as f:
            f.write(payloadDump)

    def getPayload(self):
        data = {
            "licenses": json.dumps(self.payload)
        }
        return data

    # gets license info from server
    def getLicenseConfig(self, cfsession):
        licenseData = cfsession.getlicenseconfig()
        if (licenseData == []):
            licenses = []
        else:
            licenses = []
            for i in range(len(licenseData)):
                licensesdata = {}
                licensesdata["licenseID"] = licenseData[i]["id"]
                licensesdata["Available Features"] = []
                features = str(licenseData[i]["availableFeatures"]).split(",")

                for j in range(len(features)):
                    licensesdata["Available Features"].append(features[j])
                licensesdata["Available Features"].sort()
                licensesdata["enterpriseId"] = licenseData[i]["enterpriseId"]
                licensesdata["ChannelLicense"] = licenseData[i]["ChannelLicense"]
                if (licenseData[i]["ChannelLicense"] != None):
                    licensesdata["status"] = "Mapped"
                else:
                    licensesdata["status"] = "Not Mapped"

                licenses.append(licensesdata)

        return licenses

    # Adds license
    def config(self, cfsession, licenseInfo):
        cfsession.add_license(licenseInfo)

        code = cfsession.add_license(licenseInfo)
        if (code == 200):
            logging.info('License added successfully')

        else:
            logging.info('License addition failed')
        self.dictionary = self.getLicenseConfig(cfsession)

    # maps the lecnese with channel
    def mapLicense(self, cfsession, channelList):

        linID = None
        for j in range(len(self.dictionary)):
            if (self.dictionary[j]["status"] == "Not Mapped"):
                channelFeatures = []
                for f in channelList["Features"]:
                    if (f == "Face Recognition"):
                        channelFeatures = ["Face Capture", "Face Detection",
                                           "Face Forensic Analysis", "Face Recognition", "Face Verification"]
                    elif (f == "Left Baggage Detection"):
                        channelFeatures = ["Left Object Detection"]
                    elif (f == "Camera Tampering"):
                        channelFeatures = [
                            "Camera Tampering", "Video Loss Alarm"]
                    else:
                        channelFeatures = channelList["Features"]

                if (len(self.dictionary[j]["Available Features"]) == len(channelFeatures)):
                    if (self.dictionary[j]["Available Features"] == channelFeatures):
                        # print(channelList["cameraid"])
                        # print(self.dictionary[j]["licenseID"])
                        code = cfsession.mapLicense(
                            self.dictionary[j]["licenseID"], channelList["cameraid"])
                        if (code == 200):
                            self.dictionary[j]["status"] = "Mapped"
                            self.dictionary[j]["ChannelLicense"] = {
                                "id": channelList["cameraid"], "name": channelList["Name"], "siteId": channelList["siteId"]}
                            self.commit()
                            return self.dictionary[j]["licenseID"]

        return None

    # return self.dictionary
    def commit(self):
        return self.dictionary
