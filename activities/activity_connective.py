"""Connective Activity: Quiz and Feedback Generators (Generic prompts - to be customized)."""

from typing import Dict, List
from core.openrouter_client import OpenRouterClient
import streamlit as st


class QuizGeneratorConnective:
    """Quiz generator for Connective annotations with language detection."""

    def __init__(self, model_name="mistralai/mistral-7b-instruct"):
        """Initialize the Connective quiz generator."""
        self.model_name = model_name
        self.openrouter_client = OpenRouterClient()

        if not self.openrouter_client.is_available():
            st.warning("OpenRouter server is not available. Make sure you have your API key configured.")

    def detect_text_language(self, text: str) -> str:
        """Detect the predominant language of the input text."""
        italian_indicators = ['il', 'la', 'di', 'che', 'è', 'sono', 'della', 'del', 'una', 'un']
        english_indicators = ['the', 'is', 'are', 'was', 'were', 'of', 'and', 'to', 'in', 'a']
        
        text_lower = text.lower()
        italian_score = sum(text_lower.count(f' {word} ') for word in italian_indicators)
        english_score = sum(text_lower.count(f' {word} ') for word in english_indicators)
        
        return 'en' if english_score > italian_score else 'it'

    def _get_language_instructions(self, detected_lang: str) -> dict:
        """Get language-specific instructions for Connective quiz generation."""
        if detected_lang == 'en':
            return {
                "task_instruction": "Create a comprehension quiz in ENGLISH that assesses understanding of connectives and textual cohesion.",
                "language_rules": """LANGUAGE RULE:
- Generate the quiz in ENGLISH (matching the input text language).
- Keep structural labels in Italian: "[Scelta Multipla]", "[Risposta Aperta]", "✅ Risposta corretta:", "✅ Risposta:"
- Everything else (questions, options) must be in ENGLISH."""
            }
        else:
            return {
                "task_instruction": "Crea un quiz di comprensione in italiano che valuti la comprensione dei connettivi e della coesione testuale.",
                "language_rules": """Ruolo lingua:
- Il quiz deve essere generato in italiano (lingua del testo).
- Mantieni le etichette strutturali: "[Scelta Multipla]", "[Risposta Aperta]", "✅ Risposta corretta:", "✅ Risposta:"
- Tutto il resto deve essere nella lingua del testo."""
            }

    def generate_quiz(self, text: str, annotations: Dict[str, List[str]]) -> str:
        """Generate a Connective quiz (GENERIC - to be customized)."""
        if not self.openrouter_client.is_available():
            return "OpenRouter API non disponibile."

        detected_lang = self.detect_text_language(text)
        lang_instructions = self._get_language_instructions(detected_lang)
        
        annotation_examples = "\n".join(
            [f"- {tag}: {', '.join(items)}" for tag, items in annotations.items()]
        )

        prompt = f"""Sei un assistente educativo specializzato nell'analisi di connettivi testuali.

TESTO:
{text}

ANNOTAZIONI CONNETTIVI:
{annotation_examples}

ISTRUZIONI:
{lang_instructions["task_instruction"]} Il quiz deve includere:

1. **2 domande a scelta multipla** (4 opzioni ciascuna):
   - Una sull'identificazione della funzione dei connettivi
   - Una sull'effetto dei connettivi sulla struttura del testo

2. **1 domanda a risposta aperta** sulla riscrittura con connettivi diversi

Ogni domanda deve essere basata sulle annotazioni e testare la comprensione dei connettivi.

FORMATO RICHIESTO:
- Numero e tipo: "1. [Scelta Multipla]" o "3. [Risposta Aperta]"
- Per scelta multipla:
    numero. [Scelta Multipla] domanda:
        - A) opzione A
        - B) opzione B
        - C) opzione C
        - D) opzione D
        
        ✅ Risposta corretta: lettera

- Per risposta aperta:
    numero. [Risposta Aperta] domanda:
    ✅ Risposta: risposta corretta

NON aggiungere spiegazioni o commenti extra.

{lang_instructions["language_rules"]}
"""

        return self.openrouter_client.generate(
            model=self.model_name,
            prompt=prompt,
            temperature=0.7,
            max_tokens=2048
        )


