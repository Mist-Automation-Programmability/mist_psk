import requests
import json

from .common import Common

class Orgs(Common):

    def pull(self, body):
        body = self.get_body(body)    
        if "host" in body and "headers" in body and "cookies" in body and "msp_id" in body:
            #try: 
                url = f"https://{body['host']}/api/v1/msps/{body['msp_id']}/orgs"
                resp = requests.get(url, headers=body["headers"], cookies=body["cookies"])                
                return {"status": 200, "data": {"orgs": resp.json()}}
            # except:
            #     return {"status": 500, "data": {"message": "unable to retrieve the Org list"}}
        else:
            return {"status":500, "data":{"message": "Information missing"}}