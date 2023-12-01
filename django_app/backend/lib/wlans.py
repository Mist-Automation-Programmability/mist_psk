'''
-------------------------------------------------------------------------------

    Written by Thomas Munzer (tmunzer@juniper.net)
    Github repository: 
    https://github.com/Mist-Automation-Programmability/mist_psk

    This script is licensed under the MIT License.

-------------------------------------------------------------------------------
'''

import logging
import requests
from .common import Common


LOGGER = logging.getLogger(__name__)

class Wlan(Common):
    def pull(self, body):
        body = self.get_body(body)
        if "site_id" in body:
            LOGGER.debug("new site_id request")
            return self._get_wlans(body, "sites", "site_id")
        elif "org_id" in body:
            LOGGER.debug("new org_id request")
            return self._get_wlans(body, "orgs", "org_id")
        else:
            LOGGER.error(f"new request without site_id not org_id: {body}")
            return {"status": 500, "data": {"message": "site_id or org_id missing"}}

    def _get_wlans(self, body, scope_name, scope_id_param):
        if scope_id_param in body:
            extract = self.extractAuth(body)
            if scope_name == "sites":
                url = f"https://{extract['host']}/api/v1/sites/{body[scope_id_param]}/wlans/derived"
            elif scope_name == "orgs":
                url = f"https://{extract['host']}/api/v1/orgs/{body[scope_id_param]}/wlans"
            if url:
                try:
                    LOGGER.debug(f"REQ: {url}")
                    resp = requests.get(
                        url, headers=extract["headers"], cookies=extract["cookies"]
                    )
                    LOGGER.debug("REQ: OK")
                    wlans = []
                    for wlan in resp.json():
                        if wlan["auth"]["type"] == "psk":
                            source = "local"
                            if isinstance(wlan.get("dynamic_psk"), dict) and wlan.get("dynamic_psk", {}).get("source"):
                                source = wlan.get("dynamic_psk", {}).get("source")
                            if wlan["auth"].get("multi_psk_only") is True or (isinstance(wlan.get("dynamic_psk"), dict) and wlan.get("dynamic_psk", {}).get("enabled") is True):
                                wlans.append(
                                    {
                                        "id": wlan["id"],
                                        "ssid": wlan["ssid"],
                                        "vlans": wlan.get("vlan_ids", []),
                                        "source": source
                                    }
                                )
                    return {"status": 200, "data": {"wlans": wlans}}
                except:
                    LOGGER.error("REQ: _get_wlans NOK")
                    LOGGER.error("Exception occurred", exc_info=True)
                    return {
                        "status": 500,
                        "data": {"message": "unable to retrieve the WLANs list"},
                    }
            else:
                LOGGER.warn("wrong or missing scope_name parameters in the request")
                return {
                    "status": 500,
                    "data": {
                        "message": f"missing {scope_id_param} parameters in the request"
                    },
                }
        else:
            LOGGER.warn(f"missing {scope_id_param} parameters in the request")
            return {
                "status": 500,
                "data": {
                    "message": f"missing {scope_id_param} parameters in the request"
                },
            }

    def _find_wlans(self, extract, ssid, scope_name, scope_id):
        url = f"https://{extract['host']}/api/v1/{scope_name}/{scope_id}/wlans"
        LOGGER.debug(f"REQ: {url}")
        resp = requests.get(url, headers=extract["headers"], cookies=extract["cookies"])
        LOGGER.debug("REQ: OK")
        wlan_confs = []
        for wlan in resp.json():
            if wlan["ssid"] == ssid:
                wlan_confs.append(wlan)
        return wlan_confs

    def _get_wlan_by_id(self, extract, wlan_id, scope_name, scope_id):
        url = f"https://{extract['host']}/api/v1/{scope_name}/{scope_id}/wlans/{wlan_id}"
        LOGGER.debug(f"REQ: {url}")
        resp = requests.get(url, headers=extract["headers"], cookies=extract["cookies"])
        LOGGER.debug("REQ: OK")
        return resp.json()

    def check_vlan(self, extract, ssid, new_vlan_id, scope_name, scope_id):
        result = []
        if new_vlan_id:
            wlan_confs = self._find_wlans(extract, ssid, scope_name, scope_id)
            """
            "vlan_enabled": true,
            "vlan_id": null,
            "dynamic_vlan": null,
            "vlan_pooling": true,
            "vlan_ids": [10,20]
            """
            if wlan_confs:
                for wlan_conf in wlan_confs:
                    vlan_enabled = wlan_conf["vlan_enabled"]
                    vlan_id = wlan_conf["vlan_id"]
                    vlan_ids = wlan_conf["vlan_ids"]
                    vlan_pooling = wlan_conf["vlan_pooling"]
                    dynamic_vlan = wlan_conf["dynamic_vlan"]
                    if not vlan_enabled:
                        result.append(
                            {
                                "wlan_id": wlan_conf["id"],
                                "reason": "VLAN tagging not enabled",
                                "vlan_id": new_vlan_id,
                                "scope_name": scope_name,
                                "scope_id": scope_id,
                                "code": "untagged",
                            }
                        )
                    elif vlan_id and vlan_id != new_vlan_id:
                        result.append(
                            {
                                "wlan_id": wlan_conf["id"],
                                "reason": "WLAN configured with another VLAN ID",
                                "vlan_id": new_vlan_id,
                                "scope_name": scope_name,
                                "scope_id": scope_id,
                                "code": "static_vlan",
                            }
                        )
                    elif (
                        dynamic_vlan
                        and dynamic_vlan["enabled"]
                        and not new_vlan_id in dynamic_vlan["vlans"]
                    ):
                        result.append(
                            {
                                "wlan_id": wlan_conf["id"],
                                "reason": "VLAN ID missing in dynamic VLAN list",
                                "vlan_id": new_vlan_id,
                                "scope_name": scope_name,
                                "scope_id": scope_id,
                                "code": "missing_in_dynamic",
                            }
                        )
                    elif not vlan_pooling:
                        result.append(
                            {
                                "wlan_id": wlan_conf["id"],
                                "reason": "VLAN Pooling not enabled",
                                "vlan_id": new_vlan_id,
                                "scope_name": scope_name,
                                "scope_id": scope_id,
                                "code": "vlan_pool_disabled",
                            }
                        )
                    elif not new_vlan_id in vlan_ids:
                        result.append(
                            {
                                "wlan_id": wlan_conf["id"],
                                "reason": "VLAN ID missing in VLAN pool list",
                                "vlan_id": new_vlan_id,
                                "scope_name": scope_name,
                                "scope_id": scope_id,
                                "code": "missing_in_pool",
                            }
                        )
        return result

    def change_vlan(self, body):
        # host: this.host, cookies: this.cookies, headers: this.headers, vlan_check: vlan_chec
        body = self.get_body(body)
        extract = self.extractAuth(body)
        result = {"done": [], "error": []}
        if "vlan_check" in body:
            vlan_check = body["vlan_check"]
            wlan_conf = {}
            for check in vlan_check:
                if check["code"] in ["untagged", "vlan_pooling_disabled"]:
                    wlan_conf = {
                        "vlan_enabled": True,
                        "vlan_id": None,
                        "dynamic_vlan": None,
                        "vlan_pooling": True,
                        "vlan_ids": [1, check["vlan_id"]],
                    }
                elif check["code"] == "static_vlan":
                    wlan_conf = self._get_wlan_by_id(
                        extract,
                        check["wlan_id"],
                        check["scope_name"],
                        check["scope_id"],
                    )
                    wlan_conf = {
                        "vlan_enabled": True,
                        "vlan_id": None,
                        "dynamic_vlan": None,
                        "vlan_pooling": True,
                        "vlan_ids": [wlan_conf["vlan_id"], check["vlan_id"]],
                    }
                elif check["code"] == "missing_in_dynamic":
                    wlan_conf = self._get_wlan_by_id(
                        extract,
                        check["wlan_id"],
                        check["scope_name"],
                        check["scope_id"],
                    )
                    wlan_conf["dynamic_vlan"].append(check["vlan_id"])
                elif check["code"] == "missing_in_pool":
                    wlan_conf = self._get_wlan_by_id(
                        extract,
                        check["wlan_id"],
                        check["scope_name"],
                        check["scope_id"],
                    )
                    wlan_conf["vlan_ids"].append(check["vlan_id"])

                try:
                    url = f"https://{extract['host']}/api/v1/{check['scope_name']}/{check['scope_id']}/wlans/{check['wlan_id']}"
                    LOGGER.debug(f"REQ: {url}")
                    resp = requests.put(
                        url,
                        headers=extract["headers"],
                        cookies=extract["cookies"],
                        json=wlan_conf,
                    )
                    LOGGER.debug("REQ: OK")
                    result["done"].append(check["wlan_id"])
                except Exception as e:
                    print(e.__str__)
                    LOGGER.debug("REQ: NOK")
                    result["error"].append(check["wlan_id"])

        return {"status": 200, "data": result}
