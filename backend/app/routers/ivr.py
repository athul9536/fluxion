"""Twilio IVR webhook handlers for the Vani agricultural helpline.

Flow:
  /ivr/voice          greeting + listen for the farmer's question
  /ivr/process        transcription arrives -> LLM answer -> speak it
  /ivr/more           ask whether they have another question

/ivr/voice2 is kept as an alias of /ivr/voice so the Twilio console
webhook does not need to be reconfigured.
"""
from urllib.parse import quote, unquote

from fastapi import APIRouter, Form, Request
from fastapi.responses import Response

from .. import pending
from ..config import settings
from ..logbook import log
from ..services import llm, pincode, sms, stt

router = APIRouter(prefix="/ivr", tags=["ivr"])

# Hints bias the recogniser strongly. Question stems matter as much as crop
# names: without them the model guesses at unfamiliar phrasing.
SPEECH_HINTS = (
    # Question stems
    "what is the best crop, what are the vegetables, what should I do, "
    "how do I treat, how do I control, how much fertilizer, how often, "
    "why are my leaves, why is my crop, when should I plant, when to harvest, "
    "which variety, is it safe to, can I grow, my crop has, my leaves have, "
    # Crops common in Kerala
    "crop, rice, paddy, coconut, banana, pepper, tapioca, cardamom, "
    "rubber, areca nut, ginger, turmeric, vegetables, okra, cowpea, "
    "bitter gourd, snake gourd, pumpkin, cucumber, amaranthus, brinjal, "
    # Problems
    "disease, pest, blight, leaf blight, blast, brown spot, leaf spot, "
    "wilt, root wilt, rot, yellowing, yellow leaves, brown spots, "
    "fungus, insects, beetle, weevil, borer, hopper, caterpillar, aphids, "
    # Treatments and practices
    "fertilizer, urea, potash, phosphorus, zinc, pesticide, fungicide, "
    "neem oil, spray, dosage, organic, compost, "
    "irrigation, drainage, waterlogging, water level, soil, soil test, "
    "seeds, seedlings, spacing, transplanting, harvest, monsoon, season"
)

MAX_ATTEMPTS = 3

# Below this, read the question back before answering rather than risk
# answering something the farmer never asked. Only used with Twilio's
# recogniser, which is the only one that reports confidence.
CONFIDENCE_THRESHOLD = 0.70

# Each poll waits ~2s, so this caps the wait at roughly 20 seconds.
MAX_POLLS = 10

# Safety net for Hindi-ish tokens the recogniser has produced in practice.
# A heuristic, not a translation layer: it only cleans up what we have
# actually observed in the call log.
_HINGLISH_FIXES = {
    "aur": "and",
    "nau": "now",
    "kya": "what",
    "kaise": "how",
    "kab": "when",
    "hai": "is",
    "mera": "my",
    "meri": "my",
    "fasal": "crop",
    "paani": "water",
    "keeda": "pest",
    "patta": "leaf",
    "patte": "leaves",
    # Filler the recogniser inserts that carries no meaning
    "han": "",
    "haan": "",
    "na": "",
    "ho": "",
    "ise": "is",
    "d": "the",
}


def _normalise_transcript(text: str) -> str:
    """Force the transcript to plain English words only.

    Drops any non-ASCII (e.g. Devanagari) and swaps known Hindi tokens for
    their English equivalents so the LLM sees a cleaner question.
    """
    text = text.encode("ascii", "ignore").decode("ascii")

    out = []
    for word in text.split():
        stripped = word.strip(".,!?;:").lower()
        if stripped in _HINGLISH_FIXES:
            replacement = _HINGLISH_FIXES[stripped]
            if replacement:
                out.append(replacement)
        else:
            out.append(word)

    return " ".join(out).strip()


def _twiml(inner: str) -> Response:
    xml = f'<?xml version="1.0" encoding="UTF-8"?><Response>{inner}</Response>'
    return Response(content=xml, media_type="application/xml; charset=utf-8")


def _esc(text: str) -> str:
    return (
        text.replace("&", " and ")
        .replace("<", "")
        .replace(">", "")
        .replace('"', "")
    )


def _say(text: str) -> str:
    return f'<Say voice="Polly.Aditi">{_esc(text)}</Say>'


