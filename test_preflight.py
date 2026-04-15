import ast, os, sys, importlib
sys.path.insert(0, "C:/InfluMatch_AI")

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
errors = []

def check(label, fn):
    try:
        fn()
        print(f"{PASS} {label}")
    except Exception as e:
        print(f"{FAIL} {label} -> {e}")
        errors.append(label)

# 1. Syntax check all frontend .py files
frontend_root = "C:/InfluMatch_AI/influmatch/frontend"
for root, dirs, files in os.walk(frontend_root):
    dirs[:] = [d for d in dirs if d != "__pycache__"]
    for f in files:
        if f.endswith(".py"):
            path = os.path.join(root, f)
            rel  = path.replace(frontend_root, "frontend")
            check(f"Syntax: {rel}", lambda p=path: ast.parse(open(p, encoding="utf-8").read()))

# 2. Session exports
def check_session():
    from influmatch.frontend.utils.session import (
        get_user, get_role, is_logged_in, init_session, logout)
check("Session exports: get_user/get_role/is_logged_in/init_session/logout", check_session)

# 3. Dashboard imports (non-Streamlit-runtime — just check attribute exists after import)
for mod, fn in [
    ("influmatch.frontend._pages.merchant_dashboard",   "render"),
    ("influmatch.frontend._pages.influencer_dashboard", "render"),
    ("influmatch.frontend._pages.god_mode_page",        "render"),
    ("influmatch.frontend._pages.home_page",            "render_home"),
]:
    def _check(m=mod, f=fn):
        m_obj = importlib.import_module(m)
        assert hasattr(m_obj, f), f"Missing: {f}"
    check(f"Import: {mod.split('.')[-1]}", _check)

# 4. CSS tokens
def check_css():
    css = open("C:/InfluMatch_AI/influmatch/frontend/assets/css/style.css", encoding="utf-8").read()
    for token in ["--merchant-primary", "aria-card", "kpi-block", "influencer-banner", "admin-banner"]:
        assert token in css, f"Missing CSS token: {token}"
check("CSS tokens: role colors + card classes", check_css)

# 5. Backend health (optional — skip if not running)
try:
    import httpx
    r = httpx.get("http://localhost:8000/health", timeout=3)
    if r.status_code == 200:
        print(f"{PASS} Backend health: {r.json()}")
    else:
        print(f"{FAIL} Backend health: HTTP {r.status_code}")
        errors.append("Backend health")
except Exception as e:
    print(f"\033[93mSKIP\033[0m Backend health (not running): {e}")

# Summary
print()
if errors:
    print(f"\033[91m{len(errors)} FAILED: {errors}\033[0m")
    sys.exit(1)
else:
    print("\033[92mALL CHECKS PASSED - safe to launch\033[0m")
