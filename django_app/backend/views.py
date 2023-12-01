'''
-------------------------------------------------------------------------------

    Written by Thomas Munzer (tmunzer@juniper.net)
    Github repository: 
    https://github.com/Mist-Automation-Programmability/mist_psk

    This script is licensed under the MIT License.

-------------------------------------------------------------------------------
'''
import json
import ast
import requests
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt

from .mist_smtp.mist_smtp import Mist_SMTP
from .lib.__req import Req
from .lib.psks import Psk
from .lib.wlans import Wlan
from .lib.sites import Sites
from .lib.orgs import Orgs

try:
    from .config import disclaimer_config
    disclaimer_config = {
        "disclaimer": disclaimer_config.get("disclaimer", None),
        "github_url": disclaimer_config.get("github_url", None),
        "docker_url": disclaimer_config.get("docker_url", None)
    }
except:
    import os
    disclaimer_config = {
        "disclaimer": os.environ.get("APP_DISCLAIMER", None),
        "github_url": os.environ.get("APP_GITHUB_URL", None),
        "docker_url": os.environ.get("APP_DOCKER_URL", None)
    }


try:
    from .config import mist_hosts
except:
    mist_hosts = ast.literal_eval(os.environ.get("MIST_HOSTS", default='{"Global 01 - manage.mist.com": "api.mist.com", "Global 02 - manage.gc1.mist.com": "api.gc1.mist.com", "Global 03 - manage.ac2.mist.com": "api.ac2.mist.com","Global 04 - manage.gc2.mist.com": "api.gc2.mist.com", "Europe 01 - manage.eu.mist.com": "api.eu.mist.com"}'))


#############################################
#### SMTP CONFIG
try:
    from .config import smtp_config
    smtp_config["host"] = smtp_config.get("host", None)
    smtp_config["port"] = smtp_config.get("port", 587)
    smtp_config["use_ssl"] = smtp_config.get("use_ssl", True)
    smtp_config["username"] = smtp_config.get("username", None)
    smtp_config["password"] = smtp_config.get("password", None)
    smtp_config["from_name"] = smtp_config.get("from_name", "Wi-Fi Access")
    smtp_config["from_email"] = smtp_config.get("from_email", None)
    smtp_config["logo_url"] = smtp_config.get(
        "logo_url", "https://cdn.mist.com/wp-content/uploads/logo.png")
    smtp_config["enable_qrcode"] = smtp_config.get("enable_qrcode", True)
except:
    import os
    smtp_enabled = os.environ.get("MIST_SMTP_ENABLED", default=False)
    if smtp_enabled:
        smtp_config = {
            "host": os.environ.get("MIST_SMTP_HOST", default=None),
            "port": os.environ.get("MIST_SMTP_PORT", default=587),
            "use_ssl": os.environ.get("MIST_SMTP_SSL", default=True),
            "username": os.environ.get("MIST_SMTP_USER", default=None),
            "password": os.environ.get("MIST_SMTP_PASSWORD", default=None),
            "from_name": os.environ.get("MIST_SMTP_FROM_NAME", default="Wi-Fi Access"),
            "from_email": os.environ.get("MIST_SMTP_FROM_EMAIL", default=None),
            "logo_url": os.environ.get("MIST_SMTP_LOGO_URL", default="https://cdn.mist.com/wp-content/uploads/logo.png"),
            "enable_qrcode": os.environ.get("MIST_SMTP_QRCODE", default=True)
        }
    else:
        smtp_config = None
finally:
    mist_smtp = Mist_SMTP(smtp_config)
    print("".ljust(80, "-"))
    print(" SMTP CONFIG ".center(80))
    print("")
    print(f"host          : {smtp_config['host']}")
    print(f"port          : {smtp_config['port']}")
    print(f"use_ssl       : {smtp_config['use_ssl']}")
    print(f"username      : {smtp_config['username']}")
    print(f"from_name     : {smtp_config['from_name']}")
    print(f"from_email    : {smtp_config['from_email']}")
    print(f"logo_url      : {smtp_config['logo_url']}")
    print(f"enable_qrcode : {smtp_config['enable_qrcode']}")
    print("")

#############################################
#### PSK CONFIG
try:
    from .config import psk_config
    psk_config["salt"] = psk_config.get(
        "salt", "$2b$12$SIGWr574/7OggDO4BBJ1D.")
    psk_config["length"] = psk_config.get("length", 12)
    psk_config["default_expire_time"] = psk_config.get(
        "default_expire_time", 0)
except:
    psk_config = {
        "default_expire_time": int(os.environ.get("MIST_PSK_DEFAULT_EXPIRE_TIME", default=0)),
        "salt": os.environ.get("MIST_PSK_SALT", default="$2b$12$SIGWr574/7OggDO4BBJ1D."),
        "length": int(os.environ.get("MIST_PSK_LENGTH", default=12))
    }
