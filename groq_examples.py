##### example API call

from groq import Groq

client = Groq()
completion = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
      {
        "role": "user",
        "content": ""
      }
    ],
    temperature=1,
    max_completion_tokens=8192,
    top_p=1,
    reasoning_effort="medium",
    stream=True,
    stop=None
)

for chunk in completion:
    print(chunk.choices[0].delta.content or "", end="")





##### example API call with TTS


import os
from groq import Groq

client = Groq()
speech_file_path = Path(__file__).parent / "speech.wav"
response = client.audio.speech.create(
  model="playai-tts",
  voice="Aaliyah-PlayAI",
  response_format="wav",
  input="",
)
response.stream_to_file(speech_file_path)
      