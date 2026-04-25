import spacy
from nlp.stopwords import STOPWORDS
from nlp.asl_grammar import PHRASE_MAP, reorder_for_asl
from utils.logger import logger

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    raise RuntimeError(
        "spaCy model not found. Run: python -m spacy download en_core_web_sm"
    )


class TextProcessor:
    """
    Converts raw transcript text into a clean list of ASL keywords.

    Pipeline:
    1. Check phrase map for whole-phrase matches
    2. Tokenize with spaCy
    3. Remove stopwords
    4. Lemmatize (run → run, running → run)
    5. Reorder for ASL grammar
    """

    def process(self, transcript: str) -> list[str]:
        if not transcript:
            return []

        text = transcript.lower().strip()
        logger.debug("Processing transcript: '{}'", text)

        # Step 1: check for known phrase mappings
        if text in PHRASE_MAP:
            result = PHRASE_MAP[text]
            logger.debug("Phrase map hit: {} → {}", text, result)
            return result

        # Step 2–4: tokenize, filter, lemmatize
        doc = nlp(text)
        keywords: list[str] = []
        for token in doc:
            if token.is_punct or token.is_space:
                continue
            lemma = token.lemma_.lower()
            if lemma in STOPWORDS:
                continue
            keywords.append(lemma)

        # Step 5: ASL reorder
        result = reorder_for_asl(keywords)
        logger.debug("Keywords: {}", result)
        return result
