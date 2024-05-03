from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube
import google.generativeai as genai

global captions_string
captions_string = ""
global finalQuestion
finalQuestion=""
app = Flask(__name__)
CORS(app)


@app.route('/process_video', methods=['POST'])
def process_video():
    global captions_string  # Declare the variable as global
    
    try:
        # Access video ID from the request
        data = request.json
        video_id = data.get('video_id')

        # Validate video ID (you might want to check if it's a valid ID)
        if video_id is None:
            raise ValueError('Video ID is missing in the request.')

        def get_youtube_captions(video_url):
            try:
                # getting youtube url
                yt = YouTube(video_url)

                # extract captions 
                captions = YouTubeTranscriptApi.get_transcript(yt.video_id)

                # captions to variable 
                captions_text = ""

                # Concatenating captions into single variabke
                for caption in captions:
                    captions_text += f"{caption['text']}  "

                return captions_text.strip()

            except Exception as e:
                print(f"An error occurred: {e}")
                return None

        youtube_url = video_id

        #Captions into the captions_string...
        captions_string = get_youtube_captions(youtube_url)

        response_data = {'message': f'Captions : {captions_string}'}
        return jsonify(response_data)

    except Exception as e:
        return jsonify({'error': str(e)})
    

@app.route('/process_output', methods=['POST'])
def process_output():
    global finalQuestion
    try:
        data = request.json
        question = data.get('question')
        if question is None:
            raise ValueError('Question is not mentioned in the request.')
        #combining question and caption everytime , when the question is asked..
        finalQuestion =captions_string +".........."+ question
        genai.configure(api_key="AIzaSyDu3noOAGc6qsOZPUQwI4BqLqshOeM8Nsc")
       
       
        # Setting up the model
        generation_config = {
        "temperature": 0.9,
        "top_p": 1,
        "top_k": 1,
        "max_output_tokens": 2048,
        }

        #Safety settings to filter harmfull content 
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
        ]

        #model initalized 
        model = genai.GenerativeModel(model_name="gemini-1.0-pro",
                                        generation_config=generation_config,
                                        safety_settings=safety_settings)

        convo = model.start_chat(history=[])


        # request to model
        convo.send_message(finalQuestion)
       
        response_answer = {'answer': f'{convo.last.text}'}
        return jsonify(response_answer)
    
    except Exception as e:
        return jsonify({'error': str(e)})