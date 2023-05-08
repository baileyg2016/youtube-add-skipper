import { ArgumentParser } from 'argparse';
import { createWriteStream } from 'fs';
import { LLMChain } from 'langchain';
import { ChatOpenAI } from 'langchain/chat_models';
import { PromptTemplate } from 'langchain/prompts';
import { YouTubeTranscriptApi } from 'youtube_transcript_api';
const DEBUG = false;
function saveTranscript(transcript, filePath) {
    createWriteStream(filePath).write(transcript);
}
async function downloadTranscript(videoUrl) {
    const videoId = videoUrl.split('watch?v=')[1];
    const transcript = await YouTubeTranscriptApi.getTranscript(videoId);
    return transcript;
}
function getOnlyTranscript(transcript) {
    let combinedText = '';
    for (const item of transcript) {
        combinedText += item.text + ' ';
    }
    return combinedText;
}
async function determineAds(transcript) {
    const prompt = new PromptTemplate({
        inputVariables: ['transcript'],
        template: `
      I am going to give you a transcript of a youtube video and I want you to tell me if there are any ads in it.
      You will only respond with 'Yes' or 'No'. Nothing else.

      Transcript: {transcript}
      AI:`,
    });
    const llm = new ChatOpenAI({ modelName: 'gpt-3.5-turbo', temperature: 0 });
    const chain = new LLMChain({ llm: llm, prompt: prompt });
    const split = 20;
    const partLength = Math.floor(transcript.length / split);
    const prompts = transcript.split('').map((_char, i) => transcript.slice(i * partLength, (i + 1) * partLength));
    if (DEBUG) {
        for (const p of prompts) {
            console.log('prompt:', p.length);
        }
    }
    const responses = [];
    for (const p of prompts) {
        const r = await chain.run([p]);
        responses.push(r);
    }
    console.log(`Responses: ${responses}`);
}
async function main() {
    const parser = new ArgumentParser({ description: 'Process YouTube URL and output file' });
    parser.add_argument('video_url', { type: 'str', help: 'YouTube video URL' });
    const args = parser.parse_args();
    const videoUrl = args.video_url;
    try {
        const data = await downloadTranscript(videoUrl);
        const transcript = getOnlyTranscript(data);
        await determineAds(transcript);
    }
    catch (e) {
        console.error(`Error: ${e}`);
        console.error(e.stack);
    }
}
main();
