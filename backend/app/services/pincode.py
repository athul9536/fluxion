"""Resolve a Kerala PIN code to its district.

Static lookup, so there is no network call or LLM cost at call time.
Districts are derived from the 3-digit postal prefix, which is accurate for
13 of Kerala's 14 districts. Wayanad shares prefixes with Kozhikode and
Kannur, so its main towns are listed explicitly.
"""

KERALA_MIN = 670000
KERALA_MAX = 695999

# 3-digit prefix -> district
PREFIX_DISTRICT = {
    "670": "Kannur",
    "671": "Kasaragod",
    "673": "Kozhikode",
    "676": "Malappuram",
    "678": "Palakkad",
    "679": "Malappuram",
    "680": "Thrissur",
    "681": "Thrissur",
    "682": "Ernakulam",
    "683": "Ernakulam",
    "685": "Idukki",
    "686": "Kottayam",
    "688": "Alappuzha",
    "689": "Pathanamthitta",
    "690": "Alappuzha",
    "691": "Kollam",
    "695": "Thiruvananthapuram",
}

# Wayanad has no prefix of its own; these are its main post towns.
EXACT_DISTRICT = {
    "670644": "Wayanad",   # Mananthavady area
    "670645": "Wayanad",
    "670646": "Wayanad",
    "673121": "Wayanad",   # Kalpetta
    "673122": "Wayanad",
    "673575": "Wayanad",
    "673576": "Wayanad",   # Vythiri
    "673577": "Wayanad",
    "673579": "Wayanad",
    "673591": "Wayanad",
    "673592": "Wayanad",   # Sulthan Bathery
    "673593": "Wayanad",
    "673595": "Wayanad",
    "673596": "Wayanad",
}


def is_valid(pincode: str) -> bool:
    """Six digits, nothing else."""
    return len(pincode) == 6 and pincode.isdigit()


def is_kerala(pincode: str) -> bool:
    return is_valid(pincode) and KERALA_MIN <= int(pincode) <= KERALA_MAX


def district(pincode: str) -> str | None:
    """District name, or None if we cannot place the PIN code."""
    if not is_kerala(pincode):
        return None
    if pincode in EXACT_DISTRICT:
        return EXACT_DISTRICT[pincode]
    return PREFIX_DISTRICT.get(pincode[:3])


def spoken_digits(pincode: str) -> str:
    """Read digits back one at a time so TTS does not say 'six hundred'."""
    return " ".join(pincode)
