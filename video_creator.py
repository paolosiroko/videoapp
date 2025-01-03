from moviepy.editor import *
from gtts import gTTS
import os

def create_video(script):
    # 1. Convert the script to audio using gTTS
    tts = gTTS(text=script, lang='en')
    audio_path = "audio.mp3"
    tts.save(audio_path)

    # 2. Create video with a simple background and the audio track
    # Here we use a static background image for simplicity
    background = ImageClip("background.jpg", duration=10)  # Adjust duration as needed
    audio = AudioFileClip(audio_path)
    
    # Combine video and audio
    video = background.set_audio(audio)

    # Output file path
    video_path = "output_video.mp4"
    video.write_videofile(video_path, fps=24)

    # Cleanup
    os.remove(audio_path)

    return video_path
