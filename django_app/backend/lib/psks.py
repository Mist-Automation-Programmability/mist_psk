
import requests
import json
from .common import Common


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
                        url = "https://{0}/api/v1/{1}/{2}/psks?limit={3}&page={4}".format(
                            extract["host"], scope_name, scope_id, limit, page)
                        if "ssid" in body and body["ssid"]:
                            url += "&ssid={0}".format(body["ssid"])
                        resp=requests.get(
                            url, headers = extract["headers"], cookies = extract["cookies"])
                        results.extend(resp.json())
                        total=resp.headers["X-Page-Total"]
                        page += 1
                    return {"status": 200, "data": {"total": total, "results": results}}

                else:
                    limit=body["limit"] if "limit" in body else 100
                    page=body["page"] + 1 if "page" in body else 1
                    url="https://{0}/api/v1/{1}/{2}/psks?limit={3}&page={4}".format(
                        extract["host"], scope_name, scope_id, limit, page)
                    if "ssid" in body and body["ssid"]:
                        url += "&ssid={0}".format(body["ssid"])
                    resp = requests.get(
                        url, headers=extract["headers"], cookies=extract["cookies"])
                    return {"status": 200, "data": {"page": resp.headers["X-Page-Page"], "limit": resp.headers["X-Page-limit"], "total": resp.headers["X-Page-Total"], "results": resp.json()}}
            except:
                return {"status": 500, "data": {"message": "Unable to retrieve the PSKs list"}}
        else:
            return {"status": 500, "data": {"message": "missing parameters in the request"}}


#############
# Create or Edit PSK
#############

    def push(self, body):
        body = self.get_body(body)
        if "site_id" in body:
            return self._push_psk(body, "sites", "site_id")
        elif "org_id" in body:
            return self._push_psk(body, "orgs", "org_id")
        else:
            return {"status": 500, "data": {"message": "site_id or org_id missing"}}

    def _push_psk(self, body, scope_name, scope_id_param):
        if scope_id_param in body and "name" in body and "passphrase" in body and "ssid" in body:
            psk = {
                "name": body["name"],
                "passphrase": body["passphrase"],
                "ssid": body["ssid"],
                "usage": "multi",
            }
            if "vlan_id" in body:
                psk["vlan_id"] = body["vlan_id"]
            if "created_by" in body:
                psk["created_by"] = body["created_by"]
            if "user_email" in body:
                psk["user_email"] = body["user_email"]
            if "id" in body:
                return self._updatePsk(body, body["id"], psk, scope_name, scope_id_param)
            else:
                return self._createPsk(body, psk, scope_name, scope_id_param)

    def _createPsk(self, body, psk, scope_name, scope_id_param):
        extract = self.extractAuth(body)
        try:
            url = "https://{0}/api/v1/{1}/{2}/psks".format(
                body["host"], scope_name, body[scope_id_param])
            resp = requests.post(
                url, headers=extract["headers"], cookies=extract["cookies"], json=psk)
            return {"status": 200, "data": {"results": resp.json()}}
        except:
            return {"status": 500, "data": {"message": "Unable to update the Psk"}}

    def _updatePsk(self, body, psk_id, psk, scope_name, scope_id_param):
        extract = self.extractAuth(body)
        try:
            url = "https://{0}/api/v1/{1}/{2}/psks/{3}".format(
                body["host"], scope_name, body[scope_id_param], body["id"])
            resp = requests.put(
                url, headers=extract["headers"], cookies=extract["cookies"], json=psk)
            return {"status": 200, "data": {"results": resp.json()}}
        except:
            return {"status": 500, "data": {"message": "Unable to create the Psk"}}

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
                url = "https://{0}/api/v1/{1}/{2}/psks/{3}".format(
                    body["host"], scope_name, body[scope_id_param], body["psk_id"])
                resp = requests.delete(
                    url, headers=extract["headers"], cookies=extract["cookies"])
                return {"status": 200, "data": {"result": resp.json()}}
            except:
                return {"status": 500, "data": {"message": "unable to delete the psk"}}

        else:
            return {"status": 500, "data": {"message": "psk_id is missing"}}
