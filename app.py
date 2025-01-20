from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import abacusai
from gtts import gTTS
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip

app = Flask(__name__)

# Create uploads directory if it doesn't exist
if not os.path.exists('uploads'):
    os.makedirs('uploads')

client = abacusai.ApiClient("s2_6c16e1b965a74e4eaa86c3fb982d58d0")
base_dir = os.path.dirname(os.path.dirname(__file__))  # Base directory of the app
output_dir = os.path.join(base_dir, 'output')
# Home route
@app.route('/')
def index():
    videos_dir = os.path.join(output_dir)
    # Ensure the videos and images directories exist
    os.makedirs(videos_dir, exist_ok=True)
    videos = os.listdir(videos_dir)
    return render_template('index.html', videos=videos)

# API endpoint to generate script
@app.route('/generate_script', methods=['POST'])
def generate_script():
    topic = request.form['topic']
    
    # Create a prompt for generating a clean narrative script
    prompt = f"Write a detailed narrative script for a Tick Tok video on the topic: {topic}. The script should be in a conversational tone, suitable for text-to-speech, and should not include any comments, formatting, or annotations."
    model="gpt-4o-mini",
      
    r = client.evaluate_prompt(prompt=prompt, system_message=f"You are a helpful assistant that creates Tick Tok scripts for a video about {topic}. The output should be a clean narrative without any comments or formatting.", llm_name="OPENAI_GPT4O")
    
    # Response:
    print(r.content)
    # Extract the generated script
    script = r.content
    # Return the script in a JSON response
    return jsonify({"script": script})

# API endpoint to create voiceover and video
@app.route('/create_video', methods=['POST'])
def create_video():
    try:
        # Get the script and video file from the POST request
        script = request.form['script']
        video_file = request.files['video_file']
        
        # Save the uploaded video file temporarily
        video_file_path = os.path.join("uploads", video_file.filename)
        video_file.save(video_file_path)
        
        # Generate voiceover using Google Text-to-Speech (gTTS)
        tts = gTTS(script, lang='en')
        tts.save("voiceover.mp3")
        
        # Load the video clip
        clip = VideoFileClip(video_file_path)  # Use the uploaded video file
        
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
        output_video_path = os.path.join(output_dir, f"final_video.mp4")
        final_video.write_videofile(
            output_video_path, 
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
    
@app.route('/output/<filename>')
def serve_video(filename):
    return send_from_directory(os.path.join(output_dir), filename)

if __name__ == '__main__':
    app.run(debug=True)