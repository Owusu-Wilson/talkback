import streamlit as st
import whisper
import requests
import sounddevice as sd
import numpy as np
import io
import wave
import tempfile

# Initialize Whisper model
model = whisper.load_model("base")  # You can use "small", "medium", etc.

# Function to transcribe speech to text using Whisper
def transcribe_audio(file):
    audio = whisper.load_audio(file)
    result = model.transcribe(audio)
    return result["text"]

# Function to convert text to speech using 11Labs API (voice cloning)
def text_to_speech(text, voice_id, api_key):
    url = f"https://api.11labs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "voice": voice_id,
        "lang": "en"
    }
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        audio_data = response.content
        return audio_data
    else:
        st.error(f"Error: {response.status_code}, {response.text}")
        return None

# Streamlit UI
st.title("TalkTrack Application")

# Step 1: Record Audio
st.subheader("Record Live Audio")

# Parameters for audio recording
sampling_rate = 16000
duration = 5  # Duration in seconds

# Record audio button
record_button = st.button("Record Audio")

if record_button:
    with st.spinner("Recording..."):
        # Record audio in real-time using sounddevice
        recording = sd.rec(int(sampling_rate * duration), samplerate=sampling_rate, channels=1, dtype='int16')
        sd.wait()  # Wait for the recording to finish

        # Convert the recorded audio to WAV format in-memory
        wav_io = io.BytesIO()
        with wave.open(wav_io, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 2 bytes (16 bits)
            wf.setframerate(sampling_rate)
            wf.writeframes(recording.tobytes())
        wav_io.seek(0)

        st.audio(wav_io, format="audio/wav")

        # Step 2: Transcribe the recorded audio to text using Whisper
        st.write("Transcribing audio...")
        transcribed_text = transcribe_audio(wav_io)
        st.write(f"Transcribed Text: {transcribed_text}")

        # Step 3: Enter Voice ID and API Key for 11Labs (Voice Cloning)
        voice_id = st.text_input("Enter your 11Labs Voice ID")
        api_key = st.text_input("Enter your 11Labs API Key", type="password")

        if st.button("Generate Speech"):
            if voice_id and api_key:
                # Step 4: Generate Speech from Text
                st.write("Generating speech...")
                audio_data = text_to_speech(transcribed_text, voice_id, api_key)

                if audio_data:
                    # Step 5: Play Generated Speech
                    st.audio(audio_data, format="audio/wav")
            else:
                st.error("Please provide both the Voice ID and API Key")
