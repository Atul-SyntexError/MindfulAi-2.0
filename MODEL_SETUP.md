# MindfulAI - Groq Model Configuration Guide

## ✅ Solution: Use Updated Models

MindfulAI has been updated to use **`openai/gpt-oss-120b`** by default, which is an officially supported production model as of August 2026.

### Currently Supported Models (Working ✅)

**Production Models** (Recommended):
- ✅ `openai/gpt-oss-120b` - 500 T/sec (DEFAULT - Recommended)
- ✅ `openai/gpt-oss-20b` - 1000 T/sec (Faster)
- ✅ `llama-3.1-8b-instant` - 560 T/sec

**Preview Models**:
- ✅ `qwen/qwen3.6-27b` - 500 T/sec
- ✅ `qwen/qwen3.8-27b` - 450 T/sec

## How to Configure (Optional)

If you want to use a different model, create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-120b
GROQ_MAX_TOKENS=1024
GROQ_TEMPERATURE=0.7
```

Then restart the app:

```bash
python -m streamlit run app.py
```

## Decommissioned Models (Don't Use)
❌ `llama-3.3-70b-versatile`
❌ `mixtral-8x7b-32768`
❌ `llama-3.1-70b-versatile`
❌ `llama-3-70b-8192`
❌ `gemma-7b-it`
❌ `mistral-7b-instruct-v0.2`
❌ `llama2-70b-4096`

## Need Help?
- Groq Supported Models: https://console.groq.com/docs/supported-models
- Deprecations Page: https://console.groq.com/docs/deprecations
