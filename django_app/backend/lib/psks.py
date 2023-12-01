'''
-------------------------------------------------------------------------------

    Written by Thomas Munzer (tmunzer@juniper.net)
    Github repository: 
    https://github.com/Mist-Automation-Programmability/mist_psk

    This script is licensed under the MIT License.

-------------------------------------------------------------------------------
'''

import requests
import bcrypt
from .common import Common
from .wlans import Wlan

class Psk(Common):

    #############
    # get PSKs from Cloud
    #############
    def pull(self, body):
        body = self.get_body(body)
        if "site_id" in body:
            return self._pull_psks(body, "sites", "site_id")
        elif "org_id" in body:
            return self._pull_psks(body, "orgs", "org_id")
        else:
            return {"status": 500, "data": {"message": "site_id or org_id missing"}}

    def _pull_psks(self, body, scope_name, scope_id_param):
        if scope_id_param in body:
            scope_id = body[scope_id_param]
            try:
                extract = self.extractAuth(body)
                if "full" in body and body["full"]:
                    limit = 1000
                    page = 1
                    results = []
                    total = 1
                    while len(results) < int(total) and int(page) < 50:
                        url=f"https://{extract['host']}/api/v1/{scope_name}/{scope_id}/psks?limit={limit}&page={page}"
                        if "ssid" in body and body["ssid"]:
                            url += f"&ssid={body['ssid']}"
                        resp=requests.get(
                            url, headers = extract["headers"], cookies = extract["cookies"])
                        results.extend(resp.json())
                        total=resp.headers["X-Page-Total"]
                        page += 1
                    return {"status": 200, "data": {"total": total, "results": results}}

                else:
                    limit=body["limit"] if "limit" in body else 100
                    page=body["page"] + 1 if "page" in body else 1
                    url=f"https://{extract['host']}/api/v1/{scope_name}/{scope_id}/psks?limit={limit}&page={page}"
                    if "ssid" in body and body["ssid"]:
                        url += f"&ssid={body['ssid']}"
                    resp = requests.get(
                        url, headers=extract["headers"], cookies=extract["cookies"])
                    return {
                        "status": 200,
                        "data": {
                            "page": resp.headers["X-Page-Page"],
                            "limit": resp.headers["X-Page-limit"],
                            "total": resp.headers["X-Page-Total"],
                            "results": resp.json()
                            }
                            }
            except:
                return {"status": 500, "data": {"message": "Unable to retrieve the PSKs list"}}
        else:
            return {"status": 500, "data": {"message": "missing parameters in the request"}}


#############
# Create or Edit PSK
#############

    def push(self, body, psk_config):
        body = self.get_body(body)
        if "site_id" in body:
            return self._push_psk(body, "sites", "site_id", psk_config)
        elif "org_id" in body:
            return self._push_psk(body, "orgs", "org_id", psk_config)
        else:
            return {"status": 500, "data": {"message": "site_id or org_id missing"}}

    def _gen_renewable_psk(self, username, scope_id, psk_config):
        salt = psk_config["salt"]
        psk_length = psk_config["length"]
        passwd = f"{scope_id}_{username}"
        passwd = str(passwd).encode()
        # generate the hash in bytes
        psk = bcrypt.hashpw(passwd, salt)
        # convert bytes to utf-8
        psk = psk.decode("utf-8")
        # get a substr of the psk to match the length
        if psk_length > len(psk): 
            psk_length = len(psk)
        psk = psk[len(psk)-psk_length:]
        return psk


    def _push_psk(self, body, scope_name, scope_id_param, psk_config):
        if not scope_id_param in body:
            return {"status": 500, "data": {"message": "scope_id_param missing"}}
        elif not "name" in body:
            return {"status": 500, "data": {"message": "name missing"}}
        elif not "ssid" in body:
            return {"status": 500, "data": {"message": "ssid missing"}}
        else:
            extract = self.extractAuth(body)
            psk = {
                "name": body["name"],
                "passphrase": body.get("passphrase"),
                "ssid": body["ssid"],
                "expire_time": body["expire_time"],
                "usage": "multi",
            }
            if "renewable" in body and body["renewable"]:
                psk["passphrase"] = self._gen_renewable_psk(
                    body["name"],
                    body[scope_id_param],
                    psk_config
                    )
            if "vlan_id" in body:
                psk["vlan_id"] = body["vlan_id"]
            if "created_by" in body:
                psk["created_by"] = body["created_by"]
            if "user_email" in body:
                psk["user_email"] = body["user_email"]
            if body.get("-max_usage"):
                psk["-max_usage"] = True
            elif body.get("max_usage"):
                psk["max_usage"] = body["max_usage"]

            result = {"status": None}
            if "id" in body:
                result =  self._updatePsk(
                    body,
                    extract,
                    body["id"],
                    psk,
                    scope_name,
                    scope_id_param
                    )
            else:
                result =  self._createPsk(body, extract, psk, scope_name, scope_id_param)
            if "vlan_id" in body and result["status"] == 200:
                vlan_check = Wlan().check_vlan(
                    extract,
                    body["ssid"],
                    body["vlan_id"],
                    scope_name,
                    body[scope_id_param]
                    )
                result["data"]["vlan_check"] = vlan_check
            return result

    def _createPsk(self, body, extract, psk, scope_name, scope_id_param):
        try:
            url = f"https://{body['host']}/api/v1/{scope_name}/{body[scope_id_param]}/psks"
            resp = requests.post(
                url, headers=extract["headers"], cookies=extract["cookies"], json=psk)
            return {"status": 200, "data": {"results": resp.json()}}
        except:
            return {"status": 500, "data": {"message": "Unable to create the Psk"}}

    def _updatePsk(self, body, extract, psk_id, psk, scope_name, scope_id_param):
        try:
            url = f"https://{body['host']}/api/v1/{scope_name}/{body[scope_id_param]}/psks/{psk_id}"
            resp = requests.put(
                url, headers=extract["headers"], cookies=extract["cookies"], json=psk)
            return {"status": 200, "data": {"results": resp.json()}}
        except:
            return {"status": 500, "data": {"message": "Unable to update the Psk"}}

#############
# delete PSKs
#############
    def delete(self, body):
        body = self.get_body(body)
        if "site_id" in body:
            return self._delete_psk(body, "sites", "site_id")
        elif "org_id" in body:
            return self._delete_psk(body, "orgs", "org_id")
        else:
            return {"status": 500, "data": {"message": "site_id or org_id missing"}}


    def _delete_psk(self, body, scope_name, scope_id_param):
        extract = self.extractAuth(body)
        if scope_id_param in body and "psk_id" in body:
            try:
                url = f"https://{body['host']}/api/v1/{scope_name}/{body[scope_id_param]}/psks/{body['psk_id']}"
                resp = requests.delete(
                    url, headers=extract["headers"], cookies=extract["cookies"])
                return {"status": 200, "data": {"result": resp.json()}}
            except:
                return {"status": 500, "data": {"message": "unable to delete the psk"}}

        else:
            return {"status": 500, "data": {"message": "psk_id is missing"}}