finally:
    print("".ljust(80, "-"))
    print(" PSK CONFIG ".center(80))
    print("")
    print(f"default expire time: {psk_config['default_expire_time']}")
    print(f"length             : {psk_config['length']}")
    print("")
    psk_config["salt"] = str.encode(psk_config["salt"])




#############################################
#### VIEWS

##########
# PSK CONFIG
def pskConfig(request):
    if request.method == "GET":
        response = {
            "psk_length": psk_config["length"],
            "default_expire_time": psk_config["default_expire_time"]
        }
        return JsonResponse(status=200, data=response)
    else:
        return Http404

##########
# PSK


@csrf_exempt
def psks(request):
    if request.method == "POST":
        response = Psk().pull(request.body)
        return JsonResponse(status=response["status"], data=response["data"])
    else:
        return Http404


@csrf_exempt
def createPsk(request):
    if request.method == "POST":
        response = Psk().push(request.body, psk_config)
        return JsonResponse(status=response["status"], data=response["data"])
    else:
        return Http404


@csrf_exempt
def deletePsk(request):
    if request.method == "POST":
        response = Psk().delete(request.body)
        return JsonResponse(status=response["status"], data=response["data"])
    else:
        return Http404

##########
# orgs


@csrf_exempt
def orgs(request):
    if request.method == 'POST':
        response = Orgs().pull(request.body)
        return JsonResponse(status=response["status"], data=response["data"])
    else:
        return Http404
    

##########
# Sites


@csrf_exempt
def sites(request):
    if request.method == 'POST':
        response = Sites().pull(request.body)
        return JsonResponse(status=response["status"], data=response["data"])
    else:
        return Http404

##########
# WLANS


@csrf_exempt
def wlans(request):
    if request.method == 'POST':
        response = Wlan().pull(request.body)
        return JsonResponse(status=response["status"], data=response["data"])
    else:
        return Http404

##########
# VLAN


@csrf_exempt
def vlans(request):
    if request.method == "POST":
        response = Wlan().change_vlan(request.body)
        return JsonResponse(status=response["status"], data=response["data"])
    else:
        return Http404
##########
# LOGIN


def _get_self(request, host, method, headers={}, cookies=None):
    if cookies == None:
        cookies_dict = None
    else:
        cookies_dict = cookies.get_dict()
    url = "https://%s/api/v1/self" % (host)
    resp = requests.get(url, headers=headers, cookies=cookies)
    data = resp.json()
    return JsonResponse({"host": host, "data": data, "method": method, "headers": headers, "cookies":  cookies_dict})


@csrf_exempt
def login(request):
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        if "host" in body:

            if "token" in body:
                headers = {"Authorization": "Token " +
                           body["token"], 'Content-Type': "application/json"}
                return _get_self(request, body["host"], "token", headers=headers)

            elif "email" in body and "password" in body:
                url = "https://%s/api/v1/login" % (body["host"])
                data = {"email": body["email"], "password": body["password"]}
                if "two_factor" in body:
                    data["two_factor"] = body["two_factor"]
                headers = {'Content-Type': "application/json"}
                resp = requests.post(url, json=data, headers={})

                if resp.status_code == 200:
                    cookies = resp.cookies
                    return _get_self(request, body["host"], "username", headers=headers, cookies=cookies)
                else:
                    return JsonResponse(status=400, data={"message": "authentication failed"})
            elif "email" in body:
                return JsonResponse(status=401, data={"message": "authentication information are missing"})
            elif "password" in body:
                return JsonResponse(status=401, data={"message": "authentication information are missing"})
            else:
                return JsonResponse(status=500, data={"message": "authentication information are missing"})
        else:
            return JsonResponse(status=500, data={"message": "host missing"})
    else:
        return JsonResponse(status=400, data={"message": "not allowed"})

##########
# EMAIL


@csrf_exempt
def emailPsk(request):
    if request.method == 'POST':
        body_unicode = request.body.decode("utf-8")
        body = json.loads(body_unicode)
        if "name" in body and "user_email" in body and "ssid" in body and "psk" in body:
            resp = mist_smtp.send_psk(
                body["psk"], body["ssid"], body["name"], body["user_email"], body.get("expire_time", None))
            return JsonResponse({"result": resp})
        else:
            return JsonResponse(status=500, data={"message": "missing parametesr"})


def disclaimer(request):
    if request.method == "GET":
        return JsonResponse(disclaimer_config)
    else:
        return JsonResponse(status=500, data={"message": "missing parametesr"})


def hosts(request):
    if request.method == "GET":
        data = []
        for key in mist_hosts:
            data.append({"value": mist_hosts[key], "viewValue": key})
        data = sorted(data, key=lambda x: x["viewValue"])
        return HttpResponse(json.dumps(data))
