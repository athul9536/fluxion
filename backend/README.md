# Vani - Agricultural Helpline (IVR)

Voice-based agricultural Q&A for rural farmers. Farmer calls → speaks question → gets AI answer.

## Quick Start

```bash
# 1. Create virtual environment
python -m venv .venv
.venv\Scripts\activate   # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure
copy .env.example .env
# Edit .env with your keys

# 4. Run
uvicorn app.main:app --reload --port 8000
```

## Twilio Setup

1. Create free Twilio account at https://www.twilio.com/try-twilio
2. Get a phone number (trial gives you one free)
3. Copy Account SID and Auth Token to .env
4. Use ngrok to expose local server: `ngrok http 8000`
5. In Twilio Console → Phone Numbers → Configure your number:
   - Voice webhook: `https://your-ngrok-url.ngrok.io/ivr/voice`
   - Method: POST

## Call Flow

1. Farmer calls Twilio number
2. "Hello! Welcome to Vani. Are you calling from Alappuzha?"
3. Farmer says "yes"
4. "Please tell me your farming question"
5. Farmer asks question
6. AI answers using RAG + Azure OpenAI
7. "Do you have another question?"
8. Loop or goodbye

## Test Without Calling

```bash
# Test LLM directly
curl "http://localhost:8000/ivr/test?question=How%20do%20I%20treat%20rice%20blast"
```

## Project Structure

```
backend/
  app/
    main.py           # FastAPI app
    config.py         # Settings
    routers/
      ivr.py          # Twilio webhook handlers
    services/
      llm.py          # Azure OpenAI integration
      rag.py          # Document retrieval
      weather.py      # Weather context
  data/
    docs/             # Agricultural PDFs/guides for RAG
  requirements.txt
  .env.example
```
