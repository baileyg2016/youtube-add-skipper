import argparse
import logging

from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from youtube_transcript_api import YouTubeTranscriptApi

DEBUG = False

def save_transcript(transcript, file_path):
    with open(file_path, "w") as f:
        f.write(transcript)

def download_transcript(video_url):
    video_id = video_url.split('watch?v=')[-1]
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    
    return transcript
    
def get_only_transcript(transcript):
    combined_text = ''
    for item in transcript:
        combined_text += item['text'] + ' '

    return combined_text

def determine_ads(transcript):
    
    prompt = PromptTemplate(
        input_variables=["transcript"],
        template="""
        I am going to give you a transcript of a youtube video and I want you to tell me if there are any ads in it.
        You will only respond with 'Yes' or 'No'. Nothing else.

        Transcript: {transcript}
        AI:"""
    )
    split = 20 # TODO: need to make this dynamic
    part_length = len(transcript) // split
    
    prompts = [transcript[i * part_length:(i + 1) * part_length] for i in range(split)]
    # model = openai.ChatCompletion.create(model="gpt-3.5-turbo")
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    chain = LLMChain(
        llm=llm,
        prompt=prompt
    )

    if DEBUG:
        for p in prompts:
            print("prompt:", len(p))

    responses = []
    for p in prompts:
        r = chain.run([p])
        responses.append(r)
    
    print(f"Responses: {responses}")

def main():
    # Set up logger
    logging.basicConfig(filename='download_audio.log',
                        filemode='w', 
                        level=logging.ERROR)

    parser = argparse.ArgumentParser(description='Process YouTube URL and output file')
    parser.add_argument('video_url', type=str, help='YouTube video URL')
    args = parser.parse_args()

    video_url = args.video_url
    output_file = "output_audio.mp3" # args.output_file if args.output_file.endswith(".mp3") else f"{args.output_file}.mp3"
    try:
        data = download_transcript(video_url)
        transcript = get_only_transcript(data)

        # Determine if there are any ads
        determine_ads(transcript)

        # print(f"\n\nTranscript saved to {transcript_file}")
    except Exception as e:
        print(f"Error: {e}")
        print(e.with_traceback())
        


if __name__ == '__main__':
    main()
