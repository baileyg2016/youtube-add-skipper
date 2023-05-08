import ast
import logging
import re
import os

from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv

DEBUG = False
load_dotenv()

def log(*args):
    DEBUG and print(*args)

class AdsEngine:
    def __init__(self, url):
        self.url = url
        self.video_id = url.split('watch?v=')[-1]
        self.transcript = None
        self.split = 20 # TODO: make this dynamic

    def __call__(self):
        # Set up logger
        logging.basicConfig(filename='download_audio.log',
                            filemode='w', 
                            level=logging.ERROR)

        try:
            data = self.download_transcript()
            
            transformed_data = self.transform_data(data)
            log(transformed_data)

            # Determine if there are any ads
            return self.determine_ads(transformed_data)

            # print(f"\n\nTranscript saved to {transcript_file}")
        except Exception as e:
            print(f"Error: {e}")
            print(e.with_traceback())

    def save_transcript(self, transcript, file_path):
        with open(file_path, "w") as f:
            f.write(transcript)

    def download_transcript(self):
        transcript = YouTubeTranscriptApi.get_transcript(self.video_id)
        
        return transcript
        
    def get_only_transcript(self, transcript):
        combined_text = ''
        for item in transcript:
            combined_text += item['text'] + ' '

        return combined_text
    
    def transform_data(self, data):
        transformed_data = []
        for item in data:
            transformed_data.append({
                'text': item['text'],
                'start': item['start'],
                'duration': item['duration'],
                'end': item['start'] + item['duration']
            })

        return transformed_data

    def determine_ads(self, transcript):
        # init chain
        yes_or_no = PromptTemplate(
            input_variables=["transcript"],
            template="""
            I am going to give you a transcript of a youtube video and I want you to tell me if there are any ads in it.
            You will only respond with 'Yes' or 'No'. Nothing else.

            Transcript: {transcript}
            AI:"""
        )


        prompt = PromptTemplate(
            input_variables=["transcript"],
            template="""
            I am going to give you an array of json objects. This objects will include a start time, end time, and duration.
            You will need to determine if there is an ad in the video.
            Return to me an array of objects with each object including the start and end time for each add. Do not add a note.
            If there are no ads, only return "None". Nothing else.

            Transcript: {transcript}
            AI:"""
        )
        llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY"))
        chain = LLMChain(
            llm=llm,
            prompt=prompt
        )

        # split transcript into parts
        split = 20 # TODO: need to make this dynamic
        part_length = len(transcript) // split
        prompts = [transcript[i * part_length:(i + 1) * part_length] for i in range(split)]

        responses = []
        for p in prompts:
            resp = chain.run([p])
            log(f'r==> {resp}')
            if 'None' in resp or resp == 'None':
                continue
        
            trim = re.search(r'\[(.*)\]', resp)
            data = ast.literal_eval(trim.group(0))
            log('type', type(data))
            responses.append({'start': data[0]['start'], 'end': data[-1]['end']})

        return responses
