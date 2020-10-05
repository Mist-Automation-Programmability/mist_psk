from django.shortcuts import render
import requests
import json
from django.http import JsonResponse, HttpResponse, Http404
import json
from django.views.decorators.csrf import csrf_exempt
from .lib.__req import Req
import json
import time

def _extractAuth(request):
    # cookies
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)  
    cookies = body["cookies"] if "cookies" in body else None
    # headers
    headers = body['headers'] if "headers" in body else None
    host = body["host"] if "host" in body else None
    # result
    #csrf
    if "csrftoken" in body["cookies"]:
        headers["X-CSRFToken"] = body["cookies"]["csrftoken"]
    extract = {"host": host, "headers": headers, "cookies": cookies }
    return extract

# Load PSK

@csrf_exempt
def psks(request):
    if request.method == "POST":
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        if "site_id" in body :            
            try:
                site_id = body["site_id"]     
                limit =  body["limit"] if "limit" in body else 100
                page = body["page"] + 1 if "page" in body else 1
                extract = _extractAuth(request)
                if "full" in body:
                    limit=1000
                    page=1
                    results = []
                    total = 1
                    while len(results) < int(total) and int(page) < 50:
                        url = "https://{0}/api/v1/sites/{1}/psks?limit={2}&page={3}".format(extract["host"], site_id, limit, page)
                        if "ssid" in body and body["ssid"]: url += "&ssid={0}".format(body["ssid"])
                        resp = requests.get(url, headers=extract["headers"], cookies=extract["cookies"])                      
                        results.extend(json.loads(resp.content))
                        total = resp.headers["X-Page-Total"]
                        page += 1
                    return JsonResponse({"total": total, "results": results})

                else:   
                    url = "https://{0}/api/v1/sites/{1}/psks?limit={2}&page={3}".format(extract["host"], site_id, limit, page)
                    if "ssid" in body and body["ssid"]: url += "&ssid={0}".format(body["ssid"])
                    resp = requests.get(url, headers=extract["headers"], cookies=extract["cookies"])  
                    return JsonResponse({"page": resp.headers["X-Page-Page"], "limit": resp.headers["X-Page-limit"], "total": resp.headers["X-Page-Total"], "results": json.loads(resp.content)})
            except Exception as e:
                print(e)
                return JsonResponse({"error": "unable to retrieve the PSKs list"})
        else:
            return JsonResponse({"error": "site_id missing"})
    else: 
        return Http404

@csrf_exempt
def createPsk(request):
    if request.method == "POST":
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        if "site_id" in body and "name" in body and "passphrase" in body and "ssid" in body:
            psk = {
                "name": body["name"],
                "passphrase": body["passphrase"],
                "ssid": body["ssid"],
                "usage": "multi",                
                }
            if "vlan_id" in body: psk["vlan_id"] = body["vlan_id"]
            if "created_by" in body: psk["created_by"] = body["created_by"]
            extract = _extractAuth(request)          
            url = "https://{0}/api/v1/sites/{1}/psks".format(body["host"], body["site_id"])
            resp = requests.post(url, headers=extract["headers"], cookies=extract["cookies"], json=psk)
            return JsonResponse({"results": json.loads(resp.content) })
    else: 
        return Http404

@csrf_exempt
def deletePsk(request):
    if request.method == "POST":
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        if "site_id" in body and "psk_id" in body:
            try:
                extract = _extractAuth(request)          
                url = "https://{0}/api/v1/sites/{1}/psks/{2}".format(body["host"], body["site_id"], body["psk_id"])
                resp = requests.delete(url, headers=extract["headers"], cookies=extract["cookies"])
                return JsonResponse({"result": "done"})
            except:
                return JsonResponse({"error": "unable to delete the psk"})
                
        else:
            return JsonResponse({"error": "psk_id is missing"})
    else: 
        return Http404
    


@csrf_exempt
def wlans(request):
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)       
        if "site_id" in body :           
            try: 
                site_id = body["site_id"]
                extract = _extractAuth(request)
                url = "https://{0}/api/v1/sites/{1}/wlans".format(extract["host"], site_id)
                resp = requests.get(url, headers=extract["headers"], cookies=extract["cookies"])  
                wlans = []
                for wlan in json.loads(resp.content):
                    if wlan['auth']["type"] == "psk":
                        if wlan["auth"]["multi_psk_only"] == True:
                            wlans.append({"id": wlan["id"], "ssid": wlan["ssid"]})
                return JsonResponse({"data": wlans})
            except:
                return JsonResponse({"error": "unable to retrieve the WLANs list"})
        else:
            return JsonResponse({"error": "site_id missing"})
    else: 
        return Http404
          

def _get_self(request, host, method, headers = {}, cookies=None):
    if cookies == None:
        cookies_dict = None
    else:
        cookies_dict = cookies.get_dict()
    url = "https://%s/api/v1/self" %(host)
    resp = requests.get(url, headers=headers, cookies=cookies)
    data = resp.json()
    return JsonResponse({"data": data, "method":method, "headers": headers, "cookies":  cookies_dict})


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
                    return JsonResponse({"error": "authentication failed"})
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
