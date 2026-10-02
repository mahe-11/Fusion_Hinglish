from services.agent_api_calls import call_claude  
import json
import re

_MULTI_FUSION_PROMPT = """
You are an expert multimodal hate-speech classifier.
You must classify the attached meme into ONE of: Homophobia | Transphobia | Non-LGBT.
Use ALL of the following evidence in an interleaved chain-of-thought before giving your final answer. Think step-by-step, referencing each evidence source explicitly.

### Evidence 1  - Text Agent
Predicted Label : {text_predicted_label}
Detected Spans  : {text_spans}
Reasoning       : {text_reasoning}

### Evidence 2 - Image Agent
Predicted Label : {image_predicted_label}
Reasoning       : {image_reasoning}
Tiles Used      : {used_chunks}

Tile Descriptions:
{tile_descriptions}

### Evidence 3 - Scene Graph Agent
Predicted Label : {scenegraph_predicted_label}

Scene Entities:
{scene_entities}

Scene Relationships:
{scene_relationships}

Now synthesise ALL evidence above.
Write a chain-of-thought that:
  1. Evaluates the Text Agent evidence (slurs, spans, language).
  2. Evaluates the Image Agent evidence (visual content, tiles, layout).
  3. Evaluates the Scene Graph evidence (entities, relationships, visual structure).
  4. Resolves any conflicts between agents.
  5. Arrives at a final consolidated label.

Respond ONLY with valid JSON (no markdown fences):
{{
  "label"     : "<Homophobia | Transphobia | Non-LGBT>",
  "summary": "<1-2 sentence explanation of the final decision>",
  "reasoning" : "<full multi-step chain-of-thought referencing all 3 agents>"
}}
"""


def extract_json_fusion(output):
    try:
        if not isinstance(output, str):
            print(f"JSON extraction error: Input was not a string, got {type(output)}")
            return {
                "label": "ERROR",
                "reasoning": "Fusion agent output was not a string"
            }


        json_code_block_match = re.search(r"```json\s*(\{.*?})\s*```", output, re.DOTALL)
        if json_code_block_match:
            json_str = json_code_block_match.group(1)
            
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"JSON decoding error (code block) in fusion agent output: {e}. Problematic string (full):\n{json_str}")
                pass


        match = re.search(r"(\{.*?})", output, re.DOTALL)
        if match:
            json_str = match.group(1)
            if not json_str.strip():
                print(f"JSON extraction found empty/whitespace string. Output:\n{output[:500]}...")
                return {
                    "label": "ERROR",
                    "reasoning": "Extracted JSON string was empty or only whitespace."
                }

            while json_str:
                try:
                    parsed = json.loads(json_str)
                    return parsed
                except json.JSONDecodeError as e:
                    if "Extra data" in str(e):
                        json_str = json_str[:-1]
                    else:
                        print(f"JSON decoding error (general, non-trimming): {e}. Problematic string (full):\n{json_str}")
                        return {
                            "label": "ERROR",
                            "reasoning": f"Failed to parse JSON: {e}"
                        }
                except Exception as e:
                    print(f"Unexpected error during JSON parsing attempt (general): {e}")
                    return {
                        "label": "ERROR",
                        "reasoning": f"Unexpected error during JSON parsing: {e}"
                    }

            print(f"No valid JSON object found in output after trimming.\nOutput: {output[:500]}...")
            return {
                "label": "ERROR",
                "reasoning": "No valid JSON object found after trimming."
            }
        else:
            print(f"No JSON object found in fusion agent output.\nOutput: {output[:500]}...")
            return {
                "label": "ERROR",
                "reasoning": "No JSON object found in fusion agent output"
            }
    except Exception as e:
        print(f"An unexpected error occurred within extract_json_fusion: {e}. Original output:\n{output[:500]}...")
        return {
            "label": "ERROR",
            "reasoning": f"Unexpected error in JSON extraction logic: {e}"
        }


def fusion_agent(
    text_agent_prediction,
    image_agent_prediction,
    scenegraph_agent_prediction,
):
    try:
        print(f"[INFO] Fusion Agent Starting processing ...")

        # Provide default empty dicts if agent predictions are None
        text_pred = text_agent_prediction or {}
        image_pred = image_agent_prediction or {}
        scenegraph_pred = scenegraph_agent_prediction or {}

        final_prompt = _MULTI_FUSION_PROMPT.format(
            text_predicted_label=text_pred.get("predicted_label", "N/A"),
            text_spans=text_pred.get("spans", []),
            text_reasoning=text_pred.get("reasoning", "N/A"),

            image_predicted_label=image_pred.get("predicted_label", "N/A"),
            image_reasoning=image_pred.get("reasoning", "N/A"),
            used_chunks=image_pred.get("used_chunks", []),

            tile_descriptions="\n".join(
                f"  • Tile {d['tile']}: {d['description']}"
                for d in image_pred.get("used_chunk_details", [])
            ),

            scenegraph_predicted_label=scenegraph_pred.get(
                "predicted_label", "N/A"
            ),

            scene_entities="\n".join(
                f"  • [{e['id']}] {e['name']} — {e['attributes']}"
                for e in scenegraph_pred.get(
                    "scene_graph", {}
                ).get("entities", [])
            ),

            scene_relationships="\n".join(
                f"  • {r['subject_id']} → {r['relation']} → {r['object_id']}"
                for r in scenegraph_pred.get(
                    "scene_graph", {}
                ).get("relationships", [])
            )
        )
       
        raw_output = call_claude(final_prompt)

        prediction = extract_json_fusion(raw_output)

        print(f"[INFO] Fusion Agent: Finished processing .")
        return prediction

    except Exception as e:
        print(f"[ERROR] Fusion Agent: Error processing : {e}")
        return None