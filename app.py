import streamlit as st
import requests
import json
import base64
from PIL import Image
import io
import google.generativeai as genai
from datetime import datetime

# ----------------------------------
# Page Configuration
# ----------------------------------
st.set_page_config(
    page_title="Animal Explorer for Kids! 🐾",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------
# Custom CSS - Kid-Friendly Design
# ----------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Comic+Neue:wght@400;700&display=swap');
    
    body, p, span, div, li {
        font-family: 'Comic Neue', cursive, sans-serif !important;
    }
    
    h1, h2, h3 {
        font-family: 'Comic Neue', cursive, sans-serif !important;
    }
    
    .main {
        background: linear-gradient(135deg, #fef3c7 0%, #bfdbfe 50%, #ddd6fe 100%);
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #10b981 0%, #059669 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
        font-size: 18px !important;
    }
    
    h1 {
        color: #dc2626;
        font-family: 'Comic Neue', cursive !important;
        font-weight: 700;
        text-align: center;
        padding: 20px;
        font-size: 2.5em !important;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.2);
    }
    
    h2, h3 {
        color: #ea580c;
        font-weight: bold;
        font-size: 1.3em;
    }
    
    .stButton>button {
        background: linear-gradient(90deg, #f59e0b 0%, #ef4444 100%);
        color: white;
        border: none;
        padding: 15px 35px;
        font-size: 18px !important;
        font-weight: bold;
        border-radius: 50px;
        box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4);
        transition: all 0.3s ease;
        width: 100%;
        cursor: pointer;
    }
    
    .stButton>button:hover {
        transform: scale(1.05) translateY(-3px);
        box-shadow: 0 8px 25px rgba(239, 68, 68, 0.6);
        background: linear-gradient(90deg, #ef4444 0%, #f59e0b 100%);
    }
    
    .result-card {
        background: white;
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
        margin: 15px 0;
        color: #2d2d2d;
        border: 4px solid #fbbf24;
    }
    
    .result-card h2, .result-card h3 {
        color: #dc2626 !important;
        font-size: 1.4em !important;
    }
    
    .result-card p, .result-card strong, .result-card li {
        color: #333333 !important;
        font-size: 1em !important;
        line-height: 1.6;
    }
    
    .animal-card {
        background: linear-gradient(135deg, #34d399 0%, #3b82f6 100%);
        color: white;
        padding: 30px;
        border-radius: 20px;
        margin: 15px 0;
        border: 5px solid #fbbf24;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .animal-card h2, .animal-card h3, .animal-card p, .animal-card strong {
        color: white !important;
        font-size: 1.1em !important;
    }
    
    .chat-message {
        padding: 15px;
        border-radius: 15px;
        margin: 15px 0;
        font-size: 1em;
        color: #2d2d2d;
        border: 3px solid transparent;
    }
    
    .chat-message strong {
        color: #1a1a1a !important;
        font-size: 1em !important;
    }
    
    .user-message {
        background: linear-gradient(135deg, #bfdbfe 0%, #93c5fd 100%);
        margin-left: 15%;
        color: #1e40af;
        border-color: #3b82f6;
    }
    
    .user-message strong {
        color: #1e3a8a !important;
    }
    
    .bot-message {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        margin-right: 15%;
        color: #065f46;
        border-color: #10b981;
    }
    
    .bot-message strong {
        color: #064e3b !important;
    }
    
    .feature-card {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 6px 15px rgba(0,0,0,0.1);
        text-align: center;
        transition: transform 0.3s;
        color: #333333;
        border: 4px solid #f59e0b;
        cursor: pointer;
    }
    
    .feature-card:hover {
        transform: scale(1.1) rotate(2deg);
    }
    
    .feature-card h3 {
        color: #dc2626 !important;
        font-size: 1.3em !important;
    }
    
    .feature-card p {
        color: #555555 !important;
        font-size: 1em !important;
    }
    
    .stat-box {
        background: linear-gradient(135deg, #fae8ff 0%, #e9d5ff 100%);
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 6px 15px rgba(0,0,0,0.1);
        color: #333333;
        border: 4px solid #a855f7;
    }
    
    .stat-number {
        font-size: 36px;
        font-weight: bold;
        color: #7c3aed;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .stat-box div:not(.stat-number) {
        color: #6b21a8 !important;
        font-size: 1em !important;
        font-weight: bold;
    }
    
    .fun-emoji {
        font-size: 2.5em;
        animation: wiggle 1s ease-in-out infinite;
    }
    
    @keyframes wiggle {
        0%, 100% { transform: rotate(0deg); }
        25% { transform: rotate(-10deg); }
        75% { transform: rotate(10deg); }
    }
    
    .stAlert {
        font-size: 1em !important;
        border-radius: 15px;
        border: 3px solid;
    }
    
    /* Make text normal size and readable for kids */
    p, li, span, div {
        font-size: 1em !important;
        line-height: 1.5;
    }
    
    .red-panda-container {
        text-align: center;
        margin: 30px 0;
    }
    
    .red-panda-container img {
        border-radius: 30px;
        border: 6px solid #f59e0b;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------
# Initialize Session State
# ----------------------------------
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'animal_context' not in st.session_state:
    st.session_state.animal_context = None
if 'detection_history' not in st.session_state:
    st.session_state.detection_history = []

# ----------------------------------
# API Configuration
# ----------------------------------
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

# ----------------------------------
# Gemini Vision API for Animal Detection (Kid-Friendly)
# ----------------------------------
def identify_animal_with_gemini(image_data):
    """
    Identify animal using Gemini Vision API with kid-friendly responses
    """
    if not GEMINI_API_KEY:
        return {
            "error": True,
            "message": "Oops! We need to set up the AI first. Ask a grown-up to add the API key!"
        }
    
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        
        model_names = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro-vision']
        
        prompt = """Analyze this image and identify the animal. Provide information in a fun, kid-friendly way suitable for children in grades 1-6. Use simple words and make it exciting!

Animal Name: [Common name that kids would know]
Scientific Name: [Scientific name - but explain it's the "science name"]
Animal Type: [Is it a Mammal/Bird/Reptile/Fish/Amphibian/Insect - explain what that means simply]
Where They Live: [Their home/habitat in simple terms]
What They Eat: [Diet in simple, fun terms - like "They LOVE to munch on..."]
Are They Safe?: [Conservation status in kid terms - like "Doing great!" or "Need our help"]
Cool Facts: [5-7 super fun facts that kids will find amazing! Make them exciting!]
What They Look Like: [Fun description of how they look]

Make it fun, educational, and exciting for kids ages 6-12! Use emojis when helpful!"""

        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content([prompt, image_data])
                
                return {
                    "error": False,
                    "text": response.text,
                    "model_used": model_name
                }
            except Exception as e:
                continue
        
        return {
            "error": True,
            "message": "Hmm, the AI couldn't figure this one out. Try another picture!"
        }
        
    except Exception as e:
        return {
            "error": True,
            "message": f"Oops! Something went wrong: {str(e)}"
        }

# ----------------------------------
# Gemini Chat Functions (Kid-Friendly)
# ----------------------------------
def chat_with_gemini(user_message, context=None):
    """
    Chat with Gemini AI about animals - kid-friendly version
    """
    if not GEMINI_API_KEY:
        return "Oops! We need to set up the AI first. Ask a grown-up to add the API key!"
    
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        
        model_names = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
        
        if context:
            system_prompt = f"""You are a super friendly animal expert talking to kids in grades 1-6 (ages 6-12). 
            
Current animal we're learning about:
- Animal: {context.get('animal_name', 'Unknown')}
- Scientific Name: {context.get('scientific_name', 'N/A')}
- Type: {context.get('animal_type', 'N/A')}
- Where it lives: {context.get('habitat', 'N/A')}

Answer questions in a fun, exciting way! Use simple words, be enthusiastic, and make learning about animals super fun! You can use emojis to make it more fun! Keep answers clear and not too long - perfect for kids to understand.

Kid's question: {user_message}"""
        else:
            system_prompt = f"""You are a super friendly animal expert talking to kids in grades 1-6 (ages 6-12). Answer questions about animals in a fun, exciting way! Use simple words, be enthusiastic, and make learning super fun! You can use emojis! Keep answers clear and not too long.

Kid's question: {user_message}"""
        
        last_error = None
        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(system_prompt)
                return response.text
            except Exception as e:
                last_error = str(e)
                continue
        
        return f"⚠️ Oh no! The AI is taking a break. Please try again in a moment!"
        
    except Exception as e:
        return f"Oops! Something went wrong: {str(e)}"

# ----------------------------------
# Sidebar
# ----------------------------------
st.sidebar.markdown("# 🌟 Let's Explore!")
st.sidebar.markdown("---")
app_mode = st.sidebar.selectbox(
    "Where do you want to go?", 
    ["🏠 Home", "🔍 Find Animals", "💬 Ask Questions", "📚 My Animals"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎉 Your Stats")
st.sidebar.metric("Animals You Found", len(st.session_state.detection_history))
st.sidebar.metric("Animals We Know", "1,000+")
st.sidebar.metric("Fun Level", "⭐⭐⭐⭐⭐")

st.sidebar.markdown("---")
st.sidebar.markdown("### 💡 Tips for Great Photos")
st.sidebar.info("""
📸 Take clear pictures!
☀️ Use good lighting
🐾 Show the whole animal
📷 Don't blur the photo
😊 Have fun exploring!
""")

# ----------------------------------
# Home Page
# ----------------------------------
if app_mode == "🏠 Home":
    st.markdown("<h1>🐾 Animal Explorer for Kids! 🐾</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 22px; color: #dc2626; font-weight: bold;'>Learn About Amazing Animals with AI Magic! ✨</p>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Red Panda Hero Image
    st.markdown("""
    <div class="red-panda-container">
        <h2 style='color: #dc2626; font-size: 2em;'>🐼 Meet the Red Panda! 🐼</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("https://images.unsplash.com/photo-1497752531616-c3afd9760a11?w=800", 
                 use_column_width=True, caption="Red Pandas are super cute and love to climb trees!")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Fun Facts about Red Pandas
    st.markdown("### 🎈 Fun Fact About Red Pandas!")
    st.success("""
    🌟 Red Pandas are NOT related to Giant Pandas! They're actually more like raccoons!
    🍃 They LOVE bamboo and spend 13 hours a day eating it!
    🦊 They have a fluffy tail that helps them balance and keep warm!
    🧗 They're amazing climbers and spend most of their time in trees!
    """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Features
    st.markdown("### ✨ What Can You Do Here?")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="fun-emoji">🔍</div>
            <h3>Find Animals!</h3>
            <p>Take a picture and let AI tell you what animal it is!</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="fun-emoji">📚</div>
            <h3>Learn Cool Facts!</h3>
            <p>Discover amazing things about animals!</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="fun-emoji">💬</div>
            <h3>Ask Questions!</h3>
            <p>Chat with AI and learn even more!</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Stats
    st.markdown("### 🌈 Amazing Numbers!")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="stat-box">
            <div class="stat-number">1000+</div>
            <div>Animals!</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-box">
            <div class="stat-number">🌍</div>
            <div>From All Over!</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stat-box">
            <div class="stat-number">🤖</div>
            <div>AI Powered!</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="stat-box">
            <div class="stat-number">⚡</div>
            <div>Super Fast!</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Getting Started
    st.markdown("### 🚀 How to Start!")
    st.info("""
    1️⃣ Click on **Find Animals** on the left
    2️⃣ Upload a picture of any animal
    3️⃣ Watch the AI work its magic! ✨
    4️⃣ Learn cool facts about the animal
    5️⃣ Ask more questions if you want!
    """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Animal Quiz Section
    st.markdown("### 🎮 Quick Animal Quiz!")
    quiz_col1, quiz_col2 = st.columns(2)
    
    with quiz_col1:
        st.info("""
        **🤔 Did you know?**
        - 🦒 Giraffes have the same number of neck bones as humans (7!)
        - 🐙 Octopuses have 3 hearts!
        - 🦎 Some lizards can regrow their tails!
        """)
    
    with quiz_col2:
        st.success("""
        **🌟 Amazing Animals!**
        - 🐘 Elephants can't jump!
        - 🦋 Butterflies taste with their feet!
        - 🐨 Koalas sleep 18-22 hours a day!
        """)
    
    # API Setup Warning
    if not GEMINI_API_KEY:
        st.warning("""
        ⚠️ **Hey Grown-ups!**
        
        To use this app, you need a Gemini API key:
        1. Get a FREE API key from https://aistudio.google.com/app/apikey
        2. Create `.streamlit/secrets.toml` file with:
        ```
        GEMINI_API_KEY = "your_gemini_api_key"
        ```
        
        **It's completely FREE to use!** 🎉
        """)

# ----------------------------------
# Animal Detection Page
# ----------------------------------
elif app_mode == "🔍 Find Animals":
    st.markdown("<h1>🔍 Find That Animal! 🐾</h1>", unsafe_allow_html=True)
    
    if not GEMINI_API_KEY:
        st.error("⚠️ Oops! We need to set up the AI first. Ask a grown-up to add the API key!")
        st.stop()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📸 Upload Your Animal Picture!")
        st.info("Take a clear photo of any animal - dogs, cats, birds, bugs, anything! 🦁🐶🦅🐛")
        
        uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"], key="animal_upload")
        
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Your Awesome Photo! 📸", use_column_width=True)
            
            if st.button("🔍 Find Out What Animal This Is!", use_container_width=True):
                with st.spinner("🤖 AI is looking at your picture... This is so cool! ✨"):
                    result = identify_animal_with_gemini(image)
                    
                    if result.get("error"):
                        st.error(result.get("message"))
                    else:
                        response_text = result.get("text", "")
                        
                        # Extract information
                        lines = response_text.split('\n')
                        animal_info = {
                            'animal_name': 'Mystery Animal',
                            'scientific_name': 'N/A',
                            'animal_type': 'N/A',
                            'habitat': 'N/A',
                            'diet': 'N/A',
                            'conservation': 'N/A',
                            'facts': [],
                            'characteristics': 'N/A'
                        }
                        
                        current_section = None
                        for line in lines:
                            line = line.strip()
                            if 'Animal Name:' in line or 'Name:' in line:
                                animal_info['animal_name'] = line.split(':', 1)[1].strip()
                            elif 'Scientific Name:' in line or 'Science Name:' in line:
                                animal_info['scientific_name'] = line.split(':', 1)[1].strip()
                            elif 'Animal Type:' in line or 'Type:' in line:
                                animal_info['animal_type'] = line.split(':', 1)[1].strip()
                            elif 'Where They Live:' in line or 'Habitat:' in line or 'Home:' in line:
                                animal_info['habitat'] = line.split(':', 1)[1].strip()
                            elif 'What They Eat:' in line or 'Diet:' in line or 'Food:' in line:
                                animal_info['diet'] = line.split(':', 1)[1].strip()
                            elif 'Are They Safe:' in line or 'Conservation' in line or 'Status:' in line:
                                animal_info['conservation'] = line.split(':', 1)[1].strip()
                            elif 'What They Look Like:' in line or 'Physical' in line or 'Looks:' in line:
                                current_section = 'characteristics'
                                animal_info['characteristics'] = line.split(':', 1)[1].strip() if ':' in line else ''
                            elif 'Cool Facts:' in line or 'Fun Facts:' in line or 'Interesting Facts:' in line:
                                current_section = 'facts'
                            elif (line.startswith('*') or line.startswith('-') or line.startswith('•') or line.startswith('→')):
                                if current_section == 'facts':
                                    fact = line.lstrip('*-•→ ').strip()
                                    if fact:
                                        animal_info['facts'].append(fact)
                                elif current_section == 'characteristics' and animal_info['characteristics'] == 'N/A':
                                    animal_info['characteristics'] = line.lstrip('*-•→ ').strip()
                        
                        # Store in session state
                        st.session_state.animal_context = animal_info
                        st.session_state.detection_history.append({
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
                            'animal_name': animal_info['animal_name'],
                            'animal_type': animal_info['animal_type']
                        })
                        
                        # Display results in col2
                        with col2:
                            st.markdown("### 🎉 We Found It!")
                            st.balloons()
                            
                            st.markdown(f"""
                            <div class="animal-card">
                                <h2>🐾 {animal_info['animal_name']}</h2>
                                <p><strong>🔬 Science Name:</strong> {animal_info['scientific_name']}</p>
                                <p><strong>🏷️ Type:</strong> {animal_info['animal_type']}</p>
                                <p><strong>🏠 Where They Live:</strong> {animal_info['habitat']}</p>
                                <p><strong>🍽️ What They Eat:</strong> {animal_info['diet']}</p>
                                <p><strong>💚 Are They Safe?:</strong> {animal_info['conservation']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if animal_info['characteristics'] and animal_info['characteristics'] != 'N/A':
                                st.markdown("### 👀 What They Look Like")
                                st.success(animal_info['characteristics'])
                            
                            if animal_info['facts']:
                                st.markdown("### 🌟 Super Cool Facts!")
                                for i, fact in enumerate(animal_info['facts'], 1):
                                    if fact:
                                        st.write(f"**{i}.** {fact}")
                            
                            st.success("✅ Awesome! Now you can ask questions about this animal in the 'Ask Questions' page!")
    
    with col2:
        if not uploaded_file:
            st.markdown("### 🎨 What Can You Find?")
            st.success("""
            You can find ANY animal! Try these:
            
            🐕 **Pets:** Dogs, cats, rabbits, hamsters
            
            🦁 **Wild Animals:** Lions, tigers, elephants
            
            🦅 **Birds:** Eagles, parrots, penguins
            
            🐍 **Reptiles:** Snakes, lizards, turtles
            
            🐠 **Water Animals:** Fish, dolphins, sharks
            
            🐛 **Bugs:** Butterflies, beetles, ants
            
            🐸 **Amphibians:** Frogs, salamanders
            
            And MANY MORE! Upload a picture to start! 📸
            """)

# ----------------------------------
# AI Chat Page
# ----------------------------------
elif app_mode == "💬 Ask Questions":
    st.markdown("<h1>💬 Ask the Animal Expert! 🦉</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 18px; color: #059669;'>Ask me ANYTHING about animals! I love answering questions! 😊</p>", unsafe_allow_html=True)
    
    if not GEMINI_API_KEY:
        st.error("⚠️ Oops! We need to set up the AI first. Ask a grown-up to add the API key!")
        st.stop()
    
    # Display context if available
    if st.session_state.animal_context:
        with st.expander("🎯 Animal We're Learning About", expanded=True):
            context = st.session_state.animal_context
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**🐾 Animal:** {context.get('animal_name', 'Unknown')}")
                st.write(f"**🔬 Science Name:** {context.get('scientific_name', 'N/A')}")
            with col2:
                st.write(f"**🏷️ Type:** {context.get('animal_type', 'N/A')}")
                st.write(f"**🏠 Home:** {context.get('habitat', 'N/A')}")
    else:
        st.info("💡 You can ask about ANY animal! Or find an animal first to ask specific questions about it!")
    
    st.markdown("---")
    
    # Chat History
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>😊 You Asked:</strong> {message['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message bot-message">
                    <strong>🦉 Animal Expert Says:</strong> {message['content']}
                </div>
                """, unsafe_allow_html=True)
    
    # Chat Input
    st.markdown("---")
    st.markdown("### 💭 Your Question:")
    
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_input("Type your question here...", key="chat_input", 
                                   placeholder="Example: Why do giraffes have long necks?")
    
    with col2:
        send_btn = st.button("Send! 📨", use_container_width=True)
    
    if send_btn and user_input:
        st.session_state.chat_history.append({
            'role': 'user',
            'content': user_input
        })
        
        with st.spinner("🤔 Thinking..."):
            response = chat_with_gemini(user_input, st.session_state.animal_context)
        
        st.session_state.chat_history.append({
            'role': 'assistant',
            'content': response
        })
        
        st.rerun()
    
    # Quick Questions
    if len(st.session_state.chat_history) == 0:
        st.markdown("### 💡 Fun Questions to Ask!")
        quick_questions = [
            "What's the biggest animal on Earth?",
            "How do dolphins talk to each other?",
            "What do pandas eat?",
            "How fast can a cheetah run?",
            "Why do elephants have trunks?",
            "Can penguins fly?"
        ]
        
        cols = st.columns(2)
        for i, question in enumerate(quick_questions):
            with cols[i % 2]:
                if st.button(question, key=f"quick_{i}"):
                    st.session_state.chat_history.append({
                        'role': 'user',
                        'content': question
                    })
                    response = chat_with_gemini(question, st.session_state.animal_context)
                    st.session_state.chat_history.append({
                        'role': 'assistant',
                        'content': response
                    })
                    st.rerun()
    
    # Clear Chat
    if len(st.session_state.chat_history) > 0:
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()

# ----------------------------------
# My Animals Page
# ----------------------------------
elif app_mode == "📚 My Animals":
    st.markdown("<h1>📚 My Animal Collection</h1>", unsafe_allow_html=True)
    
    if not st.session_state.detection_history:
        st.info("🐾 You haven't identified any animals yet. Go to Find Animals to get started!")
    else:
        st.markdown(f"### Total Animals Found: {len(st.session_state.detection_history)}")
        
        for i, record in enumerate(reversed(st.session_state.detection_history)):
            with st.expander(f"🐾 {record['animal_name']} - {record['timestamp']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Animal:** {record['animal_name']}")
                    st.write(f"**Type:** {record['animal_type']}")
                with col2:
                    st.write(f"**Date:** {record['timestamp']}")
        
        if st.button("🗑️ Clear History"):
            st.session_state.detection_history = []
            st.rerun()
