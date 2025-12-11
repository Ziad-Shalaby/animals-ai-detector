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
    page_title="Animal Identifier AI",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------
# Custom CSS
# ----------------------------------
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3a8a 0%, #0f172a 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    h1 {
        color: #1e3a8a;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 700;
        text-align: center;
        padding: 20px;
    }
    
    h2, h3 {
        color: #2563eb;
    }
    
    .stButton>button {
        background: linear-gradient(90deg, #3b82f6 0%, #60a5fa 100%);
        color: white;
        border: none;
        padding: 15px 40px;
        font-size: 18px;
        font-weight: bold;
        border-radius: 50px;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.6);
    }
    
    .result-card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: 15px 0;
        color: #2d2d2d;
    }
    
    .result-card h2, .result-card h3 {
        color: #1e3a8a !important;
    }
    
    .result-card p, .result-card strong, .result-card li {
        color: #333333 !important;
    }
    
    .animal-card {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        color: white;
        padding: 25px;
        border-radius: 15px;
        margin: 15px 0;
    }
    
    .animal-card h2, .animal-card h3, .animal-card p, .animal-card strong {
        color: white !important;
    }
    
    .chat-message {
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        color: #2d2d2d;
    }
    
    .chat-message strong {
        color: #1a1a1a !important;
    }
    
    .user-message {
        background: #dbeafe;
        margin-left: 20%;
        color: #1e40af;
    }
    
    .user-message strong {
        color: #1e3a8a !important;
    }
    
    .bot-message {
        background: #f5f5f5;
        margin-right: 20%;
        color: #2d2d2d;
    }
    
    .bot-message strong {
        color: #1a1a1a !important;
    }
    
    .feature-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        text-align: center;
        transition: transform 0.3s;
        color: #333333;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
    }
    
    .feature-card h3 {
        color: #1e3a8a !important;
    }
    
    .feature-card p {
        color: #555555 !important;
    }
    
    .stat-box {
        background: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        color: #333333;
    }
    
    .stat-number {
        font-size: 36px;
        font-weight: bold;
        color: #3b82f6;
    }
    
    .stat-box div:not(.stat-number) {
        color: #555555 !important;
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
# Gemini Vision API for Animal Detection
# ----------------------------------
def identify_animal_with_gemini(image_data):
    """
    Identify animal using Gemini Vision API
    """
    if not GEMINI_API_KEY:
        return {
            "error": True,
            "message": "Gemini API key not configured. Please add GEMINI_API_KEY to .streamlit/secrets.toml"
        }
    
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Try vision models
        model_names = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro-vision']
        
        prompt = """Analyze this image and identify the animal. Provide the following information in a structured format:

Animal Name: [Common name]
Scientific Name: [Scientific/Latin name]
Animal Type: [Mammal/Bird/Reptile/Fish/Amphibian/Insect/etc]
Habitat: [Natural habitat]
Diet: [Herbivore/Carnivore/Omnivore and details]
Conservation Status: [Status if known]
Interesting Facts: [3-5 bullet points]
Physical Characteristics: [Brief description]

If you cannot identify the animal clearly, explain what you see."""

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
            "message": "Could not identify animal with any available model"
        }
        
    except Exception as e:
        return {
            "error": True,
            "message": f"Error: {str(e)}"
        }

# ----------------------------------
# Gemini Chat Functions
# ----------------------------------
def chat_with_gemini(user_message, context=None):
    """
    Chat with Gemini AI about animals
    """
    if not GEMINI_API_KEY:
        return "Gemini API key not configured. Please add GEMINI_API_KEY to .streamlit/secrets.toml"
    
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        
        model_names = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
        
        if context:
            system_prompt = f"""You are a helpful animal expert assistant. 
            
Current animal context:
- Animal: {context.get('animal_name', 'Unknown')}
- Scientific Name: {context.get('scientific_name', 'N/A')}
- Type: {context.get('animal_type', 'N/A')}
- Habitat: {context.get('habitat', 'N/A')}

Provide helpful, accurate advice about animals, their behavior, care, and conservation. Be friendly and conversational."""
            
            full_prompt = f"{system_prompt}\n\nUser question: {user_message}"
        else:
            full_prompt = f"""You are a helpful animal expert assistant. Provide accurate information about animals, wildlife, pets, conservation, and animal behavior. Be friendly and conversational.

User question: {user_message}"""
        
        last_error = None
        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(full_prompt)
                return response.text
            except Exception as e:
                last_error = str(e)
                continue
        
        return f"⚠️ Could not connect to Gemini API.\n\nPlease ensure your API key is correct.\n\nLast error: {last_error}"
        
    except Exception as e:
        return f"Error: {str(e)}"

