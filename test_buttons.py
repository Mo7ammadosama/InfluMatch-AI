import urllib.request, json, urllib.error, urllib.parse, time, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

base = 'http://127.0.0.1:8000'
ts   = int(time.time())
results = []

def get(path, token=None, params=None):
    url = f'{base}{path}'
    if params: url += '?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url)
    if token: req.add_header('Authorization', f'Bearer {token}')
    try:
        r = urllib.request.urlopen(req, timeout=10)
        return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        try: return e.code, json.loads(e.read())
        except: return e.code, {}
    except Exception as ex:
        return 0, str(ex)

def post(path, data=None, token=None, form=False):
    if form:
        body = urllib.parse.urlencode(data).encode()
        ct = 'application/x-www-form-urlencoded'
    else:
        body = json.dumps(data or {}).encode()
        ct = 'application/json'
    req = urllib.request.Request(f'{base}{path}', data=body, method='POST')
    req.add_header('Content-Type', ct)
    if token: req.add_header('Authorization', f'Bearer {token}')
    try:
        r = urllib.request.urlopen(req, timeout=15)
        return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        try: return e.code, json.loads(e.read())
        except: return e.code, {}
    except Exception as ex:
        return 0, str(ex)

def patch(path, data, token=None):
    body = json.dumps(data).encode()
    req = urllib.request.Request(f'{base}{path}', data=body, method='PATCH')
    req.add_header('Content-Type', 'application/json')
    if token: req.add_header('Authorization', f'Bearer {token}')
    try:
        r = urllib.request.urlopen(req, timeout=10)
        return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        try: return e.code, json.loads(e.read())
        except: return e.code, {}
    except Exception as ex:
        return 0, str(ex)

def chk(label, s, expected=None, detail=''):
    ok = (s < 400) if expected is None else (s == expected)
    tag = 'PASS' if ok else 'FAIL'
    print(f'[{tag}] {label}: HTTP {s} {detail}')
    results.append((tag, label, s))

# Tokens
def login(email, pwd, retries=3):
    for i in range(retries):
        s, r = post('/api/v1/auth/login', {'username': email, 'password': pwd}, form=True)
        if isinstance(r, dict) and r.get('access_token'):
            return r['access_token']
        time.sleep(1)
    print(f'[WARN] Login failed after {retries} tries: {email}')
    return ''

TM = login('merchant@waslai.jo', 'WaslAI@2026')
TI = login('influencer@waslai.jo', 'WaslAI@2026')
TA = login('admin@waslai.jo', 'WaslAI@2026')
print(f'Tokens: merchant={bool(TM)} influencer={bool(TI)} admin={bool(TA)}\n')

# AUTH
print('=== AUTH ===')
s,r = get('/health'); chk('Health check', s)
s,r = post('/api/v1/auth/register',{'email':f'u{ts}@t.jo','username':f'u{ts}','password':'Test@1234','full_name_en':'Test','full_name_ar':'Test AR','role':'merchant','phone':''})
chk('Register new user', s, 201, f'id={r.get("id","?")}')
s,r = post('/api/v1/auth/register',{'email':f'u{ts}@t.jo','username':f'u2{ts}','password':'Test@1234','full_name_en':'Dup','full_name_ar':'Dup','role':'merchant','phone':''})
chk('Duplicate email -> 409', s, 409)
s,r = post('/api/v1/auth/login',{'username':'merchant@waslai.jo','password':'WaslAI@2026'}, form=True); chk('Login', s)
s,r = get('/api/v1/auth/me', TM); chk('GET /me', s)
print()

# CAMPAIGNS
print('=== CAMPAIGNS ===')
s,r = get('/api/v1/campaigns/', TM)
cnt = len(r.get('data',r) if isinstance(r,dict) else r)
chk('List campaigns', s, detail=f'count={cnt}')
s,r = post('/api/v1/campaigns/', {'title_ar':'Test','title_en':'Test Camp','niche':'Fashion','total_budget':200.0,'description_ar':'desc','description_en':'desc'}, TM)
chk('Create campaign', s, 201, f'id={r.get("id","?")}')
camp_id = r.get('id')
if camp_id:
    s,r = get(f'/api/v1/campaigns/{camp_id}', TM); chk('Get campaign by ID', s)
    s,r = post(f'/api/v1/campaigns/{camp_id}/activate', token=TM); chk('Activate campaign', s)