def _listen(prompt: str, attempt: int, district: str | None = None) -> str:
    """Gather speech. Generous timeouts, retries instead of hanging up.

    speechModel="phone_call" + enhanced="true" selects Twilio's model tuned
    for narrowband telephony audio, which handles accented English far better
    than the default model.

    Only used when Azure STT is switched off.
    """
    base = settings.base_url
    action = (f"{base}/ivr/process?attempt={attempt}"
              f"&amp;loc={quote(district or '')}")
    return (
        f'<Gather input="speech" action="{action}" method="POST" '
        f'timeout="10" speechTimeout="4" language="{settings.speech_language}" '
        f'speechModel="phone_call" enhanced="true" profanityFilter="false" '
        f'hints="{SPEECH_HINTS}" actionOnEmptyResult="true">'
        f"{_say(prompt)}"
        f"</Gather>"
    )


@router.post("/voice")
@router.post("/voice2")
async def voice_entry(request: Request):
    """Entry point. Greet the farmer and confirm their location."""
    form = await request.form()
    log(f"--- CALL START --- from={form.get('From')} sid={form.get('CallSid')}")

    greeting = (
        "Hello! Welcome to Vani, your farming helpline. "
        "To find your area, please enter your six digit pincode on the keypad."
    )
    return _twiml(_ask_pincode(greeting, attempt=1))


def _ask_pincode(prompt: str, attempt: int) -> str:
    """Collect the pincode on the keypad.

    Keypad digits cannot be misheard, which makes this the most reliable
    input in the whole system.
    """
    base = settings.base_url
    action = f"{base}/ivr/pincode?attempt={attempt}"
    return (
        f'<Gather input="dtmf" action="{action}" method="POST" '
        f'numDigits="6" timeout="12" finishOnKey="#" '
        f'actionOnEmptyResult="true">'
        f"{_say(prompt)}"
        f"</Gather>"
        + _say("Sorry, I did not get your pincode. Please call again. Goodbye.")
        + "<Hangup/>"
    )


@router.post("/pincode")
async def collect_pincode(request: Request, Digits: str = Form(default="")):
    """Turn the keyed-in pincode into a district, then invite the question.

    Every branch moves the call forward: a farmer is never dead-ended
    because of a pincode problem.
    """
    attempt = int(request.query_params.get("attempt", 1))
    entered = Digits.strip()
    district = pincode.district(entered)

    log(f"pincode: entered={entered!r} district={district}")

    # Nothing usable and we still have retries left: ask again.
    if not pincode.is_valid(entered) and attempt < 2:
        prompt = (
            "That did not look like a six digit pincode. "
            "Please enter your six digit pincode again."
        )
        return _twiml(_ask_pincode(prompt, attempt=attempt + 1))

    if district:
        opening = (
            f"Thank you. That is {district} district. "
            f"Now please tell me your farming question."
        )
    elif pincode.is_valid(entered):
        # A real pincode, just not one we cover.
        opening = (
            "Thank you. We currently cover Kerala, so I will give you "
            "general farming advice. Please tell me your question now."
        )
    else:
        opening = (
            "No problem, I will give you general farming advice. "
            "Please tell me your question now."
        )

    return _twiml(_ask_question(opening, district))


def _ask_question(prompt: str, district: str | None) -> str:
    """Invite the question, using whichever speech pipeline is configured."""
    if settings.azure_stt_enabled:
        return _record(prompt, district)
    inner = _listen(prompt, attempt=1, district=district)
    inner += _say("Sorry, I could not hear you. Please call again. Goodbye.")
    inner += "<Hangup/>"
    return inner


def _record(prompt: str, district: str | None) -> str:
    """Record the caller so Azure can transcribe it.

    trim-silence keeps the clip tight; timeout ends the recording after a
    few seconds of quiet so the farmer does not have to press anything.
    The district rides along in the action URL, since Twilio is stateless.
    """
    base = settings.base_url
    action = f"{base}/ivr/recorded?loc={quote(district or '')}"
    return (
        _say(prompt)
        + f'<Record action="{action}" method="POST" '
        f'maxLength="30" timeout="4" playBeep="true" '
        f'trim="trim-silence" finishOnKey="#" />'
        + _say("Sorry, I did not hear anything. Please call again. Goodbye.")
        + "<Hangup/>"
    )


@router.post("/recorded")
async def recorded(request: Request,
                   CallSid: str = Form(default=""),
                   RecordingUrl: str = Form(default="")):
    """Recording finished. Transcribe and answer in the background."""
    district = unquote(request.query_params.get("loc", "")) or None
    log(f"recorded: sid={CallSid} district={district} url={RecordingUrl}")

    if not RecordingUrl:
        inner = _say("Sorry, I did not catch that. Please call again. Goodbye.")
        return _twiml(inner + "<Hangup/>")

    def work() -> tuple[str, str]:
        audio = stt.fetch_twilio_recording(RecordingUrl)
        question = stt.transcribe(audio)
        log(f"  azure stt heard: {question!r}")
        if not question:
            return "", ""
        return question, llm.ask(question, district)

    pending.start(CallSid, work)

    base = settings.base_url
    inner = _say("Let me check that for you.")
    inner += (
        f'<Redirect method="POST">{base}/ivr/result?tries=0'
        f'&amp;loc={quote(district or "")}</Redirect>'
    )
    return _twiml(inner)


