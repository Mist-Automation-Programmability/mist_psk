import requests
import json

from .common import Common

class Wlan(Common):

    def _get_wlans(self, body, scope_name, scope_id_param):
        if scope_id_param in body :           
            scope_id = body[scope_id_param]
            extract = self.extractAuth(body)
            try: 
                url = "https://{0}/api/v1/{1}/{2}/wlans".format(extract["host"], scope_name, scope_id)
                resp = requests.get(url, headers=extract["headers"], cookies=extract["cookies"])  
                wlans = []
                for wlan in resp.json():
                    if wlan['auth']["type"] == "psk":
                        if wlan["auth"]["multi_psk_only"] == True:
                            wlans.append({"id": wlan["id"], "ssid": wlan["ssid"]})
                return {"status": 200, "data": {"wlans": wlans}}
            except:
                return {"status": 500, "data": {"message": "unable to retrieve the WLANs list"}}
        else:
            return {"status": 500, "data": {"message": "missing parameters in the request"}}

    def pull(self, body):
        body = self.get_body(body)
        if "site_id" in body:
            return self._get_wlans(body, "sites", "site_id")
        elif "org_id" in body:
            return self._get_wlans(body, "orgs", "org_id")
        else:
            return {"status": 500, "data": {"message": "site_id or org_id missing"}}

    def _get_psks(self, body, scope_name, scope_id_param):
        try:
            scope_id = body[scope_id_param]
            extract = self.extractAuth(body)
            if "full" in body:
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

