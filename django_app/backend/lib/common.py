'''
-------------------------------------------------------------------------------

    Written by Thomas Munzer (tmunzer@juniper.net)
    Github repository: 
    https://github.com/Mist-Automation-Programmability/mist_psk

    This script is licensed under the MIT License.

-------------------------------------------------------------------------------
'''
import json


class Common:

    def get_body(self, body_raw):
        body_unicode = body_raw.decode('utf-8')
        body = json.loads(body_unicode)
        return body

    def extractAuth(self, body):
        # cookies    
        cookies = body["cookies"] if "cookies" in body else None
        # headers
        headers = body['headers'] if "headers" in body else None
        host = body["host"] if "host" in body else None
        # result
        #csrf
        if body["cookies"] :
            if "csrftoken" in body["cookies"]:
                headers["X-CSRFToken"] = body["cookies"]["csrftoken"]
            if "csrftoken.eu" in body["cookies"]:
                headers["X-CSRFToken"] = body["cookies"]["csrftoken.eu"]
            if "csrftoken.gc1" in body["cookies"]:
                headers["X-CSRFToken"] = body["cookies"]["csrftoken.gc1"]
            if "csrftoken.gc2" in body["cookies"]:
                headers["X-CSRFToken"] = body["cookies"]["csrftoken.gc2"]
            if "csrftoken.gc3" in body["cookies"]:
                headers["X-CSRFToken"] = body["cookies"]["csrftoken.gc3"]
            if "csrftoken.ac2" in body["cookies"]:
                headers["X-CSRFToken"] = body["cookies"]["csrftoken.ac2"]
            if "csrftoken.ac5" in body["cookies"]:
                headers["X-CSRFToken"] = body["cookies"]["csrftoken.ac5"]
            if "csrftoken.ac6" in body["cookies"]:
                headers["X-CSRFToken"] = body["cookies"]["csrftoken.ac6"]
        extract = {"host": host, "headers": headers, "cookies": cookies }
        return extract
