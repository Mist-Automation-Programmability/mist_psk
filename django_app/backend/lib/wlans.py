import requests
import json

from .common import Common

class Wlan(Common):

    def pull(self, body):
        body = self.get_body(body)    
        if "site_id" in body :           
            try: 
                site_id = body["site_id"]
                extract = self.extractAuth(body)
                url = "https://{0}/api/v1/sites/{1}/wlans".format(extract["host"], site_id)
                resp = requests.get(url, headers=extract["headers"], cookies=extract["cookies"])  
                wlans = []
                for wlan in resp.json():
                    if wlan['auth']["type"] == "psk":
                        if wlan["auth"]["multi_psk_only"] == True:
                            wlans.append({"id": wlan["id"], "ssid": wlan["ssid"]})
                return {"status": 200, "data": {"wlans": wlans}}
            except:
                return {"status": 500, "data": {"error": "unable to retrieve the WLANs list"}}
        else:
            return {"status":500, "data":{"error": "site_id missing"}}