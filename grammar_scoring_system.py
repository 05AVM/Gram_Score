import streamlit as st
import speech_recognition as sr
import language_tool_python
from pydub import AudioSegment
import os
import tempfile

st.title("🎙️ Grammar Scoring System for Spoken Audio")

def convert_audio_to_wav(uploaded_file):
    temp_dir = tempfile.mkdtemp()
    audio_path = os.path.join(temp_dir, "input_audio.wav")
    sound = AudioSegment.from_file(uploaded_file)
    sound.export(audio_path, format="wav")
    return audio_path

def transcribe_audio(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Could not understand audio."
    except sr.RequestError as e:
        return f"Error with the API: {e}"

def grammar_score(text):
    tool = language_tool_python.LanguageTool('en-US')
    matches = tool.check(text)
    num_errors = len(matches)
    word_count = len(text.split())

    # Scoring logic: fewer errors -> higher score
    score = max(0, 100 - int((num_errors / max(1, word_count)) * 100))
    return score, matches

uploaded_file = st.file_uploader("Upload an audio file", type=["mp3", "wav", "m4a"])

if uploaded_file:
    st.audio(uploaded_file)
    with st.spinner("Transcribing..."):
        wav_path = convert_audio_to_wav(uploaded_file)
        transcript = transcribe_audio(wav_path)
        st.markdown("### 📝 Transcribed Text:")
        st.write(transcript)

        with st.spinner("Analyzing Grammar..."):
            score, errors = grammar_score(transcript)
            st.markdown(f"### ✅ Grammar Score: `{score}/100`")
            st.markdown("### ❌ Grammar Mistakes:")
            for err in errors:
                st.write(f"- {err.message} (→ `{err.context}`)")

    os.remove(wav_path)