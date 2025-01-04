from flask import Flask, render_template, request, jsonify
import abacusai
from gtts import gTTS
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip

app = Flask(__name__)

client = abacusai.ApiClient("")


# Home route
@app.route('/')
def index():
    return render_template('index.html')

# API endpoint to generate script
@app.route('/generate_script', methods=['POST'])
def generate_script():
    topic = request.form['topic']
    
    # Create a prompt for generating a clean narrative script
    prompt = f"Write a detailed narrative script for a YouTube video on the topic: {topic}. The script should be in a conversational tone, suitable for text-to-speech, and should not include any comments, formatting, or annotations."
    model="gpt-4o-mini",
      
    r = client.evaluate_prompt(prompt = prompt, system_message = f"You are a helpful assistant that creates YouTube scripts for a video about {topic}. The output should be a clean narrative without any comments or formatting.", llm_name = "OPENAI_GPT4O")
    # Response:
    print(r.content)
    # Extract the generated script
    script =r.content
    # Return the script in a JSON response
    return jsonify({"script": script})

# API endpoint to create voiceover and video (mock example)
@app.route('/create_video', methods=['POST'])
def create_video():
    try:
        # Get the script from the POST request
        script = request.form['script']
        
        # Generate voiceover using Google Text-to-Speech (gTTS)
        tts = gTTS(script, lang='en')
        tts.save("voiceover.mp3")
        
        # Load the video clip
        clip = VideoFileClip("clip.mp4")  # Replace with your actual video file
        
        # Load the audio file
        audio_clip = AudioFileClip("voiceover.mp3")
        
        # Debug: Print durations
        print(f"Audio duration: {audio_clip.duration}")
        print(f"Video duration before trimming: {clip.duration}")
        
        # Trim the video to match the audio length
        trimmed_clip = clip.subclip(0, min(clip.duration, audio_clip.duration))
        
        # Debug: Check trimmed video duration
        print(f"Video duration after trimming: {trimmed_clip.duration}")
        
        # Set the audio for the video
        final_video = trimmed_clip.set_audio(audio_clip)
        
        # Ensure the audio is correctly attached
        if not final_video.audio:
            print("Audio was not set correctly.")
        else:
            print("Audio successfully set.")
        
        # Write the output file
        final_video.write_videofile(
            "final_video.mp4", 
            fps=24, 
            codec="libx264", 
            audio_codec="aac", 
            threads=8, 
            preset="ultrafast"  # Speeds up encoding
        )
        
        # Confirm the process
        print("Video created successfully with audio!")
        return jsonify({"message": "Video created successfully!"})
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
