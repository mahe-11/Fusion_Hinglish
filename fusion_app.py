"""A polished Streamlit GUI for sending a meme image to a classification backend."""

from __future__ import annotations
import re
import io
import json
import requests
import streamlit as st
from PIL import Image
import json
import sys
from PIL import Image
from agents.text_agent import text_agent
from agents.image_agent import image_agent
from agents.scenegraph_agent import scenegraph_agent
from agents.fusion_agent import fusion_agent

st.set_page_config(page_title="Multi Agent Fusion", page_icon="M", layout="wide")

st.markdown(
    """
    <style>
      .stApp {
        background:
          radial-gradient(circle at 8% 5%, rgba(255, 104, 143, .30), transparent 28rem),
          radial-gradient(circle at 92% 12%, rgba(37, 218, 233, .21), transparent 29rem),
          radial-gradient(circle at 50% 100%, rgba(122, 92, 255, .18), transparent 30rem),
          #10101d;
        color: #f7f6ff;
      }
      #MainMenu, footer {visibility: hidden;}
      .block-container {max-width: 820px; margin: 0 auto; padding-top: 4.5rem; padding-bottom: 4rem;}
      .eyebrow {color: #75edf1; font-size: .78rem; font-weight: 800; letter-spacing: .16em; text-transform: uppercase; text-align: center;}
      .hero-title {font-size: clamp(2.4rem, 6vw, 4.8rem); font-weight: 850; line-height: .96; letter-spacing: -.065em; margin: .55rem 0 1rem; text-align: center;}
      .gradient-text {background: linear-gradient(100deg, #ff84aa 7%, #a890ff 44%, #67e9ee 88%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
      .hero-copy {color: #d4d1e5; font-size: 1.08rem; line-height: 1.65; max-width: 38rem; margin: 0 auto; text-align: center !important;}
      .glass-card {background: rgba(24, 23, 39, .77); border: 1px solid rgba(255,255,255,.11); border-radius: 22px; padding: 1.35rem; box-shadow: 0 18px 60px rgba(0,0,0,.25);}
      .step-card {min-height: 92px; display: flex; flex-direction: column; justify-content: center;}
      .step-purple {background: linear-gradient(135deg, rgba(255, 104, 143, .29), rgba(125, 52, 105, .32)); border-color: rgba(255, 155, 185, .48);}
      .step-teal {background: linear-gradient(135deg, rgba(37, 218, 233, .24), rgba(25, 95, 122, .32)); border-color: rgba(111, 239, 244, .42);}
      .step-amber {background: linear-gradient(135deg, rgba(173, 137, 255, .28), rgba(74, 57, 136, .32)); border-color: rgba(197, 176, 255, .46);}
      .result-card {background: linear-gradient(135deg, rgba(117, 87, 224, .25), rgba(24, 23, 39, .88) 62%); border-color: rgba(181, 157, 255, .36);}
      .confidence-card {background: linear-gradient(145deg, rgba(43, 208, 169, .25), rgba(24, 23, 39, .88)); border-color: rgba(103, 238, 210, .35);}
      .section-label {font-size: .78rem; font-weight: 800; letter-spacing: .13em; text-transform: uppercase; color: #9a99ad; margin-bottom: .65rem; text-align: center;}
      .result-title {font-size: 1.8rem; font-weight: 750; margin: .1rem 0 .4rem;}
      .result-copy {color: #c7c5d3; line-height: 1.65; margin: 0;}
      .status-pill {display: inline-block; color: #a4f8df; background: rgba(39, 200, 156, .12); border: 1px solid rgba(77, 229, 185, .24); border-radius: 999px; font-size: .78rem; font-weight: 750; padding: .35rem .68rem;}
      .metric {font-size: 2rem; font-weight: 800; letter-spacing: -.05em; color: #65ecd0; margin-top: .15rem;}
      .hint {color: #8e8c9e; font-size: .88rem; text-align: center;}
      div[data-testid="stFileUploader"] {background: rgba(255,255,255,.035); border: 1px dashed rgba(178,157,255,.58); border-radius: 16px; padding: .4rem .7rem;}
      div[data-testid="stFileUploader"] section {padding: 1.25rem .5rem;}
      div[data-testid="stFileUploader"] button {border-radius: 10px;}
      .stButton > button {width: 100%; border: 0; border-radius: 12px; padding: .75rem 1rem; font-size: 1rem; font-weight: 750; color: #10101c; background: linear-gradient(100deg, #b49fff, #62e9cf); transition: transform .15s ease, box-shadow .15s ease;}
      .stButton > button:hover {transform: translateY(-2px); box-shadow: 0 10px 25px rgba(103,232,211,.22); color: #10101c;}
      div[data-testid="stImage"] img {border-radius: 15px; border: 1px solid rgba(255,255,255,.12); max-height: 460px; object-fit: contain;}
      div[data-testid="stExpander"] {border: 1px solid rgba(255,255,255,.11); border-radius: 12px; background: rgba(255,255,255,.025);}
        .agent-card{
            background: rgba(255,255,255,0.03);
            border:1px solid rgba(255,255,255,0.08);
            border-left:4px solid #74efe8;
            border-radius:14px;
            padding:18px;
            margin-bottom:16px;
            transition:0.2s;
        }

        .agent-card:hover{
            border-color:#74efe8;
            background:rgba(255,255,255,0.045);
        }

        .agent-title{
            color:#74efe8;
            font-size:1.05rem;
            font-weight:700;
            margin-bottom:12px;
        }

        .agent-body{
            color:#d0d2de;
            font-size:0.96rem;
            line-height:1.75;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

def get_ocr_text(image_bytes,filename,content_type):
        print("EXtracting OCR")
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            OCR_URL = "https://uniformed-tall-dorsal.ngrok-free.dev/ocr"

            response = requests.post(
                    OCR_URL,
                    files={
                        "image": (
                            filename,
                            image_bytes,
                            content_type
                        )
                    },
                    timeout=300
                )

            print("Status:", response.status_code)
            print("Response:")

            data = response.json()

            print(data)

            ocr_text = data["ocr_text"]
            
            print(ocr_text)
            print("OCR EXTRACTION FINISHED")
            return ocr_text
        except Exception as e:
            print(e)
        return ""


def analyse_meme(image_bytes: bytes, filename: str, content_type: str | None):
    
    extracted_text = get_ocr_text(
        image_bytes,
        filename,
        content_type
    ) or ""
    print(extracted_text)
    text_agent_response=text_agent(extracted_text) or ""
    print("Text agent Response : ",text_agent_response)
    image_agent_response=image_agent(image_bytes) or ""
    print("image agent response :",image_agent_response)
    scenegraph_agent_response =scenegraph_agent(image_bytes) or ""
    print("scene graph agent response",scenegraph_agent_response)

    final_fusion_prediction = fusion_agent(text_agent_prediction=text_agent_response,
                                           image_agent_prediction=image_agent_response,
                                           scenegraph_agent_prediction=scenegraph_agent_response) or ""
    
    print("Final Prediction :",final_fusion_prediction)
    return {
    "label": final_fusion_prediction["label"],
    "summary": final_fusion_prediction["summary"],
    "reasoning": final_fusion_prediction["reasoning"]
}


if "analysis" not in st.session_state:
    st.session_state.analysis = None
if "analysed_filename" not in st.session_state:
    st.session_state.analysed_filename = None

st.markdown('<div class="eyebrow"></div>', unsafe_allow_html=True)
st.markdown('<div class="hero-title">Fuse the Evidence<br><span class="gradient-text">Understand the meme.</span></div>', unsafe_allow_html=True)
st.markdown('<p class="hero-copy">Drop in meme image and let your model identify its category, context, and reasoning in seconds.</p>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

guide_a, guide_b, guide_c = st.columns(3, gap="small")
for column, number, label in (
    (guide_a, "01", "Upload an image"),
    (guide_b, "02", "Run analysis"),
    (guide_c, "03", "Review results"),
):
    with column:
        color_class = ("step-purple", "step-teal", "step-amber")[int(number) - 1]
        st.markdown(f'<div class="glass-card step-card {color_class}"><div class="section-label">{number}</div><div style="text-align:center; font-weight:700;">{label}</div></div>', unsafe_allow_html=True)
        
st.markdown('<div style="height: 1.5rem;"></div>', unsafe_allow_html=True)

upload_left, upload_center, upload_right = st.columns([1, 5, 1])
with upload_center:
    uploaded_file = st.file_uploader(
        "Upload your meme",
        type=["png", "jpg", "jpeg", "webp"],
        help="Supported formats: PNG, JPG/JPEG, and WebP.",
        label_visibility="collapsed",
    )

    if uploaded_file:
        image_bytes = uploaded_file.getvalue()
        try:
            image = Image.open(io.BytesIO(image_bytes))
            st.image(image, caption=uploaded_file.name, use_container_width=True)
        except OSError:
            st.error("This file could not be opened as an image.")
            image_bytes = None

        if image_bytes and st.button("Analyse this meme"):
            with st.spinner("Your model is reading the meme..."):
                try:
                    st.session_state.analysis = analyse_meme(image_bytes, uploaded_file.name, uploaded_file.type)
                    st.session_state.analysed_filename = uploaded_file.name
                except requests.RequestException as exc:
                    st.session_state.analysis = None
                    st.error(f"Could not reach the backend: {exc}")
                except (ValueError, json.JSONDecodeError) as exc:
                    st.session_state.analysis = None
                    st.error(f"The backend returned an invalid response: {exc}")
    else:
        st.markdown('<p class="hint">PNG, JPG, JPEG, or WebP &middot; Your image is sent only when you choose Analyse.</p>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

result = st.session_state.analysis
if result:
    label = str(result.get("label", "Not provided"))
    summary = result.get("summary", "No summary available.")
    reasoning = str(result.get("reasoning", "No detailed analysis available."))

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">Model Output</div>', unsafe_allow_html=True)

    result_col, label_col = st.columns([4.5,1.5])
   
    with result_col:

        st.markdown(f"""

            <div class="glass-card result-card">
                <span class="status-pill">
                  ANALYSIS COMPLETE
                </span>
            
            {summary}
            </div>
            """,
            unsafe_allow_html=True,
        )

  
    with label_col:

        colors = {
                "Homophobia": "#ff6b6b",
                "Transphobia": "#ff9f43",
                "Non-LGBT": "#66e0b3"
            }

        st.markdown(f"""
            <div class="glass-card confidence-card">

            <div class="section-label">
            Prediction
            </div>

            <h2 style="
            text-align:center;
            margin-top:18px;
            color:{colors.get(label,'white')};
            font-size:20px;
            ">
            {label}
            </h2>

            </div>
            """,
            unsafe_allow_html=True,
        )

   
    sections = re.split(r"Step\s*\d+\s*-\s*", reasoning)
    sections = [s.strip() for s in sections if s.strip()]

    titles = [
            "📄 Text Agent",
            "🖼️ Image Agent",
            "🌐 Scene Graph Agent",
            "⚖️ Conflict Resolution",
            "✅ Final Decision",
        ]

        # Remove repeated prefixes
    prefixes = [
            r"Text Agent Evidence:",
            r"Image Agent Evidence:",
            r"Scene Graph Evidence:",
            r"Conflict Resolution:",
            r"Final Label:"
        ]

    st.markdown("### Detailed Reasoning")

    for i in range(min(len(sections), len(titles))):

            body = re.sub(
                prefixes[i],
                "",
                sections[i],
                flags=re.IGNORECASE,
            ).strip()

            st.markdown(
                f"""
        <div class="agent-card">

        <div class="agent-title">
        {titles[i]}
        </div>

        <div class="agent-body">
        {body}
        </div>

        </div>
        """,
                unsafe_allow_html=True,
            )


    with st.expander("Raw Backend Response"):
        st.json(result)