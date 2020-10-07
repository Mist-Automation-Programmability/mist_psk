import requests
import json
import logging
from .common import Common

class Wlan(Common):

    def pull(self, body):
        body = self.get_body(body)
        if "site_id" in body:
            logging.debug("new site_id request")
            return self._get_wlans(body, "sites", "site_id")
        elif "org_id" in body:
            logging.debug("new org_id request")
            return self._get_wlans(body, "orgs", "org_id")
        else:
            logging.error("new request without site_id not org_id: {0}".format(body))
            return {"status": 500, "data": {"message": "site_id or org_id missing"}}

    def _get_wlans(self, body, scope_name, scope_id_param):
        if scope_id_param in body :           
            scope_id = body[scope_id_param]
            extract = self.extractAuth(body)
            #try: 
            url = "https://{0}/api/v1/{1}/{2}/wlans".format(extract["host"], scope_name, scope_id)
            logging.debug("REQ: {0}".format(url))
            resp = requests.get(url, headers=extract["headers"], cookies=extract["cookies"])  
            logging.debug("REQ: OK")
            wlans = []
            for wlan in resp.json():
                if wlan['auth']["type"] == "psk":
                    if wlan["auth"]["multi_psk_only"] == True:
                        wlans.append({"id": wlan["id"], "ssid": wlan["ssid"]})
            if scope_id_param == "site_id":            
                wlans.extend(self._get_wlans_from_templates(body, extract))
            return {"status": 200, "data": {"wlans": wlans}}
            # except:
            #     logging.error("REQ: _get_wlans NOK")
            #     return {"status": 500, "data": {"message": "unable to retrieve the WLANs list"}}
        else:
            logging.warn("missing {0} parameters in the request".format(scope_id_param))
            return {"status": 500, "data": {"message": "missing {0} parameters in the request".format(scope_id_param)}}


    def _get_wlans_from_templates(self, body, extract):
        wlans = []
        #try:
        url = "https://{0}/api/v1/orgs/{1}/wlans".format(extract["host"], body["org_id"])
        logging.debug("REQ: {0}".format(url))
        resp = requests.get(url, headers=extract["headers"], cookies=extract["cookies"])  
        wlan_list = resp.json()
        logging.debug("REQ: OK")

        template_ids = self._find_site_templates(body, extract)

        for wlan in wlan_list:
            if wlan['auth']["type"] == "psk":
                if wlan["auth"]["multi_psk_only"] == True:                    
                    if wlan["template_id"] in template_ids:
                        wlans.append({"id": wlan["id"], "ssid": wlan["ssid"]})
        return wlans
        # except:
        #     return {"status": 500, "data": {"message": "unable to retrieve wlans from org templates"}}

    def _find_site_templates(self, body, extract):
        template_ids = []
        site_id = body["site_id"]
        sitegroup_ids = body["sitegroup_ids"] if "sitegroup_ids" in body else []

        url = "https://{0}/api/v1/orgs/{1}/templates".format(extract["host"], body["org_id"])
        logging.debug("REQ: {0}".format(url))
        resp = requests.get(url, headers=extract["headers"], cookies=extract["cookies"])  
        template_list = resp.json()
        logging.debug("REQ: OK")

        for template in template_list:
            if "applies" in template:
                site_ids = template["applies"]["site_ids"] if "site_ids" in template["applies"] else []
                sitegroup_ids = template["applies"]["sitegroup_ids"] if "sitegroup_ids" in template["applies"] else []
                if site_id in site_ids or self._test_sitegroups_ids(sitegroup_ids, sitegroup_ids):
                    template_ids.append(template["id"])
        return template_ids



    def _test_sitegroups_ids(self, groups_from_site, groups_from_template):
        if groups_from_site and groups_from_template:
            for sitegroup_id in groups_from_site:
                if sitegroup_id in groups_from_template:
                    return True
        return False

