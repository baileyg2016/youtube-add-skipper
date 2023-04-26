from pydub import AudioSegment
import yt_dlp
import argparse
import logging
import openai


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

def split_audio(file_path, chunk_size_seconds=120):
    audio = AudioSegment.from_file(file_path)
    chunks = []

    for i in range(0, len(audio), chunk_size_seconds * 1000):
        chunk = audio[i:i + chunk_size_seconds * 1000]
        chunks.append(chunk)

    return chunks

def transcribe_audio_chunks(chunks):
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

def main():
    # Set up logger
    logging.basicConfig(filename='download_audio.log',
                        filemode='w', 
                        level=logging.ERROR)

    parser = argparse.ArgumentParser(description='Process YouTube URL and output file')
    parser.add_argument('video_url', type=str, help='YouTube video URL')
    parser.add_argument('output_file', type=str, help='Output file name with extension (e.g. output.m4a)')
    args = parser.parse_args()

    video_url = args.video_url
    output_file = args.output_file if args.output_file.endswith(".mp3") else f"{args.output_file}.mp3"

    download_audio(video_url, output_file)
    max_duration_seconds = 2500  # Set the maximum duration in seconds
    # truncate_audio(output_file)
    # Split audio into chunks
    chunks = split_audio(output_file)

    # Transcribe audio chunks
    transcript = transcribe_audio_chunks(chunks)

    # Save transcript
    transcript_file = "transcript.txt"
    save_transcript(transcript, transcript_file)

    print(f"Transcript saved to {transcript_file}")



if __name__ == '__main__':
    main()
