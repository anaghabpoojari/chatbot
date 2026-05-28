import json
import random
import spacy
from groq import Groq 
from dotenv import load_dotenv
import os 
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from memory import ConversationMemory

nlp = spacy.load("en_core_web_sm")
STOP_WORDS = set(stopwords.words("english"))
load_dotenv()

class Chatbot:
    def __init__(self, intents_path="intents.json"):
        with open(intents_path) as f:
            self.intents = json.load(f)["intents"]
        self.memory = ConversationMemory(max_history=20)

    # ── NLP: tokenize + lemmatize + remove stopwords ──────────────────────
    def preprocess(self, text: str) -> list[str]:
        doc = nlp(text.lower())
        tokens = [
            token.lemma_ for token in doc
            if token.is_alpha and token.lemma_ not in STOP_WORDS
        ]
        return tokens

    # ── Intent detection via token overlap scoring ─────────────────────────
    from difflib import SequenceMatcher

    def detect_intent(self, text: str) -> tuple[str, float]:
        tokens = set(self.preprocess(text))
        best_intent, best_score = "unknown", 0.0
        text_lower = text.lower()

        for intent in self.intents:
            for pattern in intent["patterns"]:
                # 1. Exact substring match → high confidence
                if pattern.lower() in text_lower:
                    return intent["tag"], 1.0

                # 2. Token overlap score
                pattern_tokens = set(self.preprocess(pattern))
                if pattern_tokens:
                    overlap = tokens & pattern_tokens
                    score = len(overlap) / len(pattern_tokens)
                else:
                    score = 0.0

                # 3. Fuzzy string similarity as a bonus
                fuzzy = self.SequenceMatcher(None, text_lower, pattern.lower()).ratio()
                combined = max(score, fuzzy * 0.8)   # fuzzy weighted slightly lower

                if combined > best_score:
                    best_score = combined
                    best_intent = intent["tag"]

        return best_intent, best_score

    # Entity extraction via spaCy NER 
    def extract_entities(self, text: str) -> dict:
        doc = nlp(text)
        return {ent.label_: ent.text for ent in doc.ents}

    # Generate a response
    def respond(self, user_input: str) -> dict:
        intent_tag, confidence = self.detect_intent(user_input)
        entities = self.extract_entities(user_input)

        # Save user name if detected
        if "PERSON" in entities:
            self.memory.set_context("user_name", entities["PERSON"])

        # Pick response
        response_text = self._get_response(intent_tag, confidence, user_input)

        # Personalise if we know the name
        name = self.memory.get_context("user_name")
        if name and random.random() > 0.6:
            response_text = f"{name}, {response_text[0].lower()}{response_text[1:]}"

        # Store in memory
        self.memory.add("user", user_input, intent_tag)
        self.memory.add("bot", response_text, intent_tag)

        return {
            "response": response_text,
            "intent": intent_tag,
            "confidence": round(confidence, 2),
            "entities": entities,
        }

    def _get_response(self, tag, confidence, original_input):
        # Low confidence → fallback
        if confidence < 0.25:
            return self._api_fallback(original_input)
        for intent in self.intents:
            if intent["tag"] == tag:
                return random.choice(intent["responses"])
        return self._api_fallback(original_input)
        
    def _api_fallback(self, user_input: str) -> str:
        client = Groq(api_key=os.environ["GROQ_API_KEY"])
        recent = self._build_history()
        try:
            resp = client.chat.completions.create(
                model="llama-3.1-8b-instant",  
                messages=[
                    {"role": "system", "content": "You are BotNLP. Reply in 1-2 sentences."},
                    *recent,
                    {"role": "user", "content": user_input}
                ],
                max_tokens=150
            )
            return resp.choices[0].message.content
        except Exception:
            return "I'm not sure — could you rephrase?"