@router.post("/result")
async def result(request: Request,
                 CallSid: str = Form(default=""),
                 Direction: str = Form(default=""),
                 To: str = Form(default=""),
                 From: str = Form(default="")):
    """Poll for the background answer, keeping the caller informed."""
    tries = int(request.query_params.get("tries", 0))
    base = settings.base_url

    job = pending.result(CallSid)

    if job is None:
        if tries >= MAX_POLLS:
            log(f"result: gave up after {tries} polls for {CallSid}")
            pending.discard(CallSid)
            inner = _say(
                "Sorry, that is taking too long. Please call again. Goodbye."
            )
            return _twiml(inner + "<Hangup/>")

        # Still working: hold briefly, then check again.
        inner = '<Pause length="2"/>'
        if tries == 2:
            inner += _say("Still working on it.")
        loc = request.query_params.get("loc", "")
        inner += (
            f'<Redirect method="POST">{base}/ivr/result?tries={tries + 1}'
            f'&amp;loc={loc}</Redirect>'
        )
        return _twiml(inner)

    pending.discard(CallSid)

    if not job["question"]:
        inner = _say(
            "Sorry, I could not make out your question. "
            "Please call again and speak a little louder. Goodbye."
        )
        return _twiml(inner + "<Hangup/>")

    district = unquote(request.query_params.get("loc", "")) or None
    log(f"result: answering {job['question'][:80]!r}")
    return _twiml(_answer_and_offer_more(
        job["question"],
        precomputed=job["answer"],
        sms_to=_farmer_number(Direction, To, From),
        district=district,
    ))


@router.post("/process")
async def process_speech(request: Request,
                         SpeechResult: str = Form(default=""),
                         Confidence: str = Form(default=""),
                         Direction: str = Form(default=""),
                         To: str = Form(default=""),
                         From: str = Form(default="")):
    """Transcription arrives here. Answer it, or re-prompt if empty."""
    attempt = int(request.query_params.get("attempt", 1))
    district = unquote(request.query_params.get("loc", "")) or None
    raw = SpeechResult.strip()
    question = _normalise_transcript(raw)

    log(f"attempt={attempt} confidence={Confidence} heard={raw!r}")
    if question != raw:
        log(f"  normalised -> {question!r}")

    if not question:
        if attempt < MAX_ATTEMPTS:
            prompt = (
                "I did not catch that. Please say your farming question "
                "clearly after the beep."
            )
            inner = _listen(prompt, attempt=attempt + 1, district=district)
            inner += _say("Sorry, I still could not hear you. Goodbye.")
            inner += "<Hangup/>"
            return _twiml(inner)

        inner = _say(
            "Sorry, I could not hear your question today. "
            "Please call again from a quieter place. Goodbye."
        )
        inner += "<Hangup/>"
        return _twiml(inner)

    # Shaky transcription: confirm before answering. Answering the wrong
    # question confidently is worse than taking one extra turn.
    if _low_confidence(Confidence) and attempt < MAX_ATTEMPTS:
        log("  low confidence, confirming with caller")
        return _twiml(_confirm_question(question, attempt, district))

    return _twiml(_answer_and_offer_more(
        question,
        sms_to=_farmer_number(Direction, To, From),
        district=district,
    ))


def _farmer_number(direction: str, to: str, from_: str) -> str:
    """Work out the farmer's number.

    On an outbound call Twilio dials the farmer, so they are `To`.
    On an inbound call the farmer is the caller, so they are `From`.
    """
    if direction.startswith("outbound"):
        return to
    return from_


def _low_confidence(raw: str) -> bool:
    try:
        return float(raw) < CONFIDENCE_THRESHOLD
    except (TypeError, ValueError):
        return False


def _confirm_question(question: str, attempt: int,
                      district: str | None = None) -> str:
    """Read the question back and ask the caller to confirm."""
    base = settings.base_url
    # &amp; because this URL sits inside an XML attribute
    action = (f"{base}/ivr/verify?q={quote(question)}&amp;attempt={attempt}"
              f"&amp;loc={quote(district or '')}")
    prompt = f"I heard: {question}. Is that correct? Say yes or no."
    return (
        f'<Gather input="speech dtmf" action="{action}" method="POST" '
        f'timeout="7" speechTimeout="3" numDigits="1" '
        f'language="{settings.speech_language}" '
        f'speechModel="phone_call" enhanced="true" '
        f'hints="yes, no, correct, wrong" actionOnEmptyResult="true">'
        f"{_say(prompt)}"
        f"</Gather>"
        + _say("Sorry, I could not hear you. Goodbye.")
        + "<Hangup/>"
    )


