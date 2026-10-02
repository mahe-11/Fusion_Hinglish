import json
import re
from services.agent_api_calls import call_gemini

_TEXT_PROMPT = """You are an expert hate-speech analyst specialising in
    Hinglish (Hindi + English) memes targeting the LGBT community.
    TEXT is the OCR-extracted from a meme. TEXT: {text}

    You perform the following three tasks sequentially:

    TASK 1 - SPAN DETECTION
    Identify the exact, words or phrases within the TEXT that explicitly convey hateful, derogatory, or discriminatory content towards the LGBT community. Prioritize the most directly offensive terms. Return an empty list [] if none.

    TASK 2 - CLASSIFICATION
    Classify the text into EXACTLY ONE of the following classes:
    - Homophobia
    - Transphobia
    - Non-LGBT

    CLASSIFICATION DEFINITIONS:
    - Homophobia: Content that mocks, insults, stereotypes, or expresses hostility toward people based on sexual orientation (e.g., gay, lesbian, bisexual). Includes ridicule, derogatory language, or negative portrayals.
    - Transphobia: Content that mocks, insults, misrepresents, or expresses hostility toward gender identity or gender expression (e.g., transgender, non-binary people). Includes misgendering, denial of identity, or derogatory references to gender transition or roles.
    - Non-LGBT: Content that does not reference or target sexual orientation or gender identity, or contains neutral, unrelated, or non-hateful content.

    TASK 3 - REASONING
    Give a short, clear explanation for your decision.

    IMPORTANT RULES:
    - Comprehensive Analysis: Analyse the text carefully and do NOT ignore offensive wording even if other parts of the text appear neutral.
    - Hinglish Specifics & Priority:
    - If TEXT contains any negative or insulting reference to transgender or hijra people (including words like hijda, hizru, hizru boy, hijde, chakka, chakke, or similar Hindi/Devanagari insults) → classify as Transphobia.
    - If TEXT contains any negative or insulting reference to gay, lesbian, or homosexual people (including words like meetha, gay, lesbo, lesbian, or similar slurs/derogatory words used insultingly) → classify as Homophobia.
    - If the text contains both Homophobic and Transphobic elements, prioritize the classification that represents the most specific or explicit form of hate speech present.
    - If TEXT contains content that does not reference or target sexual orientation or gender identity, or contains neutral, unrelated, or non-hateful content → classify as Non-LGBT.
    - Ambiguity: If no plausible determination can be made for label/reasoning, output "NA". For spans, always return [] if no hateful content is detected.
    - Strict Output Format: Your response MUST be valid JSON. Return ONLY the JSON object, WITHOUT markdown code fences (```json), introductory/concluding remarks, or any other extra text outside the JSON structure.
    - Do NOT copy placeholder texts; replace them with your actual predictions.

    Return ONLY JSON:
    {{
    "spans": [],
    "label": "<REPLACE WITH EITHER: Homophobia OR Transphobia OR Non-LGBT>",
    "reasoning": "<REPLACE WITH: short explanation for your classification decision>"
    }}
    """

def extract_json_text(output):
        try:
            match = re.search(r"\{.*\}", output, re.DOTALL)
            if match:
                return json.loads(match.group())
            else:
                return {
                    "label": "ERROR",
                    "spans": [],
                    "reasoning": "No JSON found"
                }
        except Exception as e:
            return {
                "label": "ERROR",
                "spans": [],
                "reasoning": str(e)
            }
    
def text_agent(text):
        try:
            print(f"[INFO] Text Agent: Starting processing ...")
            final_prompt = _TEXT_PROMPT.format(text=text)
            raw_output = call_gemini(final_prompt)
            parsed = extract_json_text(raw_output)

            prediction = {
                    
                    "predicted_label":parsed["label"],
                    "reasoning": parsed["reasoning"],
                    "spans": parsed["spans"]
                }
            print(f"[INFO] Text Agent: Finished processing ")
            return prediction
        except Exception as e :
            print(f"[ERROR] Text Agent: Error processing : {e}")
            return None