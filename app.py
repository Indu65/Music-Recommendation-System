import streamlit as st
from streamlit_webrtc import webrtc_streamer
import av
import cv2
import numpy as np
import mediapipe as mp
from keras.models import load_model
import webbrowser
from deepface import DeepFace  # ✅ Added DeepFace

# Logo Section
col1, col2, col3 = st.columns([1,6,1])
with col2:
    st.image("./Images/logo.png", width=530, use_column_width=True)

st.title("MyMusic")
st.write("MyMusic is an emotion-detection-based music recommendation system. To get recommended songs, start by allowing mic and camera for this web app.")

# Load Model and Labels
model = load_model("model.h5")
label = np.load("labels.npy")

# Initialize session state
if "run" not in st.session_state:
    st.session_state["run"] = "true"

try:
    detected_emotion = np.load("detected_emotion.npy")[0]
except:
    detected_emotion = ""

if not detected_emotion:
    st.session_state["run"] = "true"
else:
    st.session_state["run"] = "false"

# Emotion Detection Using DeepFace
class EmotionDetector:
    def recv(self, frame):
        frm = frame.to_ndarray(format="bgr24")
        frm = cv2.flip(frm, 1)  # Flip frame for mirror effect
        
        try:
            result = DeepFace.analyze(frm, actions=["emotion"], enforce_detection=False)
            pred = result[0]["dominant_emotion"]  # Get dominant emotion
        except:
            pred = "neutral"

        print(f"Detected Emotion: {pred}")
        cv2.putText(frm, pred, (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)
        np.save("detected_emotion.npy", np.array([pred]))

        return av.VideoFrame.from_ndarray(frm, format="bgr24")

# User Inputs
lang = st.text_input("Enter your preferred language")
artist = st.text_input("Enter your preferred artist")

if lang and artist and st.session_state["run"] != "false":
    webrtc_streamer(key="key", desired_playing_state=True, video_processor_factory=EmotionDetector)

# Recommendation Button
btn = st.button("Recommend music")

if btn:
    if not detected_emotion:
        st.warning("Please let me capture your emotion first!")
        st.session_state["run"] = "true"
    else:
        webbrowser.open(f"https://www.youtube.com/results?search_query={lang}+{detected_emotion}+songs+{artist}")
        np.save("detected_emotion.npy", np.array([""]))
        st.session_state["run"] = "false"

st.write("Made by ❤ INDIRA")

# Streamlit Customization
st.markdown("""
<style>
header {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)
