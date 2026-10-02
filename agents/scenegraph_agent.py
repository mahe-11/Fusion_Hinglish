import io
from PIL import Image
from services.agent_api_calls import call_gemini
import re
import json

_SCENEGRAPH_PROMPT="""
You are an expert in analyzing and understanding visual images to generate detailed and structured scene graphs in JSON-formatted outputs. You perform the following two tasks sequentially:

-Scene Graph Generation: For every image provided, identify all entities, objects, attributes, and relationships in the scene. The graph must include all common entities, whether singular or plural , such as "car," "person," "crowd," "tree," "building," etc., as well as their properties and the spatial or contextual relationships among them . Your goal is to create a complete and accurate representation of all visible elements in the scene.

-Graph Enhancement: Refine the scene graph by identifying and replacing the generic descriptions of entities that correspond to public figures provided in the input list. For instance, if a "person" in the scene is identified as a specific public figure, replace "person" with their provided name. During this process, ensure that: All entities, whether identified or unidentified, remain in the graph. All relationships between objects and entities are preserved. Unidentified or unrecognized entities are left unchanged but still included in the graph.

- Image Classification: Classify the image looking at the text and image seperately into EXACTLY ONE of the following   classes: Homophobic, Transphobic, or Non-LGBT.

- Important Rules For classification :
- Homophobia:
  Content that mocks, insults, stereotypes, or expresses hostility toward people based on sexual orientation (e.g., gay, lesbian, bisexual). Includes ridicule, derogatory language, or negative portrayals.

- Transphobia:
  Content that mocks, insults, misrepresents, or expresses hostility toward gender identity or gender expression (e.g., transgender, non-binary people). Includes misgendering, denial of identity, or derogatory references to gender transition or roles.

- Non-LGBT:
  Content that does not reference or target sexual orientation or gender identity, or contains neutral, unrelated, or non-hateful content.

- attempt to determine the 'temporal_stamp' (time or date) and 'geolocation' (country or continent) from visual cues in the image. If no clues are present, strictly output 'NA'.

-Your responses must be concise but thorough, breaking down the image into its components and interactions while ensuring that the scene graph remains fully intact, comprehensive , and user-friendly. Do not prune out entities or relationships during any part of the process.The objective is to provide users with a refined scene graph that includes all visible entities and incorporates specific public figure names where applicable, enhancing both clarity and usability. You may or may not be provided with the public figures present in the image. If present, ground them to their common nouns in their entities.

-You will return the output in the required response format. It is absolutely imperative that you return the JSON output and that it is always valid. Double-check your JSON for any syntax errors before returning it. You will extract the information required for the response format. If no plausible guess can be made for a field, output NA

Return ONLY JSON:
{
  "label": "Choose EXACTLY ONE: Homophobic | Transphobic | Non-LGBT",
  "scene_graph": {
    "temporal_stamp": "NA | YYYY-MM-DD HH:MM:SS",
    "geolocation": "NA | country or continent",
    "entities": [
      {
        "id": "E1",
        "name": "entity_name",
        "attributes": {
          "color": "",
          "size": "",
          "state": "",
          "position": "",
          "other": ""
        }
      }
    ],
    "relationships": [
      {
        "subject_id": "E1",
        "relation": "relation_type",
        "object_id": "E2"
      }
    ]
  },
  "enhanced": {
    "replaced_entities": [
      {
        "original": "person",
        "replacement": "public_figure_name"
      }
    ]
  }
}."""

def extract_json_scenegraph(output):
    if not isinstance(output, str):
        print(f"JSON extraction error: Input was not a string, got {type(output)}")
        return None

    # Attempt to find the outermost JSON object in the string
    match = re.search(r"({\s*\".*?\".*})", output, re.DOTALL)

    if match:
        json_str = match.group(1)
      
        while json_str:
            try:
                parsed = json.loads(json_str)
                break  # Successfully parsed
            except json.JSONDecodeError as e:
                if "Extra data" in str(e):
                   
                    json_str = json_str[:-1]
                else:
                 
                    print(f"JSON decoding error (non-'Extra data'): {e}. Problematic string (full):\n{json_str}")
                    return None
            except Exception as e:
                print(f"Unexpected error during JSON parsing attempt: {e}")
                return None
        if not json_str: 
            print(f"No valid JSON object found in output after trimming.\nOutput: {output[:500]}...")
            return None


        parsed.setdefault("label", "Non-LGBT")

        # Ensure 'scene_graph' is present and has default structure
        if "scene_graph" not in parsed:
            parsed["scene_graph"] = {"entities": [], "relationships": []}
        else:
            # Ensure nested 'entities' and 'relationships' are present
            parsed["scene_graph"].setdefault("entities", [])
            parsed["scene_graph"].setdefault("relationships", [])



        return parsed

    else:
        # If no JSON object is found, return None
        print(f"No JSON object found in output.\nOutput: {output[:500]}...")
        return None

def scenegraph_agent(image_bytes):
  try:
      print(f"[INFO] Scenegraph Agent: Starting processing ...")
      image = Image.open(io.BytesIO(image_bytes))
      final_prediction = call_gemini(_SCENEGRAPH_PROMPT, image)
      parsed_json_output = extract_json_scenegraph(final_prediction)

      # Handle case where JSON extraction failed
      if parsed_json_output is None:
          return None

      label = parsed_json_output.get("label", "Non-LGBT")
      scene_graph = parsed_json_output.get("scene_graph", {
            "entities": [],
            "relationships": []
        })

      if label not in ["Homophobia", "Transphobia", "Non-LGBT"]:
          match = re.search(r"(Homophobia|Transphobia|Non-LGBT)", final_prediction)
          if match:
            label = match.group(1)

      prediction = {
          "predicted_label": label,
          "scene_graph": scene_graph
      }
      print(f"[INFO] Scenegraph Agent: Finished processing ")
      return prediction
  except Exception as e:
      print(f"[ERROR] Scenegraph Agent: Error processing : {e}")
      return None