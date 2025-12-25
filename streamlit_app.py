import streamlit as st
import requests
import base64
from PIL import Image
import io
import textwrap
import os
import streamlit.components.v1 as components


# ------------------------
# 1. CONFIG & STATE
# ------------------------
if "page" not in st.session_state:
    st.session_state.page = "list"

st.set_page_config(page_title="CookWithMe", page_icon="🍽️", layout="wide")

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
RECIPES_URL = f"{BASE_URL}/recipes"
HIGHLIGHTS_URL = f"{BASE_URL}/highlights"


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
html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}
.stApp {
    background: var(--soft-bg);
    background-attachment: fixed;
}
[data-testid="stSidebar"] {
    background: #1e1e1e;
}
[data-testid="stSidebar"] * {
    color: white !important;
}
.sidebar-title {
     font-size: 1.7rem;              
    font-weight: 700;
    color: white;
    -webkit-text-stroke: 0.6px rgba(255,255,255,0.45);
    text-shadow: 
        0 2px 4px rgba(0,0,0,0.45), 
        0 0 12px rgba(201,162,77,0.40);
    display: flex;
    align-items: center;
    gap: 6px;
}
.signature {
    line-height: 2.6rem;
    font-family: 'Dancing Script', cursive !important;
    font-size: 1.5rem;
    color: #c9a24d !important;
    margin-top: -20px;
    margin-bottom: 20px;
    margin-left: 5px;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.15);
    transform: translateX(2px);
    letter-spacing: 0.5px;
}
h1 { color: #1e1e1e; font-weight: 800; letter-spacing: -1px; }
h2, h3 { color: var(--accent); }

.recipe-card {
    background: var(--card-bg);
    border-radius: 22px;
    box-shadow: 0 12px 40px rgba(0,0,0,0.06);
    transition: 0.4s ease;
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
.stButton button {
    background: var(--accent);
    color: black !important;
    border-radius: 40px;
    font-weight: 700;
    box-shadow: 0 10px 25px rgba(201, 162, 77, 0.3);
}
.stButton button:hover {
    background: black !important;
    color: var(--accent) !important;
}


[data-testid="stSidebar"] .stButton button {
    background-color: rgba(255, 255, 255, 0.2) !important;
    color: white !important;
    border: 1px solid white !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    background-color: white !important;
    color: var(--accent) !important;
}

.wrap {
    display: flex;
    justify-content: center;
    gap: 30px;
    margin: 30px 0;
    font-family: Poppins, sans-serif;
}

.hl {
    text-align: center;
    cursor: pointer;
}

.ring {
    width: 92px;
    height: 92px;
    border-radius: 50%;
    background: #d4af37;
    padding: 2px;
    box-sizing: border-box;
}

.inner {
    width: 100%;
    height: 100%;
    border-radius: 50%;
    background-size: cover;
    background-position: center;
    box-shadow: inset 0 0 0 2px rgba(255,255,255,0.9);
}

.hl:hover .ring {
    transform: scale(1.05);
    transition: 0.2s ease;
}

.title {
    margin-top: 8px;
    font-size: 0.8rem;
    font-weight: 600;
    color: #1e1e1e;
}

.star-row {
    display: flex;
    gap: 4px;              /* ⬅️ כאן שולטים על המרחק */
    align-items: center;
}

/* ביטול כל מרווח של Streamlit button */
.star-row .stButton {
    margin: 0 !important;
    padding: 0 !important;
}

/* הכפתור עצמו */
.star-row button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    font-size: 42px !important;
    padding: 0 !important;
    margin: 0 !important;
    min-width: unset !important;
}

/* hover */
.star-row button:hover {
    transform: scale(1.15);
}

</style>
""", unsafe_allow_html=True)

local_css()

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
    response = requests.get(RECIPES_URL)
    response.raise_for_status()
    return response.json() 

@st.cache_data(ttl=120)
def fetch_reviews(recipe_id):
    res = requests.get(f"{RECIPES_URL}/{recipe_id}/reviews")
    if res.status_code == 200:
        return res.json()

@st.cache_data(ttl=120, show_spinner=False)
def fetch_highlights():
    res = requests.get(f"{BASE_URL}/highlights")
    if res.status_code == 200:
        return res.json()
    return []

# ------------------------
# 3. SIDEBAR NAVIGATION
# ------------------------
with st.sidebar:
    st.markdown('<div class="sidebar-title">🍽️ CookWithMe</div>', unsafe_allow_html=True)
    st.markdown('<div class="signature">by Yahav</div>', unsafe_allow_html=True)
    st.write("Welcome to my digital kitchen.")
    st.markdown("---")
    
    if st.button("📖 All Recipes", use_container_width=True):
        st.query_params.clear()
        st.session_state.page = "list"
        st.session_state.search_query = "" 
        st.session_state.filter_choice = "All"  
        st.rerun()
        
    if st.button("➕ Add New Recipe", use_container_width=True):
        st.session_state.page = "add"
        st.rerun()
    
    st.markdown("---")
    st.caption("Developed with ❤️ using Streamlit")


# ------------------------
# PAGE: LIST RECIPES
# ------------------------
if st.session_state.page == "list":
    if "selected_highlight" not in st.session_state:
        st.session_state.selected_highlight = None
    hl = st.query_params.get("hl")
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
    if highlights:
        cards = ""
        for h in highlights:
            cards += f"""<a href="?hl={h['id']}#video" target="_self" style="text-decoration:none;">
            <div class="hl">
            <div class="ring">
            <div class="inner" style="background-image:url('{h.get("cover_url") or "/static/covers/default.jpg"}')"></div>
            </div>
            <div class="title">{h['title']}</div>
            </div>
            </a>"""

        st.markdown(
            f'<div class="wrap">{cards}</div>',
            unsafe_allow_html=True
        )
    # -------- VIDEO PLAYER --------
    if hl:
        try:
            hl_id = int(hl)
            selected = next((h for h in highlights if h["id"] == hl_id), None)
            if selected:
                st.markdown('<div id="video"></div>', unsafe_allow_html=True)
                st.markdown("### ▶️ Video")

                col_left, col_center, col_right = st.columns([1.5, 2, 1.5])
                with col_center:
                    st.markdown(
                        f"""
                        <video 
                            src="{selected['video_url']}"
                            controls
                            style="
                                width: 100%;
                                max-height: 65vh;
                                border-radius: 18px;
                                box-shadow: 0 20px 50px rgba(0,0,0,0.25);
                                background: black;
                            ">
                        </video>
                        """,
                        unsafe_allow_html=True
                    )
        except ValueError:
            pass
    # -------- RECIPES --------
    try:
        with st.spinner("🍳 Loading recipes..."):
            recipes = fetch_recipes()

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

                st.markdown(f"""
                <div class="recipe-card">
                    <div style="position: relative;">
                        <img src="{recipe['image_url']}" loading="lazy"
                             style="width:100%; height:200px; object-fit:cover;">
                        <span class="badge bg-{difficulty}">{difficulty}</span>
                    </div>
                    <div style="padding:15px;">
                        <div class="card-title">{recipe['title']}</div>
                        <div style="color:#777; font-size:0.9rem;">
                            ⏱️ {recipe['time_minutes']} minutes
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button( 
                    "View Recipe 👈",
                    key=f"btn_{recipe['id']}",
                    use_container_width=True 
                ): 
                    st.session_state.selected_recipe = recipe
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
# PAGE: DETAILS
# ------------------------
elif st.session_state.page == "details":
    
    # SAFETY CHECK
    if "selected_recipe" not in st.session_state:
        st.session_state.page = "list"

    recipe = st.session_state.selected_recipe

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
                    response = requests.put(f"{RECIPES_URL}/{st.session_state.selected_recipe_id}", json=updated_data)

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
        if st.button("⬅️ Back"):
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

        col_del, col_upd = st.columns([1, 4])
        with col_del:
            if st.button("🗑️ Delete", type="primary", use_container_width=True):
                try:
                    requests.delete(f"{RECIPES_URL}/{st.session_state.selected_recipe_id}")
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

        # הצגת ביקורות קיימות מהשרת
        reviews = fetch_reviews(recipe_id)
        if reviews:
            for r in reviews:
                st.markdown(render_review_box(r['rating'], r['comment']), unsafe_allow_html=True)
        else:
            st.info("No reviews yet. Be the first!")

        # ------------------------
        # ADD A REVIEW (DESIGNED)
        # ------------------------
        st.markdown("---")
        st.markdown("### Add a Review")

        if "rating" not in st.session_state:
            st.session_state.rating = 0

        # 5 עמודות צמודות
        cols = st.columns(5, gap="small")

        for i, col in enumerate(cols):
            with col:
                star = "⭐" if st.session_state.rating >= i + 1 else "☆"
                if st.button(
                    star,
                    key=f"star_{i}",
                    help=f"Rate {i+1}",
                    use_container_width=True
                ):
                    st.session_state.rating = i + 1
            st.markdown('</div>', unsafe_allow_html=True)

        with st.form("review_form", clear_on_submit=True):
            comment = st.text_area(
                "Write your review...",
                placeholder="How was the recipe?",
                height=120
            )

            submit = st.form_submit_button("Submit Review", use_container_width=True)

            if submit:
                if not comment:
                    st.error("Please add a comment.")
                else:
                    payload = {
                        "rating": st.session_state.rating,
                        "comment": comment
                    }
                    try:
                        res = requests.post(
                            f"{RECIPES_URL}/{recipe_id}/reviews",
                            json=payload
                        )
                        if res.status_code in (200, 201):
                            st.success("Review added! ⭐")
                            st.cache_data.clear()
                            st.session_state.rating = 5
                            st.rerun()
                        else:
                            st.error("Failed to submit review.")
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
                        response = requests.post(RECIPES_URL, json=new_recipe_data)
                        response.raise_for_status()
                        st.success("Recipe Added Successfully!")
                        st.session_state.page = "list"
                        st.rerun()
                        
                    except requests.exceptions.RequestException as e:
                        st.error(f"Error saving recipe: {e}")

        st.markdown("</div>", unsafe_allow_html=True)