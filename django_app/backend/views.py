from django.shortcuts import render
import requests
import json
from django.http import JsonResponse, HttpResponse, Http404
import json
from django.views.decorators.csrf import csrf_exempt
import json
import time
import logging

from .mist_smtp.mist_smtp import Mist_SMTP
from .lib.__req import Req
from .lib.psks import Psk
from .lib.wlans import Wlan
from .lib.sites import Sites

mist_smtp = Mist_SMTP()


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
        response = Psk().push(request.body)        
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
# LOGIN
def _get_self(request, host, method, headers = {}, cookies=None):
    if cookies == None:
        cookies_dict = None
    else:
        cookies_dict = cookies.get_dict()
    url = "https://%s/api/v1/self" %(host)
    resp = requests.get(url, headers=headers, cookies=cookies)
    data = resp.json()
    return JsonResponse({"host": host, "data": data, "method":method, "headers": headers, "cookies":  cookies_dict})


@csrf_exempt
def login(request):
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)        
        if "host" in body:

            if "token" in body:
                headers = {"Authorization": "Token " + body["token"], 'Content-Type': "application/json"}
                return _get_self(request, body["host"], "token", headers=headers)

            elif "email" in body and "password" in body:    
                url = "https://%s/api/v1/login" %(body["host"])
                data = {"email": body["email"],"password":body["password"]}
                if "two_factor" in body: data["two_factor"] = body["two_factor"]
                headers = { 'Content-Type': "application/json"}
                resp = requests.post(url, json=data, headers={})

                if resp.status_code == 200:
                    cookies = resp.cookies
                    return _get_self(request, body["host"], "username", headers=headers, cookies=cookies)
                else:
                    return JsonResponse(status=400, data={"error": "authentication failed"})
            elif "email" in body:
                return JsonResponse(status=401, data={"error": "authentication information are missing"})
            elif "password" in body:
                return JsonResponse(status=401, data={"error": "authentication information are missing"})
            else:
                return JsonResponse(status=500, data={"error": "authentication information are missing"})
        else:
            return JsonResponse(status=500, data={"error": "host missing"})
    else:
        return JsonResponse(status=400, data={"error": "not allowed"})

##########
# EMAIL
@csrf_exempt
def emailPsk(request):
    if request.method == 'POST':
        body_unicode = request.body.decode("utf-8")
        body = json.loads(body_unicode)
        if "name" in body and "user_email" in body and "ssid" in body and "psk" in body:
            resp = mist_smtp.send_psk(body["psk"], body["ssid"], body["name"], body["user_email"])
            return JsonResponse({"result": resp})
        else: 
            return JsonResponse(status=500, data={"error": "missing parametesr"})
