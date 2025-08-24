import asyncio
import base64
import numpy as np
import sounddevice as sd
from openai import AsyncOpenAI

IN_RATE = 16000          # mic capture rate
OUT_RATE = 24000         # model output rate (PCM16 @ 24 kHz)
CHUNK = 512

prompt = """
Today we will have a call, and you will ask me to design a **Weather Reporting System**.

I need you to conduct a system design interview on a big tech style.
The interview should follow the following structure: requirements gettering, high-level design, deep dive and wrap up.
Ask question for clarification only, or identify points of improvement.
Try to the give short responses and avoid give the candidate any answers.
Let the candidate reach the solution for it self.

# Requirements
For this step the interviewee will ask you questions to define the requirements and you should answer them, without giving the problem's solution.

## Example
Interviewer: I'd like you to design a news feed

Candidate: Is this a mobile app? Or a web app? Or both?
Interviewer: Both. Candidate: What are the most important features for the product?

Candidate: What are the most important features for the product?
Interviewer: Ability to make a post and see friends’ news feed.

Candidate: Is the news feed sorted in reverse chronological order or a particular order? The particular order means each post is given a different weight. For instance, posts from your close friends are more important than posts from a group.
Interviewer: To keep things simple, let us assume the feed is sorted by reverse chronological order.

Candidate: How many friends can a user have? Interviewer: 5000 Candidate: What is the traffic volume?
Interviewer: 10 million daily active users (DAU)

Candidate: Can feed contain images, videos, or just text? Interviewer: It can contain media files, including both images and videos.
Interviewer: It can contain media files, including both images and videos.

# High-level design
In this step the candidate should present you the sketching of the high-level design, explaining the components of the system and the decisions/tread-offs considered.
You can ask question for clarification and identify points of improvement or give some feedback.

## Example:
The candidate added a web socket service, you can ask, how can you will scale this server?

## API Design (Optional)
In the high-level design you can ask the interviewer to design the API and ask API related questions.

## Database Design (Optional)
In the high-level design you can ask the interviewer to design the database and ask database modeling questions.

# Deep dive
In this step we are digging into details of some system components, example:
For a URL shortener, it is interesting to dive into the hash function design that converts a long URL to a short one.
For a chat system, how to reduce latency and how to support online/offline status are two interesting topics.

# Time allocation for each step
* Requirements: 3 - 10 minutes
* High-level design: 10 - 15 minutes
* Deep dive: 10 - 25 minutes
"""

async def main():
    client = AsyncOpenAI()

    async with client.beta.realtime.connect(
        model="gpt-4o-realtime-preview"
    ) as conn:
        # Session config
        await conn.session.update(session={
            "modalities": ["audio", "text"],
            "input_audio_format": "pcm16",
            "input_audio_transcription": {"model": "whisper-1"},
            "output_audio_format": "pcm16"  # server returns PCM16 @ 24kHz
        })

        loop = asyncio.get_running_loop()

        # ---- Mic input (runs in background thread) ----
        def mic_callback(indata, frames, time, status):
            if status:
                print("Mic status:", status)
            # float32 [-1,1] -> PCM16 bytes -> base64 string
            pcm_bytes = (indata * 32767).astype(np.int16).tobytes()
            b64 = base64.b64encode(pcm_bytes).decode("utf-8")
            loop.call_soon_threadsafe(
                asyncio.create_task,
                conn.input_audio_buffer.append(audio=b64)
            )

        mic_stream = sd.InputStream(
            samplerate=IN_RATE,
            channels=1,
            dtype="float32",
            blocksize=CHUNK,
            callback=mic_callback
        )
        mic_stream.start()

        # ---- Speaker output (persistent queue) ----
        out_stream = sd.OutputStream(
            samplerate=OUT_RATE,
            channels=1,
            dtype="float32",
            blocksize=CHUNK
        )
        out_stream.start()

        # Kick off with text
        await conn.conversation.item.create(item={
            "type": "message",
            "role": "system",
            "content": [{"type": "input_text", "text": "You are a recruiter a teach recruiter."}]
        })
        await conn.conversation.item.create(item={
            "type": "message",
            "role": "user",
            "content": [{"type": "input_text", "text": prompt}]
        })
        await conn.response.create()

        # ---- Event loop ----
        async for event in conn:
            # AUDIO (new event names)
            if event.type == "response.audio.delta":
                # base64 -> PCM16 -> float32 [-1,1]
                audio_bytes = base64.b64decode(event.delta)
                audio_f32 = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32767.0
                out_stream.write(audio_f32)

            elif event.type == "response.audio.done":
                print("\n✅ Done speaking")

            # TEXT (optional)
            elif event.type == "response.text.delta":
                print(event.delta, end="", flush=True)
            elif event.type == "response.text.done":
                print()

if __name__ == "__main__":
    asyncio.run(main())
