import streamlit as st
import requests
import base64
from PIL import Image
import io
import textwrap
import os
import streamlit.components.v1 as components
import jwt
from urllib.parse import urlencode

st.set_page_config(page_title="CookWithMe", page_icon="🍽️", layout="wide")


# ================= TOKEN BOOTSTRAP (THE ONLY ONE) =================

# A) Try to restore from localStorage (do NOT stop unless redirect already triggered)
if not st.session_state.get("token") and not st.query_params.get("token"):
    if st.query_params.get("_ls") != "1":
        components.html("""
        <script>
        try {
            const t = window.parent.localStorage.getItem("cwm_token");
            if (t) {
            const url = new URL(window.parent.location.href);
            url.searchParams.set("_ls", "1");
            url.searchParams.set("token", t);
            window.parent.location.replace(url.toString());
            }
        } catch(e) {}
        </script>
        """, height=0)
    else:
        # We are in the middle of redirect cycle
        st.stop()

# B) If token is in URL, store it in session, then clean URL WITHOUT full reload
tok = st.query_params.get("token")
if tok:
    st.session_state.token = tok

    keep = {}
    for k in ("hl", "fav"):
        v = st.query_params.get(k)
        if v:
            keep[k] = v

    # clean query params in streamlit
    st.query_params.clear()
    for k, v in keep.items():
        st.query_params[k] = v

    # also clean URL in browser (no reload)
    qs = "?" + urlencode(keep) if keep else ""
    components.html(
        f"""
        <script>
          try {{
            window.parent.history.replaceState({{}}, "", window.parent.location.pathname + {qs!r});
          }} catch(e) {{}}
        </script>
        """,
        height=0,
    )

    st.rerun()

# C) Clean _ls if it stayed
if st.query_params.get("_ls"):
    st.query_params.pop("_ls", None)

token = st.session_state.get("token")
# ================= PAGE DEFAULT + GUARD =================
if "page" not in st.session_state:
    st.session_state.page = "list" if st.session_state.get("token") else "login"

hl_q = st.query_params.get("hl")

if st.session_state.page not in ("login", "signup") and not st.session_state.get("token"):
    if hl_q:
        st.session_state.post_login_hl = hl_q
    st.session_state.page = "login"
    st.rerun()

# ------------------------
# 1. CONFIG & STATE
# ------------------------

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
RECIPES_URL = f"{BASE_URL}/recipes"
HIGHLIGHTS_URL = f"{BASE_URL}/highlights"

# ------------------------
# security check
# ------------------------
def auth_headers():
    tok = st.session_state.get("token")
    return {"Authorization": f"Bearer {tok}"} if tok else {}

def add_favorite(recipe_id: int) -> bool:
    res = requests.post(f"{BASE_URL}/favorites/{recipe_id}", headers=auth_headers())
    if res.status_code not in (200, 201, 204):
        st.error(f"Failed to add favorite ({res.status_code})")
        st.caption(res.text)
        return False
    return True


def remove_favorite(recipe_id: int) -> bool:
    res = requests.delete(f"{BASE_URL}/favorites/{recipe_id}", headers=auth_headers())
    if res.status_code not in (200, 204):
        st.error(f"Failed to remove favorite ({res.status_code})")
        st.caption(res.text)
        return False
    return True


def get_favorites() -> list:
    res = requests.get(f"{BASE_URL}/favorites", headers=auth_headers())

    if res.status_code != 200:
        st.warning(f"Favorites not available ({res.status_code})")
        st.caption(res.text[:500] if res.text else "Empty response")
        return []

    try:
        data = res.json()
        return data if isinstance(data, list) else []
    except Exception:
        st.warning("Favorites response is not JSON")
        st.caption(res.text[:500] if res.text else "Empty response")
        return []


# ------------------------
# 2. CUSTOM CSS
# -----------------------
def local_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&family=Dancing+Script:wght@600&display=swap');

:root {
  --main: #1e1e1e;
  --accent: #c9a24d;
  --soft-bg: #faf7f2;
  --card-bg: #ffffff;
}

/* ============ BASE ============ */
html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
.stApp { background: var(--soft-bg); background-attachment: fixed; }

h1 { color: #1e1e1e; font-weight: 800; letter-spacing: -1px; }
h2, h3 { color: var(--accent); }

/* ============ SIDEBAR ============ */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #151515 0%, #1f1f1f 100%) !important;
  border-right: 1px solid rgba(255,255,255,0.08) !important;
}
[data-testid="stSidebar"] * { color: white !important; }
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.10) !important; }

.sidebar-title {
  font-size: 1.7rem;
  font-weight: 900;
  color: white;
  -webkit-text-stroke: 0.6px rgba(255,255,255,0.45);
  text-shadow:
    0 2px 4px rgba(0,0,0,0.45),
    0 0 12px rgba(201,162,77,0.40);
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 2px;
}

.signature {
  line-height: 2.6rem;
  font-family: 'Dancing Script', cursive !important;
  font-size: 1.5rem;
  color: var(--accent) !important;
  margin-top: -10px;
  margin-bottom: 18px;
  margin-left: 5px;
  text-shadow: 1px 1px 2px rgba(0,0,0,0.15);
  letter-spacing: 0.5px;
}

/* Sidebar buttons */
[data-testid="stSidebar"] .stButton > button{
  width:100% !important;
  background: rgba(255,255,255,0.08) !important;
  border: 1px solid rgba(255,255,255,0.14) !important;
  border-radius: 14px !important;
  padding: 0.75rem 0.9rem !important;
  font-weight: 800 !important;
  text-align: left !important;
  box-shadow:none !important;
  transition: 0.18s ease;
}
[data-testid="stSidebar"] .stButton > button:hover{
  transform: translateY(-1px);
  background: rgba(255,255,255,0.14) !important;
  border-color: rgba(201,162,77,0.70) !important;
  color: white !important;
}

/* ================= CTA BUTTONS ONLY (Main Area) ================= */
/* תופס רק כפתורים ספציפיים לפי הטקסט שלהם (aria-label) */

section.main button[aria-label^="View Recipe"]{
  background: var(--accent) !important;
  color: #111 !important;
  border-radius: 40px !important;
  font-weight: 800 !important;
  border: none !important;
  box-shadow: 0 10px 25px rgba(201,162,77,0.25) !important;
}
section.main button[aria-label^="View Recipe"]:hover{
  background: #111 !important;
  color: var(--accent) !important;
}

