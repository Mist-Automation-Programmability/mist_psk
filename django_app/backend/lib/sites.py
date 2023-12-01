'''
-------------------------------------------------------------------------------

    Written by Thomas Munzer (tmunzer@juniper.net)
    Github repository: 
    https://github.com/Mist-Automation-Programmability/mist_psk

    This script is licensed under the MIT License.

-------------------------------------------------------------------------------
'''
import requests

from .common import Common

class Sites(Common):

    def pull(self, body):
        body = self.get_body(body)
        if "host" in body and "headers" in body and "cookies" in body and "org_id" in body:
            try: 
                url = f"https://{body['host']}/api/v1/orgs/{body['org_id']}/sites"
                resp = requests.get(url, headers=body["headers"], cookies=body["cookies"])
                return {"status": 200, "data": {"sites": resp.json()}}
            except:
                return {"status": 500, "data": {"message": "unable to retrieve the Sites list"}}
        else:
            return {"status":500, "data":{"message": "Information missing"}}