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

![Multi-Fusion Architecture](docs/architecture/Multi_Fusion%20Architecture2.png)

### Text Agent Architecture

![Text Agent Architecture](docs/architecture/Text_Agent_Arch.png)

### Image Agent Architecture

![Image Agent Architecture](docs/architecture/Image_Agent_arch.png)

### Scene Graph Agent Architecture

![Scene Graph Architecture](docs/architecture/SceneGraph_arch.png)

> **Note:** Place the four supplied architecture images inside `docs/architecture/` using the filenames shown above. If you use different filenames, update the image paths in this README.

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
