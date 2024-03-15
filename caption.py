from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube

app = Flask(__name__)
CORS(app)
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

        response_data = {'message': f'These are the captions for the youtube video:{captions_string}'}
        return jsonify(response_data)

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)