/* עוד CTA שאת כנראה רוצה בעיצוב זהב */
section.main button[aria-label="Submit Review"],
section.main button[aria-label="Save Recipe 🎉"],
section.main button[aria-label="✏️ Edit"],
section.main button[aria-label="🗑️ Delete"],
section.main button[aria-label="⬅️ Back"]{
  background: var(--accent) !important;
  color: #111 !important;
  border-radius: 40px !important;
  font-weight: 800 !important;
  border: none !important;
  box-shadow: 0 10px 25px rgba(201,162,77,0.25) !important;
}
section.main button[aria-label="Submit Review"]:hover,
section.main button[aria-label="Save Recipe 🎉"]:hover,
section.main button[aria-label="✏️ Edit"]:hover,
section.main button[aria-label="🗑️ Delete"]:hover,
section.main button[aria-label="⬅️ Back"]:hover{
  background: #111 !important;
  color: var(--accent) !important;
}

/* ============ SIDEBAR BUTTONS OVERRIDE ============ */
[data-testid="stSidebar"] div[data-testid="stButton"] > button{
  width:100% !important;
  background: rgba(255,255,255,0.08) !important;
  border: 1px solid rgba(255,255,255,0.14) !important;
  border-radius: 14px !important;
  padding: 0.75rem 0.9rem !important;
  font-weight: 800 !important;
  text-align: left !important;
  box-shadow:none !important;
  transition: 0.18s ease;
}

[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover{
  transform: translateY(-1px);
  background: rgba(255,255,255,0.14) !important;
  border-color: rgba(201,162,77,0.70) !important;
}

/* ============ RECIPE CARDS ============ */
.recipe-card {
  background: var(--card-bg);
  border-radius: 22px;
  box-shadow: 0 12px 40px rgba(0,0,0,0.06);
  transition: 0.35s ease;
  margin-bottom: 0 !important;
  overflow: hidden;
}
.recipe-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 18px 60px rgba(0,0,0,0.12);
}
.card-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 5px;
  height: 50px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.badge {
  position: absolute;
  top: 10px;
  right: 10px;
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: bold;
  letter-spacing: 0.5px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}
