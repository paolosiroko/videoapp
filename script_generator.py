import openai

def generate_script(topic):
    prompt = f"Create a YouTube script for a video about {topic}. Include an introduction, main points, and conclusion."
    
    response = openai.Completion.create(
        engine="text-davinci-003",  # or use any other available engine
        prompt=prompt,
        max_tokens=500
    )
    
    return response.choices[0].text.strip()
