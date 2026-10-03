# Fusion Hinglish: Multi-Agent Meme Analysis

A Streamlit application that analyses meme images using a multi-agent AI pipeline. It combines OCR-based text analysis, visual analysis, scene-graph generation, and a final fusion agent to classify a meme into one of three categories:

- **Homophobia**
- **Transphobia**
- **Non-LGBT**

The system is designed around Hinglish and Devanagari meme analysis, with separate agents examining different aspects of the input before a final agent combines their findings.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [How It Works](#how-it-works)
- [Agents](#agents)
- [Output](#output)
- [Project Structure](#project-structure)
- [Technologies](#technologies)
- [Setup and Installation](#setup-and-installation)
- [API Configuration](#api-configuration)
- [Running the Application](#running-the-application)
- [Dataset](#dataset)
- [Limitations](#limitations)

---



## Overview

Memes often communicate meaning through a combination of text, images, symbols, expressions, and contextual references. Analysing only the text or only the visual content may miss important signals.

Fusion Hinglish addresses this by using multiple specialised agents:

1. The **Text Agent** analyses OCR-extracted text.
2. The **Image Agent** analyses image regions and the complete meme.
3. The **Scene Graph Agent** identifies entities, attributes, and relationships in the image.
4. The **Multi-Fusion Agent** combines the outputs from the three agents and produces the final classification and explanation.

The application provides a Streamlit interface where users can upload a meme and review the model's prediction and reasoning.

---

## Architecture

### Overall Multi-Agent Architecture

![Multi-Fusion Architecture]<img width="1681" height="936" alt="Multi_Fusion Architecture2" src="https://github.com/user-attachments/assets/2a45176c-1f4c-4d6d-a3be-89f607d7ee5b" />
)

### Text Agent Architecture

![Text Agent Architecture]<img width="1024" height="1536" alt="Text_Agent_Arch" src="https://github.com/user-attachments/assets/db08fdd8-e6be-4773-b3d4-e49e87a00396" />
)

### Image Agent Architecture

![Image Agent Architecture]<img width="1024" height="1536" alt="Image_Agent_arch" src="https://github.com/user-attachments/assets/55575153-2cf2-4faf-aca9-c67f7e3bbddc" />
)

### Scene Graph Agent Architecture

![Scene Graph Architecture]<img width="1024" height="1536" alt="SceneGraph_arch" src="https://github.com/user-attachments/assets/7e294e9c-46db-4b11-872a-c060dbd48cb7" />
)

> 

---

## How It Works

The application follows this workflow:

```text
                    Input Meme Image
                           |
                           v
                     OCR Extraction
                           |
             +-------------+-------------+
             |             |             |
             v             v             v
         Text Agent    Image Agent   Scene Graph Agent
             |             |             |
             |             |             |
             v             v             v
       Text Analysis   Visual Analysis  Scene Graph
             |             |             |
             +-------------+-------------+
                           |
                           v
                    Multi-Fusion Agent
                           |
                           v
                    Final Prediction
                           |
             +-------------+-------------+
             |             |             |
             v             v             v
           Label         Summary       Reasoning
## Project Structure
```

```text
FusionApp/
│
├── agents/
│   ├── __init__.py
│   ├── text_agent.py
│   ├── image_agent.py
│   ├── scenegraph_agent.py
│   └── fusion_agent.py
│
├── services/
│   ├── __init__.py
│   └── agent_api_calls.py
│
├── Dataset/
│   ├── English/
│   │   └── Test_English/
│   │
│   ├── Hindi/
│   │   └── test/
│   │
│   └── Chinese/
│       └── Test_images_chinese/
│
├── fusion_app.py
├── requirements.txt
├── README.md
├── .gitignore
│
└── docs/
    └── architecture/
        ├── Multi_Fusion Architecture2.png
        ├── Text_Agent_Arch.png
        ├── Image_Agent_arch.png
        └── SceneGraph_arch.png
