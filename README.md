<div align="center">

# 🧠 MindfulAI

### Your Personal Mental Wellbeing Companion

*An AI-powered mental health assistant using evidence-based CBT techniques,
built with Streamlit & Groq LLM*
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-FF4B4B?logo=streamlit)](https://streamlit.io)
[![Groq](https://img.shields.io/badge/Groq-GPT--OSS_120B-F55036?logo=groq)](https://groq.com)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](#license)

</div>

---

## ✨ Features

| Feature                    | Description                                                              |
| :------------------------- | :----------------------------------------------------------------------- |
| 🎭 **Mood Tracking**       | Select your current mood with emoji-based picker; visualized over time   |
| 🎙️ **Voice Input (EN/HI)** | Speak instead of typing — English, Hindi, or best-effort auto-detect     |
| 📊 **Stress & Sleep Logs** | Quick slider/dropdown check-ins; personalized tips based on trends       |
| 📝 **Guided Journaling**   | Free-form journal entries that feed context to the AI                    |
| 🧘 **CBT-Based Prompting** | Validate → Explore → Reframe → Empower framework, hidden in natural tone |
| 🔒 **Safety Layer**        | Real-time crisis keyword detection with immediate hotline resources      |
| 📈 **Mood Trend Chart**    | Interactive Plotly sparkline in the sidebar                              |
| 💡 **Wellness Tips**       | Dynamic tips based on your stress and sleep averages                     |
| 💬 **Streaming Responses** | Token-by-token streaming for a natural chat experience                   |
| 🧠 **Context Memory**      | Conversation summarization keeps context within LLM window limits       |
| 🎨 **Professional Interface** | Calm editorial layout with responsive controls and clear hierarchy |

---

## 📸 Preview

> The app features a calm editorial UI with warm surfaces, focused chat bubbles, and a
> sidebar for mood tracking, journaling, and wellness insights.

---

## 🏗️ Architecture

```
MindfulAI/
├── app.py                  # Main Streamlit entry point
├── config.py               # Configuration & environment loading
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── .gitignore
│
├── .streamlit/
│   └── config.toml         # Streamlit theme configuration
│
├── assets/
│   └── style.css           # Responsive application theme
│
├── components/             # UI layer
│   ├── __init__.py
│   ├── chat.py             # Header, welcome card, message renderer
│   └── sidebar.py          # Mood picker, sliders, journal, tips, chart
│
├── prompts/                # Prompt engineering
│   ├── __init__.py
│   └── templates.py        # System prompt, context builder, summary prompt
│
├── services/               # Business logic
│   ├── __init__.py
│   ├── llm.py              # Groq API wrapper (streaming + sync)
│   └── memory.py           # Session state, context window, mood/stress logs
│
└── utils/                  # Shared utilities
    ├── __init__.py
    ├── safety.py            # Crisis keyword detection + resource card
    └── helpers.py           # Timestamps, formatters, validators
```

---

## 🎙️ Voice Input

Click the microphone widget above the chat box to speak instead of typing.

- Choose **English**, **Hindi**, or **Auto Detect** in the sidebar under "Voice Language" before recording.
- Recording happens entirely in your browser (no extra software needed); the audio is transcribed server-side and fed into the **exact same** chat pipeline as typed messages — same safety checks, same CBT-guided model, same everything.
- "Auto Detect" is a best-effort heuristic: it tries both English and Hindi recognition, prefers a Hindi result if it actually contains Devanagari script (a reliable signal), and otherwise falls back to whichever result reported higher confidence. The underlying free speech API has no official language-ID mode and its confidence scores are often unreliable, so this is a heuristic — not a guaranteed detector.
- If nothing is recognized, you'll see *"Couldn't understand the audio. Please try again."* — just re-record or type instead.

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **Groq API Key** — get one free at [console.groq.com](https://console.groq.com)

### 1. Clone the repository

```bash
git clone https://github.com/Atul-SyntexError/MindfulAi-2.0.git
cd MindfulAi-2.0
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up your API key

```bash
# Copy the example env file
cp .env.example .env       # macOS/Linux
copy .env.example .env     # Windows

# Edit .env and replace the placeholder with your actual Groq API key
```

Keep `.env` local. Never commit API keys to GitHub; for Streamlit Cloud, add the key
under **Settings → Secrets** instead.

### 5. Run the app

```bash
streamlit run app.py
```

The app opens at **http://localhost:8501** 🎉

---

## ⚙️ Configuration

All settings are controlled via environment variables (`.env` file):

| Variable            | Default                    | Description                     |
| :------------------ | :------------------------- | :------------------------------ |
| `GROQ_API_KEY`      | *(required)*               | Your Groq API key               |
| `GROQ_MODEL`        | `openai/gpt-oss-120b`      | Groq model to use               |
| `GROQ_MAX_TOKENS`   | `1024`                     | Max tokens per response         |
| `GROQ_TEMPERATURE`  | `0.7`                      | Response creativity (0.0 – 1.0) |
| `LOG_LEVEL`         | `INFO`                     | Python logging level            |

> Groq periodically deprecates older models (e.g. `llama-3.3-70b-versatile` was
> retired in August 2026). See [`MODEL_SETUP.md`](MODEL_SETUP.md) for the
> current list of supported/decommissioned models before changing `GROQ_MODEL`.

---

## 🧘 How the CBT Framework Works

The system prompt uses a 4-step cognitive-behavioral approach — invisible to the user but guiding every response:

1. **Validate** — acknowledge the user's feelings without judgment
2. **Explore** — ask one focused question to understand context
3. **Reframe** — gently offer a new perspective (cognitive restructuring)
4. **Empower** — suggest one small, actionable step

The prompt adapts dynamically based on:
- Current mood selection
- Stress level trends
- Sleep quality
- Journal entries
- Conversation history

---

## 🔒 Safety

MindfulAI includes a real-time safety layer:

- Crisis keywords are matched against user input with regex, in **both English and
  Hindi** (Devanagari + common Romanized/Hinglish phrases) — this matters because
  voice input is transcribed to plain text before it reaches this check, so a
  Hindi disclosure spoken aloud is caught exactly like a typed English one
- If triggered, the AI immediately shows **crisis hotline numbers** for USA, India, UK, and international
- The AI **does not** attempt to counsel through acute crisis — it directs to professionals
- A permanent disclaimer footer reinforces that this is **not** a substitute for professional care
- The keyword list is necessarily incomplete — it is a heuristic safety net, not a
  substitute for professional crisis screening

---

## 🚢 Deployment

### Streamlit Cloud (Easiest)

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Set **Main file path**: `app.py`
5. In the app settings, open **Secrets** and add the key there. Do not add it to GitHub:
  ```toml
  GROQ_API_KEY = "your_new_key_here"
  ```
6. Click **Deploy** ✅

The key stays on Streamlit's server and is used by the app backend. Visitors only see
the public app link and never receive the key or need to enter one. The repository's
`.gitignore` excludes both `.env` and `.streamlit/secrets.toml`.

> **Public app note:** Anyone with the link can send messages through your Groq account.
> Monitor usage and revoke the deployment secret if you stop using the app. Add
> authentication or rate limiting before sharing it widely if usage costs matter.

### Render

1. Create a new **Web Service** on [render.com](https://render.com)
2. Connect your GitHub repo
3. Set:
   - **Build command**: `pip install -r requirements.txt`
   - **Start command**: `streamlit run app.py --server.port $PORT --server.headless true`
4. Add `GROQ_API_KEY` as an environment variable
5. Deploy ✅

### Railway

1. Create a new project on [railway.app](https://railway.app)
2. Connect your GitHub repo
3. Add a `Procfile`:
   ```
   web: streamlit run app.py --server.port $PORT --server.headless true
   ```
4. Add `GROQ_API_KEY` in Variables
5. Deploy ✅

---

## 🛠️ Development

```bash
# Run with auto-reload (default)
streamlit run app.py

# Enable debug logging
LOG_LEVEL=DEBUG streamlit run app.py
```

### Project modules

| Module              | Responsibility                                    |
| :------------------ | :------------------------------------------------ |
| `config.py`         | Loads `.env`, defines all constants and settings   |
| `services/llm.py`   | Groq API calls with streaming and error handling  |
| `services/memory.py` | Session state, context window, summarization     |
| `prompts/templates.py` | System prompt, context builder, summary prompt |
| `utils/safety.py`   | Crisis detection and resource card                |
| `utils/helpers.py`   | Shared utility functions                         |
| `components/chat.py` | Header, welcome card, message renderer           |
| `components/sidebar.py` | Sidebar UI (mood, stress, sleep, journal, tips) |

---

## ⚠️ Known Limitations

- **Hinglish recognition**: the free Google Web Speech backend has no dedicated
  Hinglish (code-mixed) model. Mixed-language sentences work only as well as
  the underlying `en-IN`/`hi-IN` models handle them individually — expect
  lower accuracy than pure English or pure Hindi speech.
- **Auto Detect** is a best-effort heuristic (see Voice Input above), not a
  guaranteed language identifier.
- **Microphone permission / hardware errors** (denied permission, no
  microphone, unsupported browser) are surfaced by the browser and by
  Streamlit's `st.audio_input` widget itself; the app cannot detect or
  message these specific states from Python, but it never crashes because
  of them.
- **Mobile/responsive layout**: the CSS uses relative units and a responsive
  grid, but this project has **not** been verified in a real mobile browser
  or on physical devices — treat mobile layout as `NOT VERIFIED` until
  tested on-device.
- The crisis-keyword safety net (English + Hindi) is necessarily incomplete
  and pattern-based; it is not a substitute for professional crisis
  screening.

---

## ⚠️ Disclaimer

> **MindfulAI is an AI companion, not a licensed therapist or medical professional.**
> It does not provide diagnoses, treatment plans, or medication advice.
> If you are experiencing a mental health crisis, please contact your local emergency services
> or a crisis hotline immediately.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">
  <sub>Built with 💜 using Streamlit + Groq</sub>
</div>
<div align="center">
  <sub>Copyright (c) Prince Atul</sub>
</div>
