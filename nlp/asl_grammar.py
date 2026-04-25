# ASL grammar differs significantly from English.
# Topic-comment structure: "I am hungry" → "hungry I"
# WH-questions move to the end: "what is your name" → "your name what"

PHRASE_MAP: dict[str, list[str]] = {
    "how are you": ["you", "how"],
    "what is your name": ["your", "name", "what"],
    "nice to meet you": ["meet", "you", "happy"],
    "thank you very much": ["thank", "you"],
    "where is the bathroom": ["bathroom", "where"],
    "i love you": ["love", "you"],
    "good morning": ["morning", "good"],
    "good night": ["night", "good"],
    "i don't understand": ["understand", "not"],
    "please repeat": ["repeat", "please"],
    "speak slowly": ["slow", "please"],
}

WH_WORDS: set[str] = {"what", "where", "when", "why", "who", "how", "which"}


def reorder_for_asl(keywords: list[str]) -> list[str]:
    """
    Apply basic ASL topic-comment reordering.
    WH-question words move to the end.
    """
    wh = [w for w in keywords if w in WH_WORDS]
    rest = [w for w in keywords if w not in WH_WORDS]
    return rest + wh
