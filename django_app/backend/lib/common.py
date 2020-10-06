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
        if body["cookies"] and "csrftoken" in body["cookies"]:
            headers["X-CSRFToken"] = body["cookies"]["csrftoken"]
        extract = {"host": host, "headers": headers, "cookies": cookies }
        return extract