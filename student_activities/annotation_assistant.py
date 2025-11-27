"""AI-guided annotation assistance for students."""

from typing import Dict, List, Optional
from core.openrouter_client import OpenRouterClient


class AnnotationAssistant:
    """AI assistant to guide students through text annotation process."""
    
    def __init__(self, model_name: str = "openai/gpt-4o-mini"):
        """
        Initialize the annotation assistant.
        
        Args:
            model_name: OpenRouter model to use for AI assistance
        """
        self.model_name = model_name
        self.openrouter_client = OpenRouterClient()
        
        # Tag type descriptions for different annotation types
        self.tag_descriptions = {
            "5W": {
                "Who": "Identifies people, characters, or entities involved",
                "What": "Describes events, actions, or phenomena",
                "When": "Indicates time references or temporal information",
                "Where": "Specifies locations or spatial references",
                "Why": "Explains reasons, causes, or motivations"
            },
            "Argument": {
                "Thesis": "The main claim or position of the author",
                "Antithesis": "The opposite position or contradicting claim",
                "Argument": "Evidence, reasoning, or support for the thesis",
                "Counterargument": "Arguments against the thesis or that refute objections",
                "Conclusion": "Summary or final statement reinforcing the thesis"
            },
            "Thesis": {
                "Thesis": "The main claim or central argument of the text"
            },
            "Connective": {
                "Connective": "Words or phrases that link ideas (e.g., however, therefore, additionally)"
            }
        }
    
    def get_hint(self, text: str, tag_type: str, specific_tag: str, 
                 help_level: str = "medium", language: str = "it") -> str:
        """
        Generate a helpful hint for finding a specific annotation tag.
        
        Args:
            text: The text to annotate
            tag_type: Type category (5W, Argument, etc.)
            specific_tag: Specific tag to find (e.g., "Thesis", "Who")
            help_level: How much help to give ("low", "medium", "high")
            language: Language for hints ("it" or "en")
        
        Returns:
            AI-generated hint
        """
        if not self.openrouter_client.is_available():
            return "OpenRouter API non disponibile."
        
        tag_description = self.tag_descriptions.get(tag_type, {}).get(specific_tag, "")
        
        # Determine hint intensity based on help level
        hint_instructions = {
            "low": "Provide a subtle hint without revealing the answer. Ask a guiding question.",
            "medium": "Provide a clear hint that narrows down where to look. Be specific about the paragraph or area.",
            "high": "Provide a strong hint that almost reveals the answer. Highlight specific sentences to examine."
        }
        
        lang_instruction = "Rispondi in ITALIANO." if language == "it" else "Respond in ENGLISH."
        
        prompt = f"""Sei un tutor educativo AI che aiuta uno studente a imparare l'annotazione di testi.

Lo studente deve identificare: **{specific_tag}**
Descrizione: {tag_description}

TESTO:
{text[:1500]}...

Livello di aiuto: {help_level}
Istruzione: {hint_instructions[help_level]}

{lang_instruction}

Fornisci un suggerimento utile (2-3 frasi) che guidi lo studente senza dare direttamente la risposta.
Usa il metodo socratico: fai domande che stimolino il ragionamento.

SUGGERIMENTO:"""

        return self.openrouter_client.generate(
            model=self.model_name,
            prompt=prompt,
            temperature=0.7,
            max_tokens=200
        )
    
    def validate_annotation(self, selected_text: str, tag_type: str, 
                           specific_tag: str, full_text: str,
                           student_reasoning: Optional[str] = None,
                           language: str = "it") -> Dict[str, any]:
        """
        Validate a student's annotation and provide feedback.
        
        Args:
            selected_text: The text segment the student annotated
            tag_type: Type category (5W, Argument, etc.)
            specific_tag: The tag the student assigned
            full_text: The complete text for context
            student_reasoning: Optional explanation from student
            language: Language for feedback
        
        Returns:
            Dictionary with validation result and feedback
        """
        if not self.openrouter_client.is_available():
            return {
                "is_correct": None,
                "feedback": "OpenRouter API non disponibile.",
                "confidence": 0
            }
        
        tag_description = self.tag_descriptions.get(tag_type, {}).get(specific_tag, "")
        lang_instruction = "Rispondi in ITALIANO." if language == "it" else "Respond in ENGLISH."
        
        reasoning_part = f"\n\nRAGIONAMENTO DELLO STUDENTE: {student_reasoning}" if student_reasoning else ""
        
        prompt = f"""Sei un tutor educativo AI. Uno studente ha annotato un segmento di testo.

TAG ASSEGNATO: **{specific_tag}**
Descrizione del tag: {tag_description}

TESTO SELEZIONATO DALLO STUDENTE:
"{selected_text}"{reasoning_part}

CONTESTO (testo completo):
{full_text[:1000]}...

{lang_instruction}

Valuta se l'annotazione è corretta e fornisci feedback costruttivo in questo formato:

CORRETTO: [Sì/No/Parzialmente]
SPIEGAZIONE: [1-2 frasi che spiegano perché l'annotazione è corretta o errata]
SUGGERIMENTO: [Se errato o parziale, un suggerimento per migliorare]

Sii incoraggiante e didattico. Se l'annotazione è parzialmente corretta, riconoscilo.

VALUTAZIONE:"""

        response = self.openrouter_client.generate(
            model=self.model_name,
            prompt=prompt,
            temperature=0.3,
            max_tokens=300
        )
        
        # Parse response to extract correctness
        is_correct = None
        if "CORRETTO: Sì" in response or "CORRECT: Yes" in response:
            is_correct = True
        elif "CORRETTO: No" in response or "CORRECT: No" in response:
            is_correct = False
        elif "Parzialmente" in response or "Partially" in response:
            is_correct = "partial"
        
        return {
            "is_correct": is_correct,
            "feedback": response,
            "confidence": 0.8 if is_correct == True else 0.5
        }
    
    def get_example(self, tag_type: str, specific_tag: str, language: str = "it") -> str:
        """
        Provide an example of a correctly annotated element.
        
        Args:
            tag_type: Type category (5W, Argument, etc.)
            specific_tag: Specific tag to show example for
            language: Language for example
        
        Returns:
            Example text with annotation
        """
        if not self.openrouter_client.is_available():
            return "OpenRouter API non disponibile."
        
        tag_description = self.tag_descriptions.get(tag_type, {}).get(specific_tag, "")
        lang_instruction = "Rispondi in ITALIANO." if language == "it" else "Respond in ENGLISH."
        
        prompt = f"""Sei un tutor educativo AI.

Fornisci un esempio BREVE (2-3 frasi) di un testo che contenga: **{specific_tag}**
Descrizione: {tag_description}

{lang_instruction}

Formato:
ESEMPIO DI TESTO:
[Testo esempio]

ANNOTAZIONE:
[Parte da annotare evidenziata] → {specific_tag}

SPIEGAZIONE:
[Perché questo è un {specific_tag}]

ESEMPIO:"""

        return self.openrouter_client.generate(
            model=self.model_name,
            prompt=prompt,
            temperature=0.7,
            max_tokens=250
        )
    
    def generate_metacognitive_question(self, selected_text: str, specific_tag: str, 
                                       language: str = "it") -> str:
        """
        Generate a metacognitive question to prompt student reflection.
        
        Args:
            selected_text: The annotated text
            specific_tag: The tag assigned
            language: Language for question
        
        Returns:
            Thought-provoking question
        """
        if not self.openrouter_client.is_available():
            return "Perché hai scelto questo segmento come " + specific_tag + "?"
        
        lang_instruction = "Rispondi in ITALIANO." if language == "it" else "Respond in ENGLISH."
        
        prompt = f"""Sei un tutor educativo AI che usa il metodo socratico.

Lo studente ha annotato questo testo come: **{specific_tag}**
Testo: "{selected_text}"

{lang_instruction}

Genera UNA domanda metacognitiva (1 frase) che stimoli lo studente a riflettere sulla sua scelta.
La domanda dovrebbe aiutare lo studente a verificare il suo ragionamento.

Esempi:
- "Quali elementi di questo segmento ti hanno fatto pensare che sia una tesi?"
- "Come si collega questo argomento alla tesi principale?"
- "Perché questo non potrebbe essere un semplice esempio?"

DOMANDA:"""

        return self.openrouter_client.generate(
            model=self.model_name,
            prompt=prompt,
            temperature=0.8,
            max_tokens=100
        )

