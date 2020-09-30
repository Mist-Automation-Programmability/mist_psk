from django.shortcuts import render
import requests
import json
from django.http import JsonResponse, HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
from .lib.__req import Req
import json
import time


with open('reports.json', 'r') as f:
        report_templates = json.load(f)

@csrf_exempt
def mpsk(request):
    if request.method == 'GET':
        verticals = {"verticals": [
            "retail",
            "healthcare",
            "education",
            "enterprise"
        ]}
        return JsonResponse(verticals)


@csrf_exempt
def ssid(request):
    if request.method == 'GET':
        types = {"types": [
            "presence report",
            "network report"
        ]}
        return JsonResponse(types)
          

def _get_self(request, host, headers = {}, cookies=None):
    if cookies == None:
        cookies_dict = None
    else:
        cookies_dict = cookies.get_dict()
    url = "https://%s/api/v1/self" %(host)
    resp = requests.get(url, headers=headers, cookies=cookies)
    data = resp.json()
    return JsonResponse({"data": data, "headers": headers, "cookies":  cookies_dict})


@csrf_exempt
def login(request):
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)        
        if "host" in body:

            if "token" in body:
                headers = {"Authorization": "Token " + body["token"], 'Content-Type': "application/json"}
                return _get_self(request, body["host"], headers=headers)

            elif "email" in body and "password" in body:    
                url = "https://%s/api/v1/login" %(body["host"])
                headers = { 'Content-Type': "application/json"}
                resp = requests.post(url, json={"email": body["email"],"password":body["password"]}, headers={})
                cookies = resp.cookies
                return _get_self(request, body["host"], headers=headers, cookies=cookies)


            elif "email" in body:
                return JsonResponse({"error": "authentication information are missing"})
            elif "password" in body:
                return JsonResponse({"error": "authentication information are missing"})
            else:
                return JsonResponse({"error": "authentication information are missing"})
        else:
            return JsonResponse({"error": "host missing"})
    else:
        return JsonResponse({"error": "not allowed"})

@csrf_exempt
def sites(request):
    if request.method == 'POST':
        
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)  
        if "host" in body and "headers" in body and "cookies" in body and "org_id" in body:
            url = "https://%s/api/v1/orgs/%s/sites" %(body["host"], body["org_id"])
            resp = requests.get(url, headers=body["headers"], cookies=body["cookies"])
            return JsonResponse({"data": resp.json()})
        else:
            return JsonResponse({"error": "information missing"})
    else:
        return JsonResponse({"error": "not allowed"})