s,r = get('/api/v1/campaigns/my', TM); chk('My campaigns', s)
print()

# INFLUENCERS
print('=== INFLUENCERS ===')
s,r = get('/api/v1/influencers/', TM, params={'limit':10})
cnt = len(r.get('data',r) if isinstance(r,dict) else r)
chk('List influencers', s, detail=f'count={cnt}')
s,r = get('/api/v1/influencers/me', TI); chk('GET /influencers/me', s)
s,r = patch('/api/v1/influencers/me', {'city':'Amman','niche':'Fashion','rate_per_post':75.0}, TI); chk('PATCH /influencers/me', s)
s,r = post('/api/v1/influencers/smart-search', {'brief':'fashion influencer Amman','top_k':5}, TM)
chk('Smart search', s, detail=f'results={len(r.get("results",[]) if isinstance(r,dict) else [])}')
print()

# BOOKINGS
print('=== BOOKINGS ===')
s,r = get('/api/v1/bookings/my', TM)
bks_m = r.get('data',r) if isinstance(r,dict) else r
chk('My bookings (merchant)', s, detail=f'count={len(bks_m) if isinstance(bks_m,list) else "?"}')
s,r = get('/api/v1/bookings/my', TI)
bks_i = r.get('data',r) if isinstance(r,dict) else r
chk('My bookings (influencer)', s)

if isinstance(bks_i, list):
    pending = [b for b in bks_i if b.get('status') == 'pending']
    confirmed = [b for b in bks_i if b.get('status') == 'confirmed']
    if pending:
        bid = pending[0]['id']
        s,r2 = post(f'/api/v1/bookings/{bid}/confirm', {}, TI); chk(f'Confirm booking #{bid}', s)
    if confirmed:
        bid = confirmed[0]['id']
        s,r2 = post(f'/api/v1/bookings/{bid}/submit-content', {'content_url':'https://www.instagram.com/p/test123/','caption':'Test #ad #jordan'}, TI)
        chk(f'Submit content #{bid}', s)
print()

# WALLET
print('=== WALLET ===')
s,r = get('/api/v1/wallet/me', TI)
chk('GET wallet/me', s, detail=f'points={r.get("total_points","?") if isinstance(r,dict) else r}')
s,r = post('/api/v1/wallet/redeem', {'points':0}, TI); chk('Redeem points (0)', s)
print()

# MESSAGES
print('=== MESSAGES ===')
s,r = get('/api/v1/messages/unread-count/me', TM)
chk('Unread count', s, detail=f'n={r.get("unread_count","?") if isinstance(r,dict) else r}')
print()

# CHATBOT
print('=== CHATBOT ===')
s,r = post('/api/v1/chatbot/chat', {'message':'What is escrow protection?','language':'en'}, TM)
chk('Chatbot', s, detail=f'reply_len={len(r.get("response","")) if isinstance(r,dict) else 0}')
print()

# ADMIN
print('=== ADMIN ===')
s,r = get('/api/v1/admin/platform-stats', TA)
chk('Platform stats', s, detail=f'users={r.get("total_users","?") if isinstance(r,dict) else r}')
s,r = get('/api/v1/admin/users', TA); chk('List users (admin)', s)
s,r = post('/api/v1/admin/trigger/scoring', {}, TA); chk('Trigger ARIA scoring', s)
s,r = post('/api/v1/admin/trigger/reaudit', {}, TA); chk('Trigger reaudit', s)
s,r = get('/api/v1/admin/jobs', TA); chk('List jobs', s)
print()

# SUMMARY
passed = sum(1 for t,_,_ in results if t=='PASS')
failed = sum(1 for t,_,_ in results if t=='FAIL')
print(f'{"="*40}')
print(f'TOTAL: {passed} PASS  |  {failed} FAIL')
if failed:
    print('\nFAILED ENDPOINTS:')
    for t,l,s in results:
        if t=='FAIL': print(f'  x {l}  (HTTP {s})')