class FeedbackGeneratorConnective:
    """Feedback generator for Connective activity (GENERIC - to be customized)."""

    def __init__(self, model_name="mistralai/mistral-7b-instruct"):
        """Initialize the Connective feedback generator."""
        self.model_name = model_name
        self.openrouter_client = OpenRouterClient()

    def generate_feedback(
        self, 
        question: str, 
        correct_answer: str, 
        student_answer: str,
        annotations: Dict[str, List[str]] = None,
        original_text: str = None,
        question_type: str = "open_ended",
        options: List[Dict[str, str]] = None
    ) -> str:
        """Generate feedback (GENERIC - uses same structure as 5W for now)."""
        if not self.openrouter_client.is_available():
            return "OpenRouter API non disponibile."

        if question_type == "multiple_choice":
            return self._generate_mc_feedback(question, correct_answer, student_answer, options, annotations, original_text)
        else:
            return self._generate_oe_feedback(question, correct_answer, student_answer, annotations, original_text)

    def _generate_oe_feedback(self, question: str, correct_answer: str, student_answer: str, 
                               annotations: Dict[str, List[str]] = None, original_text: str = None) -> str:
        """Generic open-ended feedback for Connective."""
        formatted_annotations = self._format_annotations(annotations)
        text_context = original_text[:500] + "..." if original_text and len(original_text) > 500 else original_text or ""
        
        prompt = f"""Sei un tutor educativo. Fornisci feedback sulla risposta dello studente basandoti sul testo e le annotazioni (Connective).

DOMANDA: {question}
RISPOSTA ATTESA: {correct_answer}
RISPOSTA STUDENTE: {student_answer}

ANNOTAZIONI (Connective):
{formatted_annotations}

CONTESTO: {text_context}

Fornisci feedback strutturato in 3 sezioni brevi (~120 parole totali):
**☀️ ASPETTI POSITIVI:** [elementi corretti]
**🎯 SUGGERIMENTO:** [come migliorare, riferimento alle annotazioni]
**🤔 DOMANDA METACOGNITIVA:** [domanda per riflettere]

FEEDBACK:"""

        return self.openrouter_client.generate(model=self.model_name, prompt=prompt, temperature=0.7, max_tokens=1024)

    def _generate_mc_feedback(self, question: str, correct_answer: str, student_answer: str,
                               options: List[Dict[str, str]] = None, annotations: Dict[str, List[str]] = None, 
                               original_text: str = None) -> str:
        """Generic multiple choice feedback for Connective."""
        formatted_options = "\n".join([f"{opt['letter']}) {opt['text']}" for opt in options]) if options else ""
        formatted_annotations = self._format_annotations(annotations)
        text_context = original_text[:500] + "..." if original_text and len(original_text) > 500 else original_text or ""
        
        correct_text = next((opt["text"] for opt in options if opt["letter"] == correct_answer), "") if options else ""
        student_text = next((opt["text"] for opt in options if opt["letter"] == student_answer), "") if options else ""
        
        prompt = f"""Feedback per scelta multipla (Connective).

DOMANDA: {question}
OPZIONI: {formatted_options}
CORRETTA: {correct_answer}) {correct_text}
STUDENTE: {student_answer}) {student_text}

ANNOTAZIONI: {formatted_annotations}
CONTESTO: {text_context}

Se CORRETTA: ✅ Conferma + riferimento.
Se SBAGLIATA: 3 sezioni (☀️ Riconoscimento, 🎯 Chiarimento, 📍 Riferimento).

FEEDBACK:"""

        return self.openrouter_client.generate(model=self.model_name, prompt=prompt, temperature=0.3, max_tokens=1024)

    def _format_annotations(self, annotations: Dict[str, List[str]]) -> str:
        """Format annotations."""
        if not annotations:
            return "Nessuna annotazione"
        formatted = []
        for tag, items in annotations.items():
            limited_items = items[:3] if len(items) > 3 else items
            item_text = ", ".join(limited_items)
            if len(items) > 3:
                item_text += f" (e altri {len(items) - 3})"
            formatted.append(f"- {tag}: {item_text}")
        return "\n".join(formatted)