@router.post("/verify")
async def verify_question(request: Request,
                          SpeechResult: str = Form(default=""),
                          Digits: str = Form(default=""),
                          Direction: str = Form(default=""),
                          To: str = Form(default=""),
                          From: str = Form(default="")):
    """Caller confirms or rejects what we thought we heard."""
    question = unquote(request.query_params.get("q", ""))
    attempt = int(request.query_params.get("attempt", 1))
    district = unquote(request.query_params.get("loc", "")) or None
    said = SpeechResult.lower().strip()

    log(f"verify: speech={said!r} digits={Digits!r} for {question!r}")

    rejected = Digits == "2" or any(
        w in said for w in ("no", "nope", "wrong", "not right", "incorrect")
    )

    if rejected:
        inner = _listen("Sorry about that. Please say your question again.",
                        attempt=attempt + 1, district=district)
        inner += _say("Sorry, I could not hear you. Goodbye.")
        inner += "<Hangup/>"
        return _twiml(inner)

    # Treat yes, silence, or anything unclear as confirmation: the caller
    # already waited once, do not make them wait again.
    return _twiml(_answer_and_offer_more(
        question,
        sms_to=_farmer_number(Direction, To, From),
        district=district,
    ))


def _answer_and_offer_more(question: str,
                           precomputed: str | None = None,
                           sms_to: str = "",
                           district: str | None = None) -> str:
    """Speak the answer, then offer another question.

    `precomputed` lets the background worker's answer be reused instead of
    calling the LLM twice. `sms_to` also texts the answer to the farmer.
    """
    if precomputed:
        answer = precomputed
        log(f"answer={answer[:160]!r}")
    else:
        try:
            answer = llm.ask(question, district)
            log(f"answer={answer[:160]!r}")
        except Exception as e:
            log(f"LLM FAILED: {e}")
            answer = (
                "I am having trouble answering right now. "
                "Please try again shortly, or contact your local Krishi Bhavan."
            )

    if not answer.strip():
        # Belt and braces: silence on the line is the worst outcome.
        log("answer was empty at router level, substituting fallback")
        answer = (
            "Sorry, I could not work out an answer for that. "
            "Please try asking in a different way."
        )

    # Text the same answer so the farmer has a record of it.
    sms.send_async(sms_to, answer)

    base = settings.base_url
    inner = _say(answer)
    inner += (
        f'<Gather input="speech dtmf" '
        f'action="{base}/ivr/more?loc={quote(district or "")}" method="POST" '
        f'timeout="6" speechTimeout="2" numDigits="1" '
        f'language="{settings.speech_language}" '
        f'speechModel="phone_call" enhanced="true" '
        f'hints="yes, no, another question" actionOnEmptyResult="true">'
        f'{_say("Do you have another question? Say yes or no.")}'
        f"</Gather>"
    )
    inner += _say("Thank you for calling Vani. Goodbye.")
    inner += "<Hangup/>"
    return inner


@router.post("/more")
async def more_questions(request: Request,
                         SpeechResult: str = Form(default=""),
                         Digits: str = Form(default="")):
    """Loop back for another question, or sign off."""
    said = SpeechResult.lower().strip()
    district = unquote(request.query_params.get("loc", "")) or None
    log(f"more: speech={said!r} digits={Digits!r} district={district}")

    wants_more = Digits == "1" or any(
        w in said for w in ("yes", "yeah", "yep", "another", "one more")
    )

    if wants_more:
        # Location carries over, so we never re-ask for the pincode.
        return _twiml(_ask_question("Please tell me your next question.",
                                    district))

    inner = _say("Thank you for calling Vani. Have a good harvest. Goodbye.")
    inner += "<Hangup/>"
    return _twiml(inner)


@router.get("/test")
async def test_llm(question: str = "How do I treat rice leaf blight?"):
    """Check the LLM path without placing a call."""
    from ..services.llm import test_connection

    conn = test_connection()
    if conn["status"] == "error":
        return conn
    return {"question": question, "answer": llm.ask(question), "status": "ok"}


@router.get("/log")
async def read_log(lines: int = 60):
    """Return the tail of the call log for quick debugging."""
    from ..logbook import LOG_FILE

    if not LOG_FILE.exists():
        return {"log": [], "note": "no calls logged yet"}
    content = LOG_FILE.read_text(encoding="utf-8").splitlines()
    return {"log": content[-lines:]}
