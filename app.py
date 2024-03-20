from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube
import torch
from transformers import AutoTokenizer, AutoModelForQuestionAnswering


app = Flask(__name__)
CORS(app)

captions_string=""
@app.route('/process_video', methods=['POST'])
def process_video():
    try:
        # Access video ID from the request
        data = request.json
        video_id = data.get('video_id')

        # Validate video ID (you might want to check if it's a valid ID)
        if video_id is None:
            raise ValueError('Video ID is missing in the request.')

        def get_youtube_captions(video_url):
            try:
                # Get YouTube video
                yt = YouTube(video_url)

                # Get available captions
                captions = YouTubeTranscriptApi.get_transcript(yt.video_id)

                # Store captions in a string
                captions_text = ""

                # Concatenate captions into a single string
                for caption in captions:
                    captions_text += f"{caption['text']}\n"

                return captions_text.strip()

            except Exception as e:
                print(f"An error occurred: {e}")
                return None

        youtube_url = video_id
        # Example usage
        captions_string = get_youtube_captions(youtube_url)

        # if captions_string:
        #     print(f"Captions for {youtube_url}:\n{captions_string}")
        
        # Choose pre-trained model
        model_name = "bert-large-uncased-whole-word-masking-finetuned-squad"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForQuestionAnswering.from_pretrained(model_name)

        givinput="Earth has a very hospitable temperature and mix of chemicals that have made life abundant here. Most notably, Earth is unique in that most of our planet is covered in liquid water, since the temperature allows liquid water to exist for extended periods of time. Earth's vast oceans provided a convenient place for life to begin about 3.8 billion years ago."
        # User input
        paragraph = captions_string
        question = "Which phone we are talking about ?"

        # Tokenize inputs
        inputs = tokenizer(question, paragraph, return_tensors="pt")

        # Generate response
        outputs = model(**inputs)
        start_scores = outputs.start_logits
        end_scores = outputs.end_logits

        # Post-process output
        start_index = torch.argmax(start_scores)
        end_index = torch.argmax(end_scores)
        answer_tokens = inputs["input_ids"][0][start_index:end_index+1]
        answer = tokenizer.decode(answer_tokens)

        # Display response
        response_data = {'message': f'Generated Answer :{answer}'}
        return jsonify(response_data)
    except Exception as e:
        return jsonify({'error': str(e)})

# @app.route('/process_output', methods=['POST'])
# def process_output():
#     try:      
#         # Choose pre-trained model
#         model_name = "bert-large-uncased-whole-word-masking-finetuned-squad"
#         tokenizer = AutoTokenizer.from_pretrained(model_name)
#         model = AutoModelForQuestionAnswering.from_pretrained(model_name)

#         givinput="Earth has a very hospitable temperature and mix of chemicals that have made life abundant here. Most notably, Earth is unique in that most of our planet is covered in liquid water, since the temperature allows liquid water to exist for extended periods of time. Earth's vast oceans provided a convenient place for life to begin about 3.8 billion years ago."
#         # User input
#         paragraph = captions_string
#         question = "Which phone we are talking about ?"

#         # Tokenize inputs
#         inputs = tokenizer(question, paragraph, return_tensors="pt")

#         # Generate response
#         outputs = model(**inputs)
#         start_scores = outputs.start_logits
#         end_scores = outputs.end_logits

#         # Post-process output
#         start_index = torch.argmax(start_scores)
#         end_index = torch.argmax(end_scores)
#         answer_tokens = inputs["input_ids"][0][start_index:end_index+1]
#         answer = tokenizer.decode(answer_tokens)

#         # Display response
#         response_data = {'message': f'Generated Answer :{answer}'}
#         return jsonify(response_data)

#     except Exception as e:
#         return jsonify({'error': str(e)})
