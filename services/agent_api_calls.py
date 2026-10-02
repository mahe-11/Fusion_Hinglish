
import time
from google import genai
from google.genai import types
import random
import io
import base64
from openai import OpenAI
import anthropic

def call_gemini(prompt, image=None):
      GEMINI_API_KEY="YOUR_API_KEY"
      gemini_client = genai.Client(api_key=GEMINI_API_KEY)
      max_retries=5
      if image:
         
          contents_to_send = [prompt, image]
      else:
        
          contents_to_send = prompt
      for attempt in range(max_retries):
        try:
            response = gemini_client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=contents_to_send,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            return response.text
        except Exception as e:
            msg = str(e)

           
            retryable = (
                "503" in msg or
                "429" in msg or
                "Service Unavailable" in msg or
                "Resource exhausted" in msg or
                "timeout" in msg.lower()
            )

            if not retryable or attempt == max_retries - 1:
                raise

            # Exponential backoff + full jitter
            delay = random.uniform(0, min(30, 2 ** attempt))
            print(f"Gemini transient error, retrying in {delay:.2f}s...")
            time.sleep(delay)

      return response.text


def encode_pil_image(image):
    if image.mode == "RGBA":
        image = image.convert("RGB")

    buffer = io.BytesIO()
    print(image.mode)
    image.save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def encode_image(image_bytes):
    return base64.b64encode(image_bytes).decode("utf-8")

def describe_tile(prompt, chunks):
    gpt_client = OpenAI  (api_key="YOUR_API_KEY")
    base64_img = encode_pil_image(chunks)

    response = gpt_client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_img}"
                    }
                }
            ]
        }],
        temperature=0
    )

    return response.choices[0].message.content


def call_claude(prompt, image_path=None):
    claude_client = anthropic.Anthropic(api_key="YOUR_API_KEY")
    messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },

                    ]
                }
            ]
    if image_path:
        base64_image = encode_image(image_path)
        messages[0]["content"].append({
            "type": "image",
             "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": base64_image
                        }
        })
    response = claude_client.messages.create(
            model="claude-sonnet-4-6",
            messages=messages,
            max_tokens=4000,
            temperature=0,

        )
    return response.content[0].text


def call_gpt(prompt, image_bytes):
    
    gpt_client = OpenAI  (api_key="YOUR_API_KEY")

    content = [{"type": "text", "text": prompt}]

    if image_bytes:
        base64_image = encode_image(image_bytes)
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
        })

    response = gpt_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": content
            }
        ],
        temperature=0
    )

    return response.choices[0].message.content