import streamlit as st
import google.generativeai as genai
import os
from PIL import Image
import pyttsx3
import speech_recognition as sr
import tempfile

# ---------- Configure Gemini ----------
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# ---------- Streamlit Page Setup ----------
st.set_page_config(page_title="Digital Krishi Officer", page_icon="🌾", layout="wide")
st.title("🌱 Digital Krishi Officer")
st.markdown(
    """
    Ask any farming-related question and get instant advice!  
    Supports **Text**, **Voice File**, and **Image** inputs.
    """
)

# ---------- Sidebar for Context ----------
st.sidebar.header("Context")
location = st.sidebar.text_input("📍 Location")
crop = st.sidebar.text_input("🌾 Crop Type")
season = st.sidebar.selectbox("🌦️ Season", ["Select", "Kharif", "Rabi", "Zaid", "Other"])
st.sidebar.markdown("---")

# ---------- Image Upload ----------
st.subheader("📷 Upload Crop Image")
uploaded_image = st.file_uploader("Choose an image file", type=["jpg", "jpeg", "png"])
if uploaded_image:
    image = Image.open(uploaded_image)
    st.image(image, caption="Uploaded Crop Image", use_column_width=True)
    st.info("✅ Image uploaded successfully. (ML-based diagnosis can be added later)")

# ---------- Voice File Upload ----------
st.subheader("🎤 Upload Voice File")
uploaded_audio = st.file_uploader("Choose an audio file (wav/mp3)", type=["wav", "mp3"])

q = ""  # Initialize question text

if uploaded_audio:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        tmp_file.write(uploaded_audio.read())
        tmp_audio_path = tmp_file.name

    r = sr.Recognizer()
    try:
        with sr.AudioFile(tmp_audio_path) as source:
            audio_data = r.record(source)
            q = r.recognize_google(audio_data)  # language="ml-IN" can be used for Malayalam
            st.success(f"🎧 You said: {q}")
    except Exception as e:
        st.error(f"⚠️ Could not recognize audio: {e}")

# ---------- Text Input ----------
st.subheader("💬 Or Type Your Question")
text_input = st.text_area("Type here:", value=q, placeholder="Which fertilizer should I use for paddy?")
q = text_input if text_input else q

# ---------- Helper: Speak Text ----------
def speak_text(text):
    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", 150)
        engine.say(text)
        engine.runAndWait()
    except:
        st.warning("Speech output not available on this system.")

# ---------- Offline Fallback ----------
knowledge_base = {
    "paddy": "For paddy during rainy season, use NPK 20:20:0 fertilizer.",
    "banana": "Use Potassium-rich fertilizer (MOP) during fruiting stage for banana.",
}

def get_local_answer(query):
    for key, value in knowledge_base.items():
        if key in query.lower():
            return value
    return "I don't have data for that yet. Please consult a local agriculture officer."

# ---------- Get Advice ----------
if st.button("🔍 Get Advice") and q.strip():
    # Combine context with question
    full_query = q
    if location:
        full_query += f" | Location: {location}"
    if crop:
        full_query += f" | Crop: {crop}"
    if season and season != "Select":
        full_query += f" | Season: {season}"

    answer = ""
    try:
        # Only API call inside spinner
        with st.spinner("🤖 Thinking..."):
            response = model.generate_content(full_query)
            answer = response.text

    except Exception:
        st.error(" Network Not available, using offline knowledge base.")
        answer = get_local_answer(q)

    # Display answer and speak text outside spinner
    st.markdown(
        f"<div style='background-color:#e0f7fa;padding:20px;border-radius:12px;font-size:16px;'>"
        f"{answer}</div>",
        unsafe_allow_html=True
    )
    speak_text(answer)

