import json
import re
import io
from PIL import Image

from services.agent_api_calls import describe_tile,call_gpt
_CHUNK_PROMPT = """You are analysing tile {idx} of {total} from a meme image.
Describe what you see in this tile in 1-2 sentences.
Focus on: people, symbols, text overlays, expressions, gestures, colours."""

_CLASSIFY_PROMPT = """You are an expert hate-speech analyst specialising in
Devnagri and Hinglish memes targeting the LGBT community.

Below are descriptions of each tile of the meme image:{chunk_descriptions}
You perform the following tasks sequentially:

Additionally, consider the full image to understand high-level context, overall meme intent, and relationships between tiles. Use this context along with tile descriptions while making the classification.

Task :
Examine each tile carefully to identify if it contains mocking, insulting, or derogatory language; stereotypes or ridicule; or references to gender identity or LGBT people.

Important Rules:
Even a single hateful tile is sufficient to classify the meme as hateful.
Text content holds greater importance than background visuals.
Do not overlook offensive wording, even if other tiles appear neutral.
If any tile contains a negative or insulting reference to transgender or hijra people (e.g., hijda, hizru, hijru boy, hijde, chakka, chakke, or similar Hindi/Devanagari insults), classify as Transphobia.
If any tile contains a negative or insulting reference to gay, lesbian, or homosexual people (e.g., meetha, gay, lesbo, lesbian, or similar slurs/derogatory words used insultingly), classify as Homophobia.

Classification Definitions:
Homophobia: Content that mocks, insults, stereotypes, or expresses hostility toward people based on sexual orientation (e.g., gay, lesbian, bisexual). This includes ridicule, derogatory language, or negative portrayals.
Transphobia: Content that mocks, insults, misrepresents, or expresses hostility toward gender identity or gender expression (e.g., transgender, non-binary people). This includes misgendering, denial of identity, or derogatory references to gender transition or roles.
Non-LGBT: Content that does not reference or target sexual orientation or gender identity, or contains neutral, unrelated, or non-hateful content.

Return ONLY JSON:

{{
  "label": "Choose EXACTLY ONE label from: Homophobia or Transphobia or Non-LGBT",
  "used_chunks": [tile numbers that contain relevant evidence],
  "reasoning": "Explain clearly which tiles contain the signal and why"
}}
"""
def chunk_image(image, rows=2, cols=2):
    w, h = image.size
    chunks = []

    for i in range(rows):
        for j in range(cols):
            left = j * w // cols
            upper = i * h // rows
            right = (j + 1) * w // cols
            lower = (i + 1) * h // rows

            chunks.append(image.crop((left, upper, right, lower)))

    return chunks

def extract_json_image(output):
    try:
        match = re.search(r"\{.*\}", output, re.DOTALL)
        return json.loads(match.group())
    except:
        return {
            "label": "ERROR",
            "spans": [],
            "reasoning": "Parsing failed"
        }
    
def image_agent(image_bytes):
    IMAGE_CHUNK_ROWS = 2
    IMAGE_CHUNK_COLS = 2
    try:
        print(f"[INFO] Image Agent: Starting processing ...")
        image = Image.open(io.BytesIO(image_bytes))

        chunks = chunk_image(image, IMAGE_CHUNK_ROWS, IMAGE_CHUNK_COLS)
        total = len(chunks)

        descriptions = []
        chunk_results = []
        # TILE DESCRIPTIONS
        for idx, chunk in enumerate(chunks, start=1):
            prompt = _CHUNK_PROMPT.format(idx=idx, total=total)

            #Tile Description call to GPT
            desc = describe_tile(prompt, chunk)

            descriptions.append(desc.strip())
            chunk_results.append({
                "tile": idx,
                "description": desc
            })

        # MERGE DESCRIPTIONS
        chunk_descriptions = "\n".join(
            [f"Tile {i+1}: {desc}" for i, desc in enumerate(descriptions)]
        )

        #FINAL CLASSIFICATION (TEXT + FULL IMAGE)
        prompt = _CLASSIFY_PROMPT.format(
        chunk_descriptions=chunk_descriptions
        )
        final_output = call_gpt(prompt,image_bytes)

        parsed = extract_json_image(final_output)

        raw_label = parsed.get("label", "Non-LGBT").lower()

        if raw_label.startswith("homo"):
            label = "Homophobia"
        elif raw_label.startswith("trans"):
            label = "Transphobia"
        else:
            label = "Non-LGBT"

        used_chunks = [
            int(x) for x in parsed.get("used_chunks", [])
            if str(x).isdigit()
        ]

        reasoning = parsed.get("reasoning", "")

        used_chunk_data = [
            c for c in chunk_results if c["tile"] in used_chunks
        ]

        prediction = {
           
            "predicted_label": label,
            "reasoning": reasoning,
            "used_chunks": used_chunks,
            "used_chunk_details": used_chunk_data
        }
        print(f"[INFO] Image Agent: Finished processing ")
        return prediction
    except Exception as e:
        print(f"[ERROR] Image Agent: Error processing : {e}")
        return None    
    
