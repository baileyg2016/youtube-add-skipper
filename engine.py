import argparse
import logging
import os
import time

import numpy as np
import openai
import whisper
import yt_dlp
from pydub import AudioSegment


def download_audio(video_url, output_file):
    print(f"Downloading audio from {video_url} to {output_file}...")
    output_file = output_file.removesuffix('.mp3')
    ydl_opts = {
        'format': 'mp3/bestaudio/best',
        'outtmpl': output_file,
        'noplaylist': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }]
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
    except yt_dlp.utils.DownloadError as e:
        logging.error(f"DownloadError: {e}")
        print('Got the download error but we worked anyway')

def split_audio(file_path, max_file_size_mb=25, default_chunk_seconds=120):
    audio = AudioSegment.from_file(file_path)
    file_size = os.path.getsize(file_path)  # Get the file size in bytes

    # If the file size is larger than max_file_size_mb, calculate new chunk duration
    if file_size > max_file_size_mb * 1024 * 1024:
        bitrate = audio.frame_rate * audio.sample_width * audio.channels  # Calculate bitrate in bps
        chunk_size_seconds = (max_file_size_mb * 1024 * 1024 * 8) / bitrate  # Calculate chunk duration in seconds
    else:
        chunk_size_seconds = default_chunk_seconds

    chunks = []
    for i in range(0, len(audio), int(chunk_size_seconds * 1000)):
        chunk = audio[i:i + int(chunk_size_seconds * 1000)]
        chunks.append(chunk)

    return chunks

def transcribe_audio_chunks(chunks):
    transcripts = []

    for i, chunk in enumerate(chunks):
        temp_filename = f"temp_chunk_{i}.mp3"
        chunk.export(temp_filename, format="mp3")

        print(f"Transcribing: {temp_filename}...")
        start_time = time.time()
        model = whisper.load_model("medium")
        result = model.transcribe(temp_filename) # openai.Audio.transcribe("whisper-1", open(temp_filename, "rb"))
        print("result", result)
        transcript_segments = []
        for seg in result['segments']:
            ts = np.round(seg['start'], 1)
            transcript_segments.append(f"&t={ts}s\t{ts}\t{seg['text']}")

        transcripts.append("\n".join(transcript_segments))
        end_time = time.time()
        time_diff = end_time - start_time

        os.remove(temp_filename)  # Remove the temporary chunk file

        print(f"Chunk {i} transcribed. Time taken: {time_diff:.2f} seconds")

    return "\n".join(transcripts)


def transcribe_audio_chunks_1(chunks):
    transcripts = []

    for i, chunk in enumerate(chunks):
        temp_filename = f"temp_chunk_{i}.mp3"
        chunk.export(temp_filename, format="mp3")

        transcript = transcribe_audio(temp_filename)
        transcripts.append(transcript)

    return "\n".join(transcripts)

def truncate_audio(file_path, max_duration_seconds=2500):
    audio = AudioSegment.from_file(file_path, keep=True)
    print(max_duration_seconds)
    truncated_audio = audio[:max_duration_seconds * 1000]  # Truncate to max_duration_seconds
    truncated_audio.export(file_path, format="mp3")  # Overwrite the original file with the truncated audio


def transcribe_audio(file_path):
    audio_file = open(file_path, "rb")

    response = openai.Audio.transcribe("whisper-1", audio_file)
    return response['text']

def save_transcript(transcript, file_path):
    with open(file_path, "w") as f:
        f.write(transcript)

# Delete the audio files
def cleanup():
    for file in os.listdir():
        if file.endswith(".mp3"):
            os.remove(file)

def main():
    # Set up logger
    logging.basicConfig(filename='download_audio.log',
                        filemode='w', 
                        level=logging.ERROR)

    parser = argparse.ArgumentParser(description='Process YouTube URL and output file')
    parser.add_argument('video_url', type=str, help='YouTube video URL')
    # parser.add_argument('output_file', type=str, help='Output file name with extension (e.g. output.m4a)') # this should be needed
    args = parser.parse_args()

    video_url = args.video_url
    output_file = "output_audio.mp3" # args.output_file if args.output_file.endswith(".mp3") else f"{args.output_file}.mp3"
    try:
        # Download audio from YouTube video
        # OpenAI really needs to let you just make an API call with a URL
        download_audio(video_url, output_file)

        # Split audio into chunks
        chunks = split_audio(output_file)

        # Transcribe audio chunks
        transcript = transcribe_audio_chunks(chunks)

        # Save transcript
        transcript_file = "transcript.txt"
        save_transcript(transcript, transcript_file)

        print(f"\n\nTranscript saved to {transcript_file}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Delete the audio files no matter what
        cleanup()
        


if __name__ == '__main__':
    main()