.bg-Easy { background: #3a7d44; }
.bg-Medium { background: #b88940; }
.bg-Hard { background: #7a2e2e; }

/* ===== FORCE GOLD BUTTONS (Main only) ===== */
section[data-testid="stMain"] div.stButton > button,
section[data-testid="stMain"] div[data-testid="stButton"] > button,
section[data-testid="stMain"] button[data-testid^="baseButton"]{
  background-color: #D4AF37 !important;
  background-image: linear-gradient(135deg, #D4AF37, #F5D76E) !important;
  color: #2b2b2b !important;
  border: none !important;
  border-radius: 14px !important;
  font-weight: 700 !important;
  padding: 0.75em 1.5em !important;
  box-shadow: 0 4px 10px rgba(212,175,55,0.35) !important;
  transition: all 0.2s ease-in-out !important;
}

section[data-testid="stMain"] div.stButton > button:hover,
section[data-testid="stMain"] div[data-testid="stButton"] > button:hover,
section[data-testid="stMain"] button[data-testid^="baseButton"]:hover{
  background-color: #F5D76E !important;
  background-image: linear-gradient(135deg, #F5D76E, #D4AF37) !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 6px 14px rgba(212,175,55,0.5) !important;
}

                /* ===== EXCEPT LOGIN MODE BUTTONS ===== */
.stApp.login-mode section[data-testid="stMain"] div[data-testid="stFormSubmitButton"] > button{
  background: var(--accent) !important;
  background-image: none !important;
  color: #111 !important;
  border-radius: 16px !important;
  font-weight: 900 !important;
  box-shadow: 0 14px 30px rgba(201,162,77,0.25) !important;
}

.stApp.login-mode section[data-testid="stMain"] div[data-testid="stFormSubmitButton"] > button:hover{
  background: #111 !important;
  background-image: none !important;
  color: var(--accent) !important;
}
/* ============ HIGHLIGHTS ============ */

.hl-wrap *{
  pointer-events: none !important;
}

/* הכפתור של היילייט יושב מעל העיגול */
.hl-wrap div[data-testid="stButton"]{
  position: absolute !important;
  top: 6px;
  left: 50%;
  transform: translateX(-50%);
  width: 92px !important;
  height: 92px !important;
  margin: 0 !important;
  padding: 0 !important;
  z-index: 100 !important;
}

.ring {
  width: 92px;
  height: 92px;
  border-radius: 50%;
  background: #d4af37;
  padding: 2px;
  box-sizing: border-box;
  transition: 0.2s ease;
}

.inner {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background-size: cover;
  background-position: center;
  box-shadow: inset 0 0 0 2px rgba(255,255,255,0.9);
}

.hl-visual{ text-align:center; }
.hl-visual:hover .ring { transform: scale(1.05); }

.title {
  margin-top: 8px;
  font-size: 0.8rem;
  font-weight: 600;
  color: #1e1e1e;
}
                
.hl-link{
  display: inline-block;
  text-decoration: none !important;
  color: inherit !important;
  position: relative;
  z-index: 99999 !important;
  pointer-events: auto !important;
}

.hl-wrap{
  cursor: pointer;
  position: relative;
  pointer-events: auto !important;
}

.hl-wrap *{
  pointer-events: auto !important;
}

/* ============ STARS (RATING) ============ */
.star-row{
  display:flex;
  gap:4px;
  align-items:center;
}

/* ביטול רווחים מסביב לסטארים */
.star-row .stButton,
.star-row div[data-testid="stButton"]{
  margin:0 !important;
  padding:0 !important;
}

/* הכפתור של הסטארים — שקוף + גדול */
.star-row button,
.star-row div[data-testid="stButton"] > button{
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  font-size: 42px !important;
  padding: 0 !important;
  margin: 0 !important;
  min-width: unset !important;
  line-height: 1 !important;
}
.star-row button:hover,
.star-row div[data-testid="stButton"] > button:hover{
  transform: scale(1.15);
}

section.main div[data-testid="stButton"] > button[key^="star_"]{
  background: transparent !important;
  box-shadow: none !important;
  border: none !important;
  font-size: 42px !important;
  padding: 0 !important;
  margin: 0 !important;
  border-radius: 0 !important;
}

/* ============ LOGIN MODE (CARD CENTER) ============ */
.stApp.login-mode section.main > div{
  display:flex;
  justify-content:center;
}
.stApp.login-mode .block-container{
  max-width: 520px !important;
  padding-top: 10vh !important;
  padding-bottom: 6vh !important;
  background: rgba(255,255,255,0.88);
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: 26px;
  box-shadow: 0 22px 60px rgba(0,0,0,0.12);
  backdrop-filter: blur(10px);
}

/* inputs */
.stApp.login-mode div[data-testid="stTextInput"] input{
  border-radius: 14px !important;
  border: 1px solid rgba(0,0,0,0.12) !important;
  padding: 0.85rem 0.9rem !important;
  background: rgba(255,255,255,0.95) !important;
}
.stApp.login-mode div[data-testid="stTextInput"] input:focus{
  border-color: rgba(201,162,77,0.75) !important;
  box-shadow: 0 0 0 4px rgba(201,162,77,0.22) !important;
  outline: none !important;
}

/* login submit button */
.stApp.login-mode div[data-testid="stFormSubmitButton"] > button{
  width: 100% !important;
  background: var(--accent) !important;
  color: #111 !important;
  border-radius: 16px !important;
  border: none !important;
  font-weight: 900 !important;
  padding: 0.9rem 1rem !important;
  box-shadow: 0 14px 30px rgba(201,162,77,0.25) !important;
}
.stApp.login-mode div[data-testid="stFormSubmitButton"] > button:hover{
  background: #111 !important;
  color: var(--accent) !important;
}

/* login page regular buttons (like "Create account") */
.stApp.login-mode section.main div[data-testid="stButton"] > button{
  width: 100% !important;
  border-radius: 16px !important;
  font-weight: 800 !important;
  background: transparent !important;
  border: 1px solid rgba(0,0,0,0.18) !important;
  color: #111 !important;
  box-shadow: none !important;
}
.stApp.login-mode section.main div[data-testid="stButton"] > button:hover{
  border-color: rgba(201,162,77,0.9) !important;
  color: rgba(201,162,77,1) !important;
}
/* ================= CTA WRAPPERS  ================= */
.cta-wrap div[data-testid="stButton"] > button{
  background: var(--accent) !important;
  color: #111 !important;
  border-radius: 40px !important;
  font-weight: 800 !important;
  border: none !important;
  box-shadow: 0 10px 25px rgba(201,162,77,0.25) !important;
  width: 100% !important;
}
.cta-wrap div[data-testid="stButton"] > button:hover{
  background: #111 !important;
  color: var(--accent) !important;
}

.cta-soft div[data-testid="stButton"] > button{
  background: transparent !important;
  border: 1px solid rgba(0,0,0,0.18) !important;
  color: #111 !important;
  border-radius: 16px !important;
  font-weight: 800 !important;
  width: 100% !important;
  box-shadow: none !important;
}
.cta-soft div[data-testid="stButton"] > button:hover{
  border-color: rgba(201,162,77,0.9) !important;
  color: rgba(201,162,77,1) !important;
}
/* ================= FAVORITES ================= */
      .fav-badge{
  position:absolute;
  top:12px;
  left:12px;  /* אם תרצי בימין: החליפי ל right:12px ומחקי left */
  z-index:70;
}
.fav-pill{
  display:flex;
  align-items:center;
  justify-content:center;
  width:44px;
  height:32px;
  border-radius:999px;
  border:1px solid rgba(255,255,255,0.55);
  background: rgba(255,255,255,0.22);
  backdrop-filter: blur(6px);
  cursor:pointer;
  user-select:none;
  font-size:18px;
  line-height:1;
}
.fav-pill:hover{ background: rgba(255,255,255,0.32); }

.recipe-wrap{ position: relative; }

.heart-slot{
  position: absolute;
  top: 12px;
  left: 12px;
  z-index: 90;
}

/* לב — שלא יקבל את עיצוב הזהב של כל הכפתורים */
.heart-slot div[data-testid="stButton"] > button{
  all: unset !important;
  cursor: pointer !important;
  font-size: 22px !important;
  line-height: 1 !important;
  padding: 6px 10px !important;
  border-radius: 999px !important;
  background: rgba(255,255,255,0.22) !important;
  border: 1px solid rgba(255,255,255,0.55) !important;
  backdrop-filter: blur(6px) !important;
}
            .fav-badge{
  position:absolute;
  top:12px;
  left:12px;
  z-index:80;
}

.fav-link{
  display:flex;
  align-items:center;
  justify-content:center;
  width:42px;
  height:34px;
  border-radius:999px;
  border:1px solid rgba(255,255,255,0.55);
  background: rgba(255,255,255,0.22);
  backdrop-filter: blur(6px);
  text-decoration:none !important;
  font-size:22px;
  line-height:1;
}
.fav-link:hover{ background: rgba(255,255,255,0.32); }
div[data-testid="stMain"] div.stButton > button,
div[data-testid="stMain"] div[data-testid="stButton"] > button,
div[data-testid="stMain"] button[data-testid^="baseButton"],
div[data-testid="stMain"] button[kind="primary"],
div[data-testid="stMain"] button[kind="secondary"]{
  background-color: #D4AF37 !important;
  background-image: linear-gradient(135deg, #D4AF37, #F5D76E) !important;
  color: #2b2b2b !important;
  border: none !important;
  border-radius: 14px !important;
  font-weight: 700 !important;
  padding: 0.75em 1.5em !important;
  box-shadow: 0 4px 10px rgba(212,175,55,0.35) !important;
  transition: all 0.2s ease-in-out !important;
}

div[data-testid="stMain"] div.stButton > button:hover,
div[data-testid="stMain"] div[data-testid="stButton"] > button:hover,
div[data-testid="stMain"] button[data-testid^="baseButton"]:hover,
div[data-testid="stMain"] button[kind="primary"]:hover,
div[data-testid="stMain"] button[kind="secondary"]:hover{
  background-color: #F5D76E !important;
  background-image: linear-gradient(135deg, #F5D76E, #D4AF37) !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 6px 14px rgba(212,175,55,0.5) !important;
}
}
</style>
""", unsafe_allow_html=True)

local_css()

def set_login_mode(enabled: bool):
    st.markdown(
        f"""
        <script>
          (function() {{
            const app = window.parent.document.querySelector('.stApp');
            if (!app) return;
            app.classList.toggle('login-mode', {str(enabled).lower()});
          }})();
        </script>
        """,
        unsafe_allow_html=True
    )
def can_delete_review(r: dict) -> bool:
    my_id = st.session_state.get("user_id")
    return (
        st.session_state.get("role") == "admin"
        or (my_id is not None and r.get("user_id") == my_id)
    )

def delete_review(review_id: int):
    return requests.delete(f"{BASE_URL}/reviews/{review_id}", headers=auth_headers())

def render_review_box(rating: int, comment: str) -> str:
    full_star = "⭐"
    empty_star = "☆"
    stars = full_star * rating + empty_star * (5 - rating)

    return f"""
<div style="
    background: #fff8e6;
    padding: 12px 16px;
    border-radius: 12px;
    margin-bottom: 10px;
    border-left: 4px solid #f1b94e;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
">
    <div style="font-size: 1.3rem; margin-bottom: 4px;">{stars}</div>
    <div style="font-size: 1rem; color: #333;">{comment}</div>
</div>
"""
@st.cache_data(ttl=60, show_spinner=False)
def fetch_recipes():
    response = requests.get(
    RECIPES_URL,
    headers=auth_headers()
    )
    response.raise_for_status()
    return response.json() 

@st.cache_data(ttl=120)
def fetch_reviews(recipe_id):
    res = requests.get(f"{RECIPES_URL}/{recipe_id}/reviews",
    headers=auth_headers())
    if res.status_code == 200:
        return res.json()

@st.cache_data(ttl=120, show_spinner=False)
def fetch_highlights():
    res = requests.get(f"{BASE_URL}/highlights",
    headers=auth_headers())
    if res.status_code == 200:
        return res.json()
    return []

@st.cache_data(ttl=300, show_spinner=False)
def fetch_recommendations(limit: int = 3):
    res = requests.get(
        f"{BASE_URL}/recommendations",
        params={"limit": limit},
        headers=auth_headers(),
        timeout=15
    )
    res.raise_for_status()
    data = res.json()
    return data.get("recommendations", []) if isinstance(data, dict) else []

@st.cache_data(ttl=60, show_spinner=False)
def fetch_recipe_by_id(recipe_id: int):
    res = requests.get(
        f"{BASE_URL}/recipes/{recipe_id}",
        headers=auth_headers(),
        timeout=15
    )
    res.raise_for_status()
    return res.json()

# ------------------------
# 3. SIDEBAR NAVIGATION
# ------------------------
with st.sidebar:
    st.markdown('<div class="sidebar-title">🍽️ CookWithMe</div>', unsafe_allow_html=True)
    st.markdown('<div class="signature">by Yahav</div>', unsafe_allow_html=True)
    st.write("Welcome to my digital kitchen.")
    st.markdown("---")
    name = st.session_state.get("user_name")
    if name:
        st.write(f"Hi, {name} 👋")

    if st.session_state.get("token"):
        if st.button("📖 All Recipes", use_container_width=True):
            st.query_params.clear()
            
            st.session_state.page = "list"
            st.session_state.search_query = "" 
            st.session_state.filter_choice = "All"  
            st.rerun()

        if st.session_state.get("role") == "admin":
            if st.button("➕ Add New Recipe", use_container_width=True):
                st.session_state.page = "add"
                st.rerun()

        if st.button("❤️ Favorites", use_container_width=True):
            st.session_state.page = "favorites"
            st.rerun()

        if st.button("🤖 AI Recommendations", use_container_width=True):
            st.session_state.page = "recommendations"
            st.rerun()

        if st.button("🚪 Logout"):
            st.session_state.clear()
            st.query_params.clear()
            components.html("""
            <script>
                try { window.parent.localStorage.removeItem("cwm_token"); } catch(e) {}
                window.parent.location.href = window.parent.location.origin;
            </script>
            """, height=0)
            st.stop()

    st.markdown("---")
    st.caption("Developed with ❤️ using Streamlit")


set_login_mode(st.session_state.get("page") in ("login", "signup"))


# ------------------------
# PAGE: LOGIN
# ------------------------
if st.session_state.page == "login":

    st.markdown('<h1 class="login-title">🍽️ CookWithMe</h1>', unsafe_allow_html=True)
    st.markdown('<div class="login-subtitle">Sign in to your digital kitchen</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-accent"></div>', unsafe_allow_html=True)

    # ---- ONE FORM ONLY ----
    with st.form("login_form"):
        email = st.text_input("Email", placeholder="name@example.com")
        password = st.text_input("Password", type="password", placeholder="••••••••")

        st.markdown('<div class="cta-wrap">', unsafe_allow_html=True)
        submit = st.form_submit_button("Login", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ---- handle submit OUTSIDE the form ----
    if submit:
        if not email.strip() or not password:
            st.error("Please enter Email and Password")
        else:
            try:
                res = requests.post(
                    f"{BASE_URL}/auth/login",
                    json={"email": email.strip(), "password": password},
                    timeout=10
                )

                if res.status_code == 200:
                    data = res.json()
                    token = data.get("access_token")
                    if not token:
                        st.error("Login succeeded but there is no token")
                    else:
                        st.session_state.token = token
                        components.html(
                        f"""
                        <script>
                          try {{
                            window.parent.localStorage.setItem("cwm_token", {token!r});
                        }} catch(e) {{}}
                        </script>
                        """,
                        height=0,
                        )

                        payload = jwt.decode(token, options={"verify_signature": False})
                        st.session_state.user_id = int(payload.get("sub")) if payload.get("sub") else None 
                        st.session_state.role = payload.get("role", "user")
                        st.session_state.user_name = payload.get("name", "")  
                        st.session_state.is_admin = (st.session_state.role == "admin")
                        st.cache_data.clear()
                        st.session_state.page = "list"
                        hl_after = st.session_state.pop("post_login_hl", None)
                        new_url = "/"
                        if hl_after:
                            new_url = f"/?hl={hl_after}"
                            
                        components.html(
                            f"""
                            <script>
                                (function() {{
                                    const target = "{new_url}";
                                    window.parent.history.replaceState({{}}, "", target);
                                }})();
                            </script>
                            """,
                            height=0,
                        )
                        st.session_state.page = "list"
                        st.rerun()
                            
                        st.stop() # עוצר את הריצה הנוכחית כדי שה-JS יתבצע
                elif res.status_code == 401:
                    st.error("Email or Password incorrect")

                elif res.status_code == 422:
                    st.error("Check your Email and Password")
                    st.caption(res.text)

                elif res.status_code == 404:
                    st.error("Endpoint problem")
                    st.caption(f"BASE_URL = {BASE_URL}")

                else:
                    st.error(f"Server error ({res.status_code}): {res.text}")

            except requests.exceptions.ConnectionError:
                st.error("Backend not reachable. Is it running on 127.0.0.1:8000?")
            except requests.exceptions.Timeout:
                st.error("Request timed out")
            except Exception as e:
                st.error(f"Unexpected error: {e}")

    # ---- Create account (ALWAYS visible) ----
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    st.markdown('<div class="cta-soft">', unsafe_allow_html=True)
    create = st.button("📝 Create account", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if create:
        st.session_state.page = "signup"
        st.rerun()
    
# ------------------------
# PAGE: SIGNUP
# ------------------------
if st.session_state.page == "signup":
    st.markdown("<h1 style='text-align:center;'>🍽️ CookWithMe</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>Create account</h3>", unsafe_allow_html=True)

    with st.form("signup_form"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submit = st.form_submit_button("Sign up")

    if submit:
        name_clean = (name or "").strip()
        email_clean = (email or "").strip()

        # ---- basic validations ----
        if not name_clean:
            st.error("Please fill Name")
        elif not email_clean or not password or not confirm_password:
            st.error("Please fill Email + Password + Confirm Password")
        elif password != confirm_password:
            st.error("Passwords do not match")
        elif len(password) < 6:
            st.error("Password must be at least 6 characters")
        else:
            try:
                res = requests.post(
                    f"{BASE_URL}/auth/register",
                    json={"email": email_clean, "password": password, "name": name_clean},
                    timeout=10
                )

                if res.status_code == 201:
                    st.success("Account created ✅ You can log in now.")
                    st.session_state.page = "login"
                    st.rerun()

                elif res.status_code == 409:
                    detail = ""
                    try:
                        detail = res.json().get("detail", "")
                    except Exception:
                        pass
                    st.error(detail or "This email is already registered. Try logging in.")

                elif res.status_code == 422:
                    st.error("Invalid input (check name/email format / password rules)")
                    try:
                        st.caption(res.json())
                    except Exception:
                        st.caption(res.text)

                elif res.status_code == 404:
                    st.error("Endpoint problem")
                    st.caption(f"BASE_URL = {BASE_URL}")

                else:
                    try:
                        msg = res.json().get("detail", res.text)
                    except Exception:
                        msg = res.text
                    st.error(f"Server error ({res.status_code}): {msg}")

            except requests.exceptions.ConnectionError:
                st.error("Cannot reach server. Check that backend is running on 127.0.0.1:8000")
            except requests.exceptions.Timeout:
                st.error("Request timed out (server too slow / not responding)")
            except Exception as e:
                st.error(f"Unexpected error: {e}")

    st.markdown("---")
    if st.button("🔐 Back to Login"):
        st.session_state.page = "login"
        st.rerun()
# ------------------------
# PAGE: LIST RECIPES
# ------------------------
if st.session_state.page == "list":

    hl_q = st.query_params.get("hl")
    if hl_q:
        try:
            st.session_state.selected_highlight_id = int(hl_q)
        except Exception:
            st.session_state.selected_highlight_id = None
    favorites = get_favorites()
    favorite_ids = {r["id"] for r in favorites}
    if "selected_highlight_id" not in st.session_state:
        st.session_state.selected_highlight_id = None
    hl_id = st.session_state.selected_highlight_id
    # --- handle favorite toggle from URL ---
    fav_q = st.query_params.get("fav")
    if fav_q:
        try:
            fav_id = int(fav_q)
            favorites_now = get_favorites()
            fav_ids_now = {r["id"] for r in favorites_now}

            if fav_id in fav_ids_now:
                remove_favorite(fav_id)
            else:
                add_favorite(fav_id)

            st.cache_data.clear()

            # remove fav param so it won't repeat on refresh
            st.query_params.pop("fav", None)
            st.rerun()
        except Exception:
            st.query_params.pop("fav", None)
        highlights = fetch_highlights()
    # -------- TITLE --------
    st.markdown(""" 
    <div style="text-align:center; margin: 50px 0 10px 0;">
        <h1 style="font-size: 3rem; font-weight: 800; color: #1e1e1e;">
            My Recipe Book
        </h1>
        <div style="height: 4px; width: 170px; background: #c9a24d; margin: 0 auto;"></div>
    </div>
    """, unsafe_allow_html=True)
    # -------- HIGHLIGHTS --------
    highlights = fetch_highlights()
    if highlights:
        cols = st.columns(min(len(highlights), 6), gap="large")

        for i, h in enumerate(highlights):
            with cols[i % len(cols)]:
                cover = h.get("cover_url") or "/static/covers/default.jpg"
                hid = int(h["id"])

                # קליק = toggle query param בלי ניווט מלא
                toggle_js = f"""
    <script>
    (function(){{
    const u = new URL(window.parent.location.href);
    const cur = u.searchParams.get('hl');

    if (cur === '{hid}') {{
        u.searchParams.delete('hl');
    }} else {{
        u.searchParams.set('hl', '{hid}');
    }}

    // לעדכן URL בלי reload
    window.parent.history.replaceState({{}}, '', u.pathname + u.search);
    }})();
    </script>
    """

                clicked = st.button(" ", key=f"hl_{hid}", help="Open highlight")
                st.markdown(
                    f"""
    <div class="hl-wrap">
    <div class="hl-visual">
        <div class="ring">
        <div class="inner" style="background-image:url('{cover}')"></div>
        </div>
    </div>
    </div>
    """,
                    unsafe_allow_html=True
                )

                if clicked:
                    # עדכון query params בצד של Streamlit (שומר session!)
                    if hl_id == hid:
                        st.query_params.pop("hl", None)
                        st.session_state.selected_highlight_id = None
                    else:
                        st.query_params["hl"] = str(hid)
                        st.session_state.selected_highlight_id = hid

                    # לעדכן גם את ה-URL בדפדפן (בשביל שיראה ?hl=)
                    components.html(toggle_js, height=0)

                    st.rerun()
    # -------- VIDEO PLAYER --------
    if hl_id is not None:

        # Close highlight (בלי href, בלי ניווט מלא)
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if st.button("✖ Close highlight", use_container_width=True, key="close_hl"):
                # לנקות state + query params של Streamlit
                st.session_state.selected_highlight_id = None
                st.query_params.pop("hl", None)

                # לנקות גם URL בדפדפן בלי reload
                components.html("""
                <script>
                try {
                    const u = new URL(window.parent.location.href);
                    u.searchParams.delete('hl');
                    window.parent.history.replaceState({}, '', u.pathname + u.search);
                } catch(e) {}
                </script>
                """, height=0)

                st.rerun()

        # לבחור את ההיילייט הנבחר
        selected = next((h for h in highlights if int(h.get("id", -1)) == int(hl_id)), None)

        if not selected:
            st.error("Selected highlight not found (id mismatch).")
        else:
            url = selected.get("video_url")

            # אופציונלי: הדפסה זמנית לדיבאג (תורידי אחרי שמסתדר)
            # st.caption(f"DEBUG video_url: {url}")

            if not url:
                st.error("This highlight has no video_url.")
            else:
                col_left, col_center, col_right = st.columns([1.5, 2, 1.5])
                with col_center:
                    # ✅ הכי יציב ב־Streamlit במקום <video> ב-HTML
                    st.video(url)
    # -------- RECIPES --------
    try:
        with st.spinner("🍳 Loading recipes..."):
            recipes = fetch_recipes()
        favorites = get_favorites()
        favorite_ids = {r["id"] for r in favorites}
        col_filter, col_search, _ = st.columns([1, 2, 3])

        with col_filter:
            filter_choice = st.selectbox(
                "Filter by Difficulty:",
                ["All", "Easy", "Medium", "Hard"]
            )

        with col_search:
            if "search_query" not in st.session_state:
                st.session_state.search_query = ""

            search_input = st.text_input(
                "🔎 Search recipe by name",
                value=st.session_state.search_query
            )

            if st.button("Search"):
                st.session_state.search_query = search_input

        cols = st.columns(3)
        recipes_displayed = 0

        for recipe in recipes:
            if not (
                (filter_choice == "All" or recipe["difficulty"] == filter_choice)
                and (
                    st.session_state.search_query.strip() == ""
                    or st.session_state.search_query.lower() in recipe["title"].lower()
                )
            ):
                continue
            
            with cols[recipes_displayed % 3]:
                difficulty = recipe["difficulty"]
                is_fav = recipe["id"] in favorite_ids
                heart = "❤️" if is_fav else "🤍"

                card_html = f"""<div class="recipe-card">
                    <div style="position: relative;">
                        <img src="{recipe['image_url']}" loading="lazy"
                            style="width:100%; height:200px; object-fit:cover;">
                        <span class="badge bg-{difficulty}">{difficulty}</span>
                        <div class="fav-badge">
                            <a class="fav-link" href="?fav={recipe['id']}" target="_self">{heart}</a>
                        </div>
                    </div>
                    <div style="padding:15px;">
                        <div style="color:#777; font-size:0.9rem;">
                            ⏱️ {recipe['time_minutes']} minutes • ⭐ {recipe.get('avg_rating', 0)} ({recipe.get('reviews_count', 0)})
                        </div>
                </div>"""

                st.markdown(card_html, unsafe_allow_html=True)

                if st.button("View Recipe 👈", key=f"btn_{recipe['id']}", use_container_width=True):
                    st.session_state.selected_recipe_id = recipe["id"]
                    st.session_state.edit_mode = False
                    st.session_state.page = "details"
                    st.rerun()
            recipes_displayed += 1

        if recipes_displayed == 0:
            st.warning(f"No recipes found with difficulty: {filter_choice}")

    except requests.exceptions.RequestException:
        st.error("❌ Connection error. Is the server running?")

# ------------------------
# PAGE: FAVORITES
# ------------------------
elif st.session_state.page == "favorites":
    if st.button("⬅️ Back"):
        st.session_state.page = "list"
        st.rerun()

    st.markdown("""
    <div style="text-align:center; margin: 35px 0 10px 0;">
        <h1 style="font-size: 2.6rem; font-weight: 800; color: #1e1e1e;">
             My Favorites ❤️
        </h1>
        <div style="height: 4px; width: 170px; background: #c9a24d; margin: 0 auto;"></div>
    </div>
    """, unsafe_allow_html=True)

    try:
        favorites = get_favorites()  
        if not favorites:
            st.info("No favorites yet. Tap 🤍 on a recipe to save it.")
            st.stop()

        cols = st.columns(3)
        displayed = 0

        for recipe in favorites:
            with cols[displayed % 3]:
                difficulty = recipe.get("difficulty", "Easy")
                tok = st.session_state.get("token", "")

                card_html = f"""<div class="recipe-card">
                    <div style="position: relative;">
                        <img src="{recipe['image_url']}" loading="lazy"
                            style="width:100%; height:200px; object-fit:cover;">
                        <span class="badge bg-{difficulty}">{difficulty}</span>
                        <div class="fav-badge">
                            <a class="fav-link" href="?fav={recipe['id']}" target="_self">❤️</a>
                        </div>
                    </div>
                    <div style="padding:15px;">
                        <div class="card-title">{recipe['title']}</div>
                        <div style="color:#777; font-size:0.9rem;">⏱️ {recipe['time_minutes']} minutes</div>
                    </div>
                </div>"""

                st.markdown(card_html, unsafe_allow_html=True)

                if st.button("View Recipe 👈", key=f"btn_{recipe['id']}", use_container_width=True):
                    st.session_state.selected_recipe = recipe
                    st.session_state.selected_recipe_id = recipe["id"]
                    st.session_state.edit_mode = False
                    st.session_state.page = "details"
                    st.rerun()

            displayed += 1

    except Exception as e:
        st.error(f"Failed to load favorites: {e}")


# ------------------------
# PAGE: AI
# ------------------------
elif st.session_state.page == "recommendations":
    if st.button("⬅️ Back"):
        st.session_state.page = "list"
        st.rerun()

    st.markdown("""
    <div style="text-align:center; margin: 35px 0 10px 0;">
        <h1 style="font-size: 2.6rem; font-weight: 800; color: #1e1e1e;">
             AI Picks For You 🤖✨
        </h1>
        <div style="height: 4px; width: 170px; background: #c9a24d; margin: 0 auto;"></div>
    </div>
    """, unsafe_allow_html=True)
    st.write("Based on what you watched recently")

    try:
        with st.spinner("Cooking up recommendations..."):
            recs = fetch_recommendations(limit=3)

        if not recs:
            st.info("No recommendations yet. Watch a few recipes and try again 🙂")
            st.stop()

        cols = st.columns(3)
        for i, recipe in enumerate(recs):
            with cols[i % 3]:
                difficulty = recipe.get("difficulty", "Easy")

                card_html = f"""<div class="recipe-card">
                    <div style="position: relative;">
                        <img src="{recipe.get('image_url','')}" loading="lazy"
                            style="width:100%; height:200px; object-fit:cover;">
                        <span class="badge bg-{difficulty}">{difficulty}</span>
                    </div>
                    <div style="padding:15px;">
                        <div style="color:#777; font-size:0.9rem;">
                            ⏱️ {recipe.get('time_minutes', 0)} minutes • ⭐ {recipe.get('avg_rating', 0)} ({recipe.get('reviews_count', 0)})
                        </div>
                    </div>
                </div>"""

                st.markdown(card_html, unsafe_allow_html=True)

                if st.button("View Recipe 👈", key=f"rec_btn_{recipe['id']}", use_container_width=True):
                    st.session_state.selected_recipe_id = recipe["id"]
                    st.session_state.prev_page = "recommendations"  
                    st.session_state.page = "details"
                    st.rerun()

    except requests.exceptions.HTTPError as e:
        st.error("Failed to load AI recommendations.")
        st.caption(str(e))
    except Exception as e:
        st.error(f"Unexpected error: {e}")


# ------------------------
# PAGE: DETAILS
# ------------------------
elif st.session_state.page == "details":

    if st.button("⬅️ Back"):
        st.session_state.page = st.session_state.get("prev_page", "list")
        st.rerun()

    rid = st.session_state.get("selected_recipe_id")
    if not rid:
        st.session_state.page = "list"
        st.rerun()

    recipe = fetch_recipe_by_id(rid) 

    # -------------------------------------------------
    # ✅ EDIT MODE
    # -------------------------------------------------
    if st.session_state.get('edit_mode'):

        st.subheader("📝 Edit Recipe")

        with st.form("edit_recipe_form"):
            new_title = st.text_input("Recipe Title", value=recipe.get('title', ''))
            new_time = st.number_input(
                "Prep Time (minutes)",
                min_value=1,
                value=int(recipe.get('time_minutes', 30))
            )

            st.markdown("### Change Image")
            st.image(recipe.get('image_url') or "https://via.placeholder.com/150", width=150)
            new_image_file = st.file_uploader("Upload New Image", type=['png', 'jpg', 'jpeg'])

            current_ingredients = recipe.get('ingredients', [])
            if isinstance(current_ingredients, list):
                current_ingredients = "\n".join(current_ingredients)

            new_ingredients = st.text_area("Ingredients", value=current_ingredients, height=150)
            new_instructions = st.text_area("Instructions", value=recipe.get('instructions_md', ''), height=150)

            difficulty_options = ["Easy", "Medium", "Hard"]
            current_diff = recipe.get('difficulty')
            idx = difficulty_options.index(current_diff) if current_diff in difficulty_options else 0
            new_difficulty = st.selectbox("Difficulty", difficulty_options, index=idx)

            col1, col2 = st.columns(2)

            with col1:
                save_btn = st.form_submit_button("💾 Save", use_container_width=True)
            with col2:
                cancel_btn = st.form_submit_button("❌ Cancel", use_container_width=True)

            if cancel_btn:
                st.session_state.edit_mode = False
                st.rerun()

            if save_btn:
                final_image_url = recipe.get('image_url')

                if new_image_file is not None:
                    try:
                        image = Image.open(new_image_file)
                        if image.mode in ("RGBA", "P"):
                            image = image.convert("RGB")

                        max_width = 800
                        if image.width > max_width:
                            ratio = max_width / float(image.width)
                            new_height = int(float(image.height) * ratio)
                            image = image.resize((max_width, new_height), Image.Resampling.LANCZOS)

                        buffered = io.BytesIO()
                        image.save(buffered, format="JPEG", quality=70)
                        base64_str = base64.b64encode(buffered.getvalue()).decode()
                        final_image_url = f"data:image/jpeg;base64,{base64_str}"

                    except Exception as e:
                        st.error(f"Image error: {e}")
                        st.stop()

                ingredients_list = [line for line in new_ingredients.split("\n") if line.strip()]

                updated_data = {
                    "title": new_title,
                    "time_minutes": new_time,
                    "ingredients": ingredients_list,
                    "instructions_md": new_instructions,
                    "difficulty": new_difficulty,
                    "image_url": final_image_url
                }

                try:
                    response = requests.put(f"{RECIPES_URL}/{st.session_state.selected_recipe_id}", json=updated_data,headers=auth_headers())

                    response.raise_for_status()

                    st.success("✅ Updated!")
                    st.session_state.selected_recipe = response.json()
                    st.session_state.edit_mode = False
                    st.rerun()

                except Exception as e:
                    st.error(f"Update failed: {e}")

    # -------------------------------------------------
    # VIEW MODE
    # -------------------------------------------------
    else:
        recipe_id = st.session_state.selected_recipe_id
        if st.button("⬅️ Back to recipes list"):
            st.session_state.page = "list"
            st.rerun()

        img_url = recipe.get('image_url') or "https://via.placeholder.com/800x400?text=No+Image"

        # HERO SECTION
        st.markdown(f"""
<div style="position: relative; width: 100%; border-radius: 32px; overflow: hidden; margin-bottom: 45px; box-shadow: 0 25px 60px rgba(0,0,0,0.25);">
<div style="height: 420px; background: linear-gradient(to bottom, rgba(0,0,0,0.15), rgba(0,0,0,0.75)), url('{img_url}'); background-size: cover; background-position: center; display: flex; flex-direction: column; justify-content: flex-end; padding: 0 30px 40px 30px; color: white; text-align: center;">
<div style="max-width: 600px; margin: 0 auto; display: flex; flex-direction: column; gap: 2px;">
<div style="display: inline-block; background: rgba(0,0,0,0.40); padding: 4px 12px; border-radius: 14px; backdrop-filter: blur(5px); border: 1px solid rgba(255,255,255,0.18); box-shadow: 0 6px 14px rgba(0,0,0,0.35);">
<h1 style="font-size: 2.4rem; font-weight: 800; margin: 0; color: white; letter-spacing: -0.5px;">{recipe.get('title')}</h1>
</div>
<div style="margin-top: 20px; font-size: 1.2rem; background: rgba(255,255,255,0.15); display: inline-block; padding: 10px 25px; border-radius: 40px; border: 1px solid rgba(255,255,255,0.25); backdrop-filter: blur(5px);">
⏱️ {recipe.get('time_minutes')} min • 🔥 {recipe.get('difficulty')}
</div>
</div>
</div>
""", unsafe_allow_html=True)

        col_ing, col_inst = st.columns([1, 2])

        # INGREDIENTS COLUMN
        with col_ing:
            ingredients = recipe.get('ingredients', [])
            
            ingredients_html = """
<div style="background: linear-gradient(180deg, #ffffff 0%, #faf7f2 100%); padding: 26px; border-radius: 22px; box-shadow: 0 14px 30px rgba(0,0,0,0.07); border: 1px solid rgba(0,0,0,0.03);">
<div style="display: flex; align-items: center; gap: 10px; font-size: 1.3rem; font-weight: 800; margin-bottom: 18px; color: #1e1e1e;">🛒 Ingredients</div>
<ul style="list-style: none; padding: 0; margin: 0; display: grid; gap: 10px; font-size: 1rem; color: #333;">
"""
            
            if isinstance(ingredients, list):
                for item in ingredients:
                    ingredients_html += f"""
<li style="display: flex; align-items: center; gap: 10px; background: rgba(0,0,0,0.02); padding: 8px 12px; border-radius: 12px;">
<span style="background: #3a7d44; color: white; font-size: 0.75rem; padding: 4px 7px; border-radius: 6px;">✓</span>
<span>{item}</span>
</li>"""
            else:
                ingredients_html += f"<li>{ingredients}</li>"

            ingredients_html += "</ul></div>"
            st.markdown(ingredients_html, unsafe_allow_html=True)

        # INSTRUCTIONS COLUMN
        with col_inst:
            st.markdown("### 👨‍🍳 Instructions")
            with st.container():
                st.markdown(recipe.get('instructions_md', 'No instructions.'))

        st.divider()
        if st.session_state.get("role") == "admin":
            col_del, col_upd = st.columns([1, 4])
            with col_del:
                if st.button("🗑️ Delete", type="primary", use_container_width=True):
                    try:
                        requests.delete(f"{RECIPES_URL}/{st.session_state.selected_recipe_id}",headers=auth_headers())
                        st.success("Deleted!")
                        st.session_state.page = "list"
                        st.rerun()
                    except:
                        st.error("Delete failed")

            with col_upd:
                if st.button("✏️ Edit", use_container_width=True):
                    st.session_state.edit_mode = True
                    st.rerun()

        # ------------------------
        # REVIEW SECTION
        # ------------------------
        st.divider()
        st.subheader("💬 Reviews")

        reviews = fetch_reviews(recipe_id)

        if reviews:
            for r in reviews:
                author = r.get("author_email", "Unknown")
                comment = r.get("comment", "")
                rating = r.get("rating", 0)

                # מציגים כותב + תגובה בתוך אותה קופסה
                combined_comment = f"<b>{author}</b><br>{comment}"
                st.markdown(render_review_box(rating, combined_comment), unsafe_allow_html=True)

                # כפתור מחיקה רק לבעל התגובה / אדמין
                if can_delete_review(r):
                    cols = st.columns([1, 6])
                    with cols[0]:
                        if st.button("🗑️", key=f"del_review_{r['id']}", help="Delete review"):
                            res = delete_review(r["id"])
                            if res.status_code in (200, 204):
                                st.cache_data.clear()
                                st.rerun()
                            else:
                                st.error(res.text)
        else:
            st.info("No reviews yet. Be the first!")


        # ------------------------
        # ADD A REVIEW (DESIGNED)
        # ------------------------
        st.markdown("---")
        st.markdown("### Add a Review")

        if "rating" not in st.session_state:
            st.session_state.rating = 0

        cols = st.columns(5, gap="small")
        for i, col in enumerate(cols):
            with col:
                star = "⭐" if st.session_state.rating >= i + 1 else "☆"
                if st.button(star, key=f"star_{i}", help=f"Rate {i+1}", use_container_width=True):
                    st.session_state.rating = i + 1

        with st.form("review_form", clear_on_submit=True):
            comment = st.text_area(
                "Write your review...",
                placeholder="How was the recipe?",
                height=120
            )

            submit = st.form_submit_button("Submit Review", use_container_width=True)

            if submit:
                if st.session_state.rating == 0:
                    st.error("Please select a rating ⭐")
                elif not comment.strip():
                    st.error("Please add a comment.")
                else:
                    payload = {"rating": st.session_state.rating, "comment": comment.strip()}
                    try:
                        res = requests.post(
                            f"{RECIPES_URL}/{recipe_id}/reviews",
                            json=payload,
                            headers=auth_headers()
                        )
                        if res.status_code in (200, 201):
                            st.success("Review added! ⭐")
                            st.cache_data.clear()
                            st.session_state.rating = 0   # יותר הגיוני לאפס
                            st.rerun()
                        else:
                            st.error(f"Failed to submit review: {res.text}")
                    except Exception as e:
                        st.error(f"Error: {e}")
# ------------------------
# PAGE: ADD RECIPE
# ------------------------
elif st.session_state.page == "add":
    st.markdown("<h2 style='text-align: center;'>➕ Add New Recipe</h2>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div style='background-color: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05);'>", unsafe_allow_html=True)
        
        with st.form("add_recipe_form", clear_on_submit=True):
            title = st.text_input("Recipe Title", placeholder="e.g., Chocolate Lava Cake")
            uploaded_file = st.file_uploader("Upload Image", type=['png', 'jpg', 'jpeg'])
            
            c1, c2 = st.columns(2)
            with c1:
                time_minutes = st.number_input("Prep Time (minutes)", min_value=1, value=30)
            with c2:
                difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])

            ingredients_text = st.text_area("Ingredients (One per line)", height=150)
            instructions = st.text_area("Instructions (Markdown supported)", height=150)

            submitted = st.form_submit_button("Save Recipe 🎉", use_container_width=True)

            if submitted:
                if not title or not ingredients_text or not instructions:
                    st.error("Please fill in all required fields.")
                else:
                    final_image_url = "https://images.unsplash.com/photo-1495521821757-a1efb6941752?auto=format&fit=crop&w=800&q=80"
                    
                    if uploaded_file is not None:
                        try:
                            image = Image.open(uploaded_file)
                            if image.mode in ("RGBA", "P"):
                                image = image.convert("RGB")
                            
                            max_width = 800
                            if image.width > max_width:
                                ratio = max_width / float(image.width)
                                new_height = int(float(image.height) * ratio)
                                image = image.resize((max_width, new_height), Image.Resampling.LANCZOS)
                            
                            buffered = io.BytesIO()
                            image.save(buffered, format="JPEG", quality=70)
                            base64_str = base64.b64encode(buffered.getvalue()).decode()
                            final_image_url = f"data:image/jpeg;base64,{base64_str}"
                        except Exception as e:
                            st.error(f"Error processing image: {e}")
                            st.stop()

                    ingredients_list = [line.strip() for line in ingredients_text.split("\n") if line.strip()]
                    
                    new_recipe_data = {
                        "title": title,
                        "time_minutes": time_minutes,
                        "ingredients": ingredients_list,
                        "instructions_md": instructions,
                        "difficulty": difficulty,
                        "image_url": final_image_url
                    }
                    
                    try:
                        response = requests.post(RECIPES_URL, json=new_recipe_data,headers=auth_headers())
                        response.raise_for_status()
                        st.success("Recipe Added Successfully!")
                        st.session_state.page = "list"
                        st.rerun()
                        
                    except requests.exceptions.RequestException as e:
                        st.error(f"Error saving recipe: {e}")

        st.markdown("</div>", unsafe_allow_html=True)