# ----------------------------------
# Sidebar
# ----------------------------------
st.sidebar.markdown("# 🐾 Navigation")
st.sidebar.markdown("---")
app_mode = st.sidebar.selectbox(
    "Select Page", 
    ["🏠 Home", "🔍 Animal Detection", "💬 AI Chat", "📚 My Animals"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Quick Stats")
st.sidebar.metric("Animals Identified", len(st.session_state.detection_history))
st.sidebar.metric("Species Coverage", "1,000+")
st.sidebar.metric("AI Powered", "100%")

st.sidebar.markdown("---")
st.sidebar.markdown("### 💡 Tips")
st.sidebar.info("""
- Use clear, well-lit photos
- Show the whole animal if possible
- Avoid blurry images
- Multiple angles help
- Include distinctive features
""")

# ----------------------------------
# Home Page
# ----------------------------------
if app_mode == "🏠 Home":
    st.markdown("<h1>🐾 Animal Identifier AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 20px; color: #666;'>AI-Powered Animal Identification & Information</p>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Hero Image
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("https://images.unsplash.com/photo-1564349683136-77e08dba1ef7?w=800", 
                 use_column_width=True, caption="Identify animals instantly with AI")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Features
    st.markdown("### ✨ Key Features")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div style="font-size: 48px;">🔍</div>
            <h3>Animal Identification</h3>
            <p>Identify animals from photos using advanced AI vision</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div style="font-size: 48px;">📚</div>
            <h3>Detailed Information</h3>
            <p>Learn about habitat, diet, behavior, and conservation</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div style="font-size: 48px;">💬</div>
            <h3>AI Chat Expert</h3>
            <p>Ask questions and get expert animal knowledge</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Stats
    st.markdown("### 📊 Powered by Google Gemini AI")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="stat-box">
            <div class="stat-number">1000+</div>
            <div>Animal Species</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-box">
            <div class="stat-number">All</div>
            <div>Animal Types</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stat-box">
            <div class="stat-number">AI</div>
            <div>Vision Tech</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="stat-box">
            <div class="stat-number">⚡</div>
            <div>Instant</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Getting Started
    st.markdown("### 🚀 Getting Started")
    st.info("""
    1. Go to **Animal Detection** page
    2. Upload a clear photo of any animal
    3. Get instant identification and information
    4. Chat with AI for more details
    """)
    
    # API Setup Warning
    if not GEMINI_API_KEY:
        st.warning("""
        ⚠️ **API Key Required**
        
        To use this app, you need a Gemini API key:
        1. Get free API key from https://aistudio.google.com/app/apikey
        2. Create `.streamlit/secrets.toml` file with:
        ```
        GEMINI_API_KEY = "your_gemini_api_key"
        ```
        
        **Completely FREE to use!**
        """)

# ----------------------------------
# Animal Detection Page
# ----------------------------------
elif app_mode == "🔍 Animal Detection":
    st.markdown("<h1>🔍 Animal Identification</h1>", unsafe_allow_html=True)
    
    if not GEMINI_API_KEY:
        st.error("⚠️ Gemini API key not configured. Please add it to .streamlit/secrets.toml")
        st.stop()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📸 Upload Animal Image")
        uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"], key="animal_upload")
        
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)
            
            if st.button("🔍 Identify Animal", use_container_width=True):
                with st.spinner("🤖 AI is analyzing the animal..."):
                    result = identify_animal_with_gemini(image)
                    
                    if result.get("error"):
                        st.error(result.get("message"))
                    else:
                        # Parse the response
                        response_text = result.get("text", "")
                        
                        # Extract information
                        lines = response_text.split('\n')
                        animal_info = {
                            'animal_name': 'Unknown',
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
                            if line.startswith('Animal Name:'):
                                animal_info['animal_name'] = line.replace('Animal Name:', '').strip()
                            elif line.startswith('Scientific Name:'):
                                animal_info['scientific_name'] = line.replace('Scientific Name:', '').strip()
                            elif line.startswith('Animal Type:'):
                                animal_info['animal_type'] = line.replace('Animal Type:', '').strip()
                            elif line.startswith('Habitat:'):
                                animal_info['habitat'] = line.replace('Habitat:', '').strip()
                            elif line.startswith('Diet:'):
                                animal_info['diet'] = line.replace('Diet:', '').strip()
                            elif line.startswith('Conservation Status:'):
                                animal_info['conservation'] = line.replace('Conservation Status:', '').strip()
                            elif line.startswith('Physical Characteristics:'):
                                current_section = 'characteristics'
                                animal_info['characteristics'] = line.replace('Physical Characteristics:', '').strip()
                            elif line.startswith('Interesting Facts:'):
                                current_section = 'facts'
                            elif line.startswith('*') or line.startswith('-') or line.startswith('•'):
                                if current_section == 'facts':
                                    animal_info['facts'].append(line.lstrip('*-• ').strip())
                        
                        # Store in session state
                        st.session_state.animal_context = animal_info
                        st.session_state.detection_history.append({
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
                            'animal_name': animal_info['animal_name'],
                            'animal_type': animal_info['animal_type']
                        })
                        
                        # Display results in col2
                        with col2:
                            st.markdown("### 🐾 Identification Results")
                            
                            st.markdown(f"""
                            <div class="animal-card">
                                <h2>🐾 {animal_info['animal_name']}</h2>
                                <p><strong>Scientific Name:</strong> {animal_info['scientific_name']}</p>
                                <p><strong>Type:</strong> {animal_info['animal_type']}</p>
                                <p><strong>Habitat:</strong> {animal_info['habitat']}</p>
                                <p><strong>Diet:</strong> {animal_info['diet']}</p>
                                <p><strong>Conservation Status:</strong> {animal_info['conservation']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if animal_info['characteristics'] and animal_info['characteristics'] != 'N/A':
                                st.markdown("### 📝 Physical Characteristics")
                                st.info(animal_info['characteristics'])
                            
                            if animal_info['facts']:
                                st.markdown("### 💡 Interesting Facts")
                                for fact in animal_info['facts']:
                                    if fact:
                                        st.write(f"• {fact}")
                            
                            st.success("✅ Animal identified! You can now chat with AI to learn more.")
    
    with col2:
        if not uploaded_file:
            st.markdown("### 📋 Instructions")
            st.info("""
            👆 Upload an image of any animal to get started!
            
            **Supported Animals:**
            - Mammals (dogs, cats, lions, etc.)
            - Birds (eagles, parrots, etc.)
            - Reptiles (snakes, lizards, etc.)
            - Fish & Marine life
            - Insects & Arthropods
            - Amphibians
            - And many more!
            """)

# ----------------------------------
# AI Chat Page
# ----------------------------------
elif app_mode == "💬 AI Chat":
    st.markdown("<h1>💬 Chat with Animal Expert AI</h1>", unsafe_allow_html=True)
    
    if not GEMINI_API_KEY:
        st.error("⚠️ Gemini API key not configured. Please add it to .streamlit/secrets.toml")
        st.stop()
    
    # Display context if available
    if st.session_state.animal_context:
        with st.expander("📌 Current Animal Context", expanded=True):
            context = st.session_state.animal_context
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Animal:** {context.get('animal_name', 'Unknown')}")
                st.write(f"**Scientific Name:** {context.get('scientific_name', 'N/A')}")
            with col2:
                st.write(f"**Type:** {context.get('animal_type', 'N/A')}")
                st.write(f"**Habitat:** {context.get('habitat', 'N/A')}")
    else:
        st.info("💡 Identify an animal first to get context-aware advice, or ask general questions!")
    
    st.markdown("---")
    
    # Chat History
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>You:</strong> {message['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message bot-message">
                    <strong>🤖 Animal Expert:</strong> {message['content']}
                </div>
                """, unsafe_allow_html=True)
    
    # Chat Input
    st.markdown("---")
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_input("Ask me anything about animals...", key="chat_input", placeholder="e.g., What do elephants eat?")
    
    with col2:
        send_btn = st.button("Send 📨", use_container_width=True)
    
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
        st.markdown("### 💡 Quick Questions")
        quick_questions = [
            "What's the largest animal on Earth?",
            "How do dolphins communicate?",
            "What do pandas eat?",
            "How fast can a cheetah run?"
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
        st.info("🐾 You haven't identified any animals yet. Go to Animal Detection to get started!")
    else:
        st.markdown(f"### Total Identifications: {len(st.session_state.detection_history)}")
        
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
