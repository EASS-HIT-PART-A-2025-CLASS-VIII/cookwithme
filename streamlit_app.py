import streamlit as st
import requests
import base64
from PIL import Image
import io
import textwrap

# ------------------------
# 1. CONFIG & STATE
# ------------------------
if "page" not in st.session_state:
    st.session_state.page = "list"

st.set_page_config(page_title="CookWithMe", page_icon="🍽️", layout="wide")

API_URL = "http://127.0.0.1:8000/recipes"

# ------------------------
# 2. CUSTOM CSS
# -----------------------
def local_css():
    st.markdown(textwrap.dedent("""
    <style>
    :root {
        --main: #1e1e1e;
        --accent: #c9a24d;
        --soft-bg: #faf7f2;
        --card-bg: #ffffff;
    }

    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&family=Dancing+Script:wght@600&display=swap');

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

    .signature {
        font-family: 'Dancing Script', cursive;
        font-size: 2rem;
        color: white !important;
        margin-top: -20px;
        margin-bottom: 20px;
        margin-left: 5px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    }

    h1 { color: #1e1e1e; font-weight: 800; letter-spacing: -1px; }
    h2, h3 { color: var(--accent); }

    .recipe-card {
        background: var(--card-bg);
        border-radius: 22px;
        box-shadow: 0 12px 40px rgba(0,0,0,0.06);
        transition: 0.4s ease;
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
    </style>
    """), unsafe_allow_html=True)

local_css()

# ------------------------
# 3. SIDEBAR NAVIGATION
# ------------------------
with st.sidebar:
    st.title("🍽️ CookWithMe")
    st.markdown('<div class="signature">by Yahav</div>', unsafe_allow_html=True)
    st.write("Welcome to my digital kitchen.")
    st.markdown("---")
    
    if st.button("📖 All Recipes", use_container_width=True):
        st.session_state.page = "list"
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
    st.markdown("<h1 style='text-align: center; margin-bottom: 40px;'>My Recipe Book 🥗</h1>", unsafe_allow_html=True)

    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        recipes = response.json()
        
        col_filter, col_spacer = st.columns([1, 3])
        with col_filter:
            filter_choice = st.selectbox("Filter by Difficulty:", ["All", "Easy", "Medium", "Hard"])

        st.write("") 

        if not recipes:
            st.info("No recipes yet. Time to add your first one!")
        else:
            cols = st.columns(3)
            recipes_displayed = 0
            
            for index, recipe in enumerate(recipes):
                if filter_choice == "All" or filter_choice == recipe['difficulty']:
                    recipes_displayed += 1
                    with cols[index % 3]:
                        difficulty = recipe['difficulty']
                        
                        # שימוש ב-dedent כדי למנוע הצגת קוד HTML כטקסט
                        st.markdown(textwrap.dedent(f"""
                        <div class="recipe-card">
                            <div style="position: relative;">
                                <img src="{recipe['image_url']}" style="width: 100%; height: 200px; object-fit: cover;">
                                <span class="badge bg-{difficulty}">
                                    {difficulty}
                                </span>
                            </div>
                            <div style="padding: 15px;">
                                <div class="card-title">
                                    {recipe['title']}
                                </div>
                                <div style="color: #777; font-size: 0.9rem; display: flex; align-items: center; gap: 5px;">
                                    <span>⏱️</span> {recipe['time_minutes']} minutes
                                </div>
                            </div>
                        </div>
                        """), unsafe_allow_html=True)
                        
                        if st.button("View Recipe 👈", key=f"btn_{recipe['id']}", use_container_width=True):
                            st.session_state.selected_recipe = recipe
                            st.session_state.selected_recipe_id = recipe["id"]
                            st.session_state.edit_mode = False 
                            st.session_state.page = "details"
                            st.rerun()

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
        st.rerun()

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

            # Ingredients handling
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
                    response = requests.put(
                        f"{API_URL}/{st.session_state.selected_recipe_id}",
                        json=updated_data
                    )
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
        if st.button("⬅️ Back"):
            st.session_state.page = "list"
            st.rerun()

        img_url = recipe.get('image_url') or "https://via.placeholder.com/800x400?text=No+Image"

        # HERO SECTION
        # בניית ה-HTML בצורה צמודה לשמאל כדי למנוע בעיות הזחה
        hero_html = f"""
<div style="background: linear-gradient(to bottom, rgba(0,0,0,0.2), rgba(0,0,0,0.75)), url('{img_url}'); background-size: cover; background-position: center; border-radius: 30px; padding: 90px 30px 50px 30px; color: white; text-align: center; margin-bottom: 40px; box-shadow: 0 18px 40px rgba(0,0,0,0.2);">
    <h1 style="font-size: 2.6rem; font-weight: 800; color: white; margin: 0;">{recipe.get('title')}</h1>
    <div style="display: inline-block; margin-top: 10px; padding: 8px 20px; background: rgba(255,255,255,0.18); border-radius: 40px; font-size: 1.05rem; backdrop-filter: blur(5px);">
        ⏱️ {recipe.get('time_minutes')} min • 🔥 {recipe.get('difficulty')}
    </div>
</div>
"""
        st.markdown(hero_html, unsafe_allow_html=True)

        col_ing, col_inst = st.columns([1, 2])

        # INGREDIENTS COLUMN
        with col_ing:
            ingredients = recipe.get('ingredients', [])
            
            # HTML נקי ללא רווחים מיותרים
            ingredients_html = """
<div style="background: linear-gradient(180deg, #ffffff 0%, #faf7f2 100%); padding: 26px; border-radius: 22px; box-shadow: 0 14px 30px rgba(0,0,0,0.07); border: 1px solid rgba(0,0,0,0.03);">
    <div style="display: flex; align-items: center; gap: 10px; font-size: 1.3rem; font-weight: 800; margin-bottom: 18px; color: #1e1e1e;">
        🛒 Ingredients
    </div>
    <ul style="list-style: none; padding: 0; margin: 0; display: grid; gap: 10px; font-size: 1rem; color: #333;">
"""
            
            if isinstance(ingredients, list):
                for item in ingredients:
                    # הוספת strip() כדי לנקות רווחים בטעות
                    ingredients_html += f"""
    <li style="display: flex; align-items: center; gap: 10px; background: rgba(0,0,0,0.02); padding: 8px 12px; border-radius: 12px;">
        <span style="background: #3a7d44; color: white; font-size: 0.75rem; padding: 4px 7px; border-radius: 6px;">✓</span>
        <span>{item}</span>
    </li>
""".strip()
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

        # ACTION BUTTONS
        col_del, col_upd = st.columns([1, 4])

        with col_del:
            if st.button("🗑️ Delete", type="primary", use_container_width=True):
                try:
                    requests.delete(f"{API_URL}/{st.session_state.selected_recipe_id}")
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
# PAGE: ADD RECIPE
# ------------------------
elif st.session_state.page == "add":
    st.markdown("<h2 style='text-align: center;'>➕ Add New Recipe</h2>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown(textwrap.dedent("""
        <div style='background-color: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05);'>
        """), unsafe_allow_html=True)
        
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
                        response = requests.post(API_URL, json=new_recipe_data)
                        response.raise_for_status()
                        st.success("Recipe Added Successfully!")
                        st.session_state.page = "list"
                        st.rerun()
                        
                    except requests.exceptions.RequestException as e:
                        st.error(f"Error saving recipe: {e}")

        st.markdown("</div>", unsafe_allow_html=True)