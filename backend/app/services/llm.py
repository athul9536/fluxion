"""Azure OpenAI LLM service for agricultural Q&A."""
import re

import requests

from ..config import settings
from . import rag
from . import weather as weather_svc

# Symbols that a text-to-speech engine reads badly or literally
_SPOKEN_REPLACEMENTS = {
    "°C": " degrees celsius",
    "°": " degrees",
    "–": " to ",
    "—": " ",
    "%": " percent",
    "&": " and ",
    "/": " or ",
    "’": "'",
    "“": "",
    "”": "",
}


FALLBACK_ANSWER = (
    "Sorry, I did not quite catch that. "
    "Please tell me the crop name and the problem you are seeing."
)

# An answer needs real words to be worth speaking; the model occasionally
# returns just punctuation when the transcription was nonsense.
MIN_ANSWER_WORDS = 4


def _is_speakable(text: str) -> bool:
    words = re.findall(r"[A-Za-z]{2,}", text)
    return len(words) >= MIN_ANSWER_WORDS


def clean_for_speech(text: str) -> str:
    """Strip markdown and symbols so Twilio's TTS reads naturally."""
    # Markdown emphasis, headings, code ticks, list bullets
    text = re.sub(r"\*\*|\*|__|`|#+", "", text)
    text = re.sub(r"^\s*[-•]\s*", "", text, flags=re.MULTILINE)

    for symbol, spoken in _SPOKEN_REPLACEMENTS.items():
        text = text.replace(symbol, spoken)

    # Drop anything still outside plain ASCII, then tidy whitespace
    text = text.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", text).strip()


def _build_system_prompt(location: str | None, weather: dict,
                         rag_context: str) -> str:
    where = f"{location} district, Kerala, India" if location else "Kerala, India"

    weather_info = ""
    if weather and not weather.get("stub"):
        weather_info = (
            f"Current weather in {where}: {weather['summary']}, "
            f"{weather['temp_c']}°C, humidity {weather['humidity']}%."
        )

    return f"""You are Vani, an agricultural advisor for farmers in {where}.
You give practical, actionable advice about crops, diseases, pests and farming practices.
Tailor advice to this area's climate, soil and growing seasons where it matters.

Answer whatever the farmer asks. Most questions will be about farming, but
help with anything else they raise too.

Rules for your reply, because it will be read aloud over a phone call:
- Answer in at most 2 short sentences. Never exceed 45 words.
- Never use markdown, asterisks, bullet points, or special symbols.
- Write units as words, for example "twenty to thirty five degrees celsius".
- If you are unsure, say so plainly rather than inventing specifics.

The caller's words come from imperfect phone speech recognition and may be
garbled or contain wrong words that sound similar. Work out what a farmer most
likely meant and answer that. Only if it is truly unintelligible, ask them to
repeat.

{weather_info}

{rag_context}"""


def ask(question: str, location: str | None = None) -> str:
    """Get AI answer for a farmer's question using direct HTTP request.

    `location` is the farmer's district, resolved from the pincode they keyed
    in. None means we could not place them, so the advice stays general.
    """
    
    # Get weather context
    weather = weather_svc.get_weather(settings.default_lat, settings.default_lng)
    
    # Get RAG context from agricultural docs
    rag_context = rag.get_context_string(question)
    
    system_prompt = _build_system_prompt(location, weather, rag_context)
    
    try:
        # Use direct HTTP request to Azure OpenAI
        url = f"{settings.azure_openai_endpoint}/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "api-key": settings.azure_openai_key,
        }
        
        payload = {
            "model": settings.azure_openai_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question},
            ],
            # This is a reasoning model: it spends tokens thinking before it
            # writes. A low cap leaves nothing for the actual answer, so the
            # budget has to cover reasoning plus output.
            "max_completion_tokens": 1000,
            # Default reasoning takes ~18s, far too slow for a live call.
            "reasoning_effort": "low",
        }

        response = requests.post(url, headers=headers, json=payload, timeout=45)
        response.raise_for_status()

        data = response.json()
        raw = data["choices"][0]["message"].get("content") or ""
        answer = clean_for_speech(raw)

        if not _is_speakable(answer):
            # Never hand back silence or a stray comma: the model sometimes
            # emits near-empty output when the transcription was nonsense.
            finish = data["choices"][0].get("finish_reason")
            print(f"LLM output not speakable ({answer!r}, finish={finish})")
            return FALLBACK_ANSWER

        return answer
        
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        print(f"LLM HTTP error: {error_msg}")
        
        # Try to get more details from response
        try:
            if hasattr(e, 'response') and e.response is not None:
                error_detail = e.response.text
                print(f"Response body: {error_detail}")
                return f"API Error: {error_detail[:150]}"
        except:
            pass
        
        return f"Connection error: {error_msg[:100]}"
    except Exception as e:
        print(f"LLM error: {e}")
        return f"Error: {str(e)[:100]}"


def test_connection():
    """Test the LLM connection and return detailed error."""
    try:
        url = f"{settings.azure_openai_endpoint}/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "api-key": settings.azure_openai_key,
        }
        
        payload = {
            "model": settings.azure_openai_model,
            "messages": [{"role": "user", "content": "Say hello"}],
            "max_completion_tokens": 10,
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            return {"status": "ok", "response": data["choices"][0]["message"]["content"]}
        else:
            return {
                "status": "error", 
                "code": response.status_code,
                "error": response.text[:500],
                "endpoint": url,
                "model": settings.azure_openai_model
            }
            
    except Exception as e:
        return {
            "status": "error", 
            "error": str(e), 
            "endpoint": settings.azure_openai_endpoint,
            "model": settings.azure_openai_model
        }
