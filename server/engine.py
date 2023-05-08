import logging
import os

from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv

DEBUG = False
load_dotenv()

class AdsEngine:
    def __init__(self, url):
        self.url = url
        self.video_id = url.split('watch?v=')[-1]
        self.transcript = None

    def __call__(self):
        # Set up logger
        logging.basicConfig(filename='download_audio.log',
                            filemode='w', 
                            level=logging.ERROR)

        try:
            data = self.download_transcript()
            transcript = self.get_only_transcript(data)

            # Determine if there are any ads
            return self.determine_ads(transcript)

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

    def determine_ads(self, transcript):
        # init chain
        prompt = PromptTemplate(
            input_variables=["transcript"],
            template="""
            I am going to give you a transcript of a youtube video and I want you to tell me if there are any ads in it.
            You will only respond with 'Yes' or 'No'. Nothing else.

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
        

        if DEBUG:
            for p in prompts:
                print("prompt:", len(p))

        responses = []
        for p in prompts:
            r = chain.run([p])
            responses.append(r)
        
        print(f"Responses: {responses}")
        return responses
