"""5W Activity: Quiz and Feedback Generators with enhanced prompts."""

from typing import Dict, List
from core.openrouter_client import OpenRouterClient
import streamlit as st


class QuizGenerator5W:
    """Quiz generator specifically for 5W annotations with language detection."""

    def __init__(self, model_name="mistralai/mistral-7b-instruct"):
        """Initialize the 5W quiz generator."""
        self.model_name = model_name
        self.openrouter_client = OpenRouterClient()

        if not self.openrouter_client.is_available():
            st.warning(
                """
            OpenRouter server is not available. Make sure you have your API key configured.
            
            To get an OpenRouter API key, visit: https://openrouter.ai/
            
            After getting your key, set it as an environment variable:
            ```
            OPENROUTER_API_KEY=your_key_here
            ```
            """
            )

    def detect_text_language(self, text: str) -> str:
        """
        Detect the predominant language of the input text.
        
        Args:
            text: The input text to analyze
            
        Returns:
            'en' for English, 'it' for Italian
        """
        # Common indicator words for each language
        italian_indicators = ['il', 'la', 'di', 'che', 'è', 'sono', 'della', 'del', 'una', 'un']
        english_indicators = ['the', 'is', 'are', 'was', 'were', 'of', 'and', 'to', 'in', 'a']
        
        text_lower = text.lower()
        
        # Count occurrences of indicator words
        italian_score = sum(text_lower.count(f' {word} ') for word in italian_indicators)
        english_score = sum(text_lower.count(f' {word} ') for word in english_indicators)
        
        # Return detected language
        return 'en' if english_score > italian_score else 'it'

    def _get_language_instructions(self, detected_lang: str) -> dict:
        """
        Get language-specific instructions for 5W quiz generation.
        
        Args:
            detected_lang: Detected language code ('en' or 'it')
            
        Returns:
            Dictionary with 'task_instruction' and 'language_rules'
        """
        if detected_lang == 'en':
            return {
                "task_instruction": "Create a comprehension quiz in ENGLISH that assesses understanding of the 5Ws in the text.",
                "language_rules": """LANGUAGE RULE (MANDATORY):
- The input text is in ENGLISH, so the quiz MUST be generated in ENGLISH.
- DO NOT translate the text content.
- Keep proper nouns and citations exactly as in the text.
- Exception: Keep these Italian structural labels:
  * "[Scelta Multipla]" and "[Risposta Aperta]"
  * "✅ Risposta corretta:" and "✅ Risposta:"
  * Markers A) B) C) D)
  Everything else (questions, options, explanations) must be in ENGLISH."""
            }
        else:  # Italian
            return {
                "task_instruction": "Crea un quiz di comprensione in italiano che valuti la comprensione delle 5W nel testo.",
                "language_rules": """Ruolo lingua (OBBLIGATORIO):
- Il testo è in italiano, quindi il quiz deve essere generato in italiano.
- NON tradurre i contenuti del testo: il quiz generato deve essere sempre nella lingua originale del testo.
- NON mescolare lingue all'interno dello stesso quiz.
- Conserva i nomi propri e le citazioni esattamente come nel testo.
- Mantieni SEMPRE in italiano le etichette di struttura necessarie al sistema:
  * "[Scelta Multipla]" e "[Risposta Aperta]"
  * "✅ Risposta corretta:" e "✅ Risposta:"
  * I marcatori A) B) C) D)
  Tutto il resto (testo delle domande, opzioni, eventuali frasi) deve essere nella lingua del testo."""
            }

    def generate_quiz(self, text: str, annotations: Dict[str, List[str]]) -> str:
        """
        Generate a 5W quiz based on the provided text and annotations.

        Args:
            text: The text to create a quiz for
            annotations: Dictionary with tag categories as keys and lists of text snippets

        Returns:
            Generated quiz as a string
        """
        if not self.openrouter_client.is_available():
            return "OpenRouter API non disponibile. Controlla la configurazione della tua API key."

        # Detect language
        detected_lang = self.detect_text_language(text)
        
        # Get language-specific instructions
        lang_instructions = self._get_language_instructions(detected_lang)
        
        annotation_examples = "\n".join(
            [f"- {tag}: {', '.join(items)}" for tag, items in annotations.items()]
        )

        prompt = f"""Sei un assistente educativo specializzato nella creazione di quiz basati sulle 5W (Who, What, When, Where, Why).

TESTO:
{text}

ANNOTAZIONI 5W:
{annotation_examples}

ISTRUZIONI:
{lang_instructions["task_instruction"]} Il quiz deve includere:

1. **2 domande a scelta multipla** (4 opzioni ciascuna):
   - Una domanda su CHI (Who) o COSA (What)
   - Una domanda su QUANDO (When), DOVE (Where) o PERCHÉ (Why)

2. **1 domanda a risposta aperta** che richieda di collegare più elementi delle 5W

Ogni domanda deve:
- Essere basata sulle annotazioni fornite. 
- Testare la comprensione specifica degli elementi 5W
- Avere risposte chiare e verificabili dal testo

  ⚠️ Le domande devono essere originali e dinamiche, ma sempre adattate al contenuto specifico del testo e al tipo di annotazioni fornite.


FORMATO RICHIESTO:
- Numero e tipo di domanda (es. "1. [Scelta Multipla]" o "2. [Risposta Aperta]")
- Testo della domanda 
- Opzioni (solo per le 2 domande a scelta multipla) - presentate una per riga, come nel formato seguente:


    numero domanda. [Scelta Multipla] testo della domanda:
        - A) opzione A
        - B) opzione B
        - C) opzione C
        - D) opzione D

        ✅ Risposta corretta: lettera della risposta corretta

        ⚠️ La risposta corretta deve comparire sempre dopo le opzioni ed essere a capo (come evidenziato sopra), e non in mezzo al quiz. La lettera indicata (A, B, C, D) deve corrispondere alla risposta realmente esatta, e non essere scelta arbitrariamente.
        
        ⚠️ È FONDAMENTALE che tu segua ESATTAMENTE questo formato per le opzioni delle domande a scelta multipla, con i trattini e gli spazi come indicato sopra.


- Per domande a risposta aperta, dopo il testo della domanda, deve seguire la risposta corretta con il seguente formato:

    numero domanda. [Risposta Aperta] testo della domanda:
    ✅ Risposta: testo della risposta corretta



NON usare un modello fisso di domande. Crea domande originali che si adattano specificamente al testo fornito.
NON aggiungere spiegazioni o commenti extra al quiz.

{lang_instructions["language_rules"]}
"""

        return self.openrouter_client.generate(
            model=self.model_name,
            prompt=prompt,
            temperature=0.7,
            max_tokens=2048
        )


class FeedbackGenerator5W:
    """Feedback generator for 5W activity with enhanced annotation-aware prompts."""

    def __init__(self, model_name="mistralai/mistral-7b-instruct"):
        """Initialize the 5W feedback generator."""
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
        """
        Generate feedback for a student's answer.

        Args:
            question: The quiz question
            correct_answer: The correct answer
            student_answer: The student's answer
            annotations: Dictionary with tag categories as keys and lists of text snippets
            original_text: The original text used for quiz generation
            question_type: Type of question ("open_ended" or "multiple_choice")
            options: List of options for multiple choice questions

        Returns:
            Generated feedback as a string
        """
        if not self.openrouter_client.is_available():
            return "OpenRouter API non disponibile per generare feedback."

        # Route to appropriate feedback method
        if question_type == "multiple_choice":
            return self._generate_mc_feedback(
                question, correct_answer, student_answer, options, 
                annotations, original_text
            )
        else:
            return self._generate_oe_feedback(
                question, correct_answer, student_answer, 
                annotations, original_text
            )

    def _generate_oe_feedback(
        self, 
        question: str, 
        correct_answer: str, 
        student_answer: str,
        annotations: Dict[str, List[str]] = None,
        original_text: str = None
    ) -> str:
        """Generate feedback for open-ended questions with annotation support."""
        
        # Format annotations for the prompt
        formatted_annotations = self._format_annotations(annotations)
        
        # Get relevant text excerpt (first 500 chars as context)
        text_context = original_text[:500] + "..." if original_text and len(original_text) > 500 else original_text or ""
        
        prompt = f"""Sei un tutor educativo che fornisce feedback basato su testi annotati. Il tuo obiettivo è guidare lo studente verso una comprensione più precisa attraverso riferimenti specifici al testo e alle annotazioni (5W). Rispondi SOLO in italiano.

CONTESTO:
- Testo annotato con elementi specifici identificati (5W)
- Domanda di comprensione che richiede analisi del testo
- Annotazioni di riferimento disponibili per guidare la comprensione
- CORRECT ANSWER (modello) di riferimento e STUDENT ANSWER (da valutare)

DOMANDA: {question}

RISPOSTA ATTESA (modello): {correct_answer}

RISPOSTA DELLO STUDENTE (da valutare): {student_answer}

ANNOTAZIONI DI RIFERIMENTO (5W):
{formatted_annotations}

CONTESTO TESTUALE (estratto): 
{text_context}

ISTRUZIONI DI OUTPUT (OBBLIGATORIE):
- Produci ESATTAMENTE tre sezioni con i seguenti titoli (usa questi titoli e nessun altro).
- In ogni sezione scrivi frasi brevi (max 3 o 4 frasi). Totale massimo ~120 parole.
- Fai SEMPRE riferimento a un'annotazione 5W specifica e, se utile, cita al massimo UNA breve citazione dal testo (≤15 parole) tra virgolette.
- Non confondere mai la STUDENT ANSWER con la CORRECT ANSWER. Valuti SOLO la STUDENT ANSWER, citandola come tale.
- Se la STUDENT ANSWER è vuota, fuori tema o < 5 parole, segnala brevemente la criticità e fornisci un micro-passo per riprovare (rimandando al testo/annotazione).
- Mantieni tono professionale, incoraggiante ma non necessariamente entusiasta. 
- Linguaggio conciso, corretto e privo di errori grammaticali.
- Inizia sempre con il positivo.
- Non aggiungere testo prima/dopo le tre sezioni. Nessuna firma, nessuna spiegazione extra.

**☀️ ASPETTI POSITIVI:**
[Conferma uno o due elementi corretti presenti nella STUDENT ANSWER; se parziali, dillo. Indica l'annotazione 5W pertinente e, se utile, una breve citazione.]

**🎯 SUGGERIMENTO PER MIGLIORARE:**
[Un solo suggerimento chiaro e operativo, collegato a una parte precisa del testo o a un'annotazione 5W (nomina il tag, es. "Why: …"). Indica dove rileggere.]

**🤔 DOMANDA METACOGNITIVA:**
[Una sola domanda breve che rimandi a una sezione del testo o a un'annotazione 5W; es.: "Rileggi il passaggio su '…' (tag: Why). In che modo questo dettaglio sostiene/contraddice la tua risposta?"]

FEEDBACK:"""

        return self.openrouter_client.generate(
            model=self.model_name,
            prompt=prompt,
            temperature=0.7,
            max_tokens=1024
        )

    def _generate_mc_feedback(
        self, 
        question: str, 
        correct_answer: str, 
        student_answer: str,
        options: List[Dict[str, str]] = None,
        annotations: Dict[str, List[str]] = None,
        original_text: str = None
    ) -> str:
        """Generate feedback for multiple choice questions with annotation support."""
        
        # Format options for display
        formatted_options = "\n".join([f"{opt['letter']}) {opt['text']}" for opt in options]) if options else ""
        
        # Get correct and student answer texts
        correct_answer_text = ""
        student_answer_text = ""
        if options:
            correct_answer_text = next((opt["text"] for opt in options if opt["letter"] == correct_answer), "")
            student_answer_text = next((opt["text"] for opt in options if opt["letter"] == student_answer), "")
        
        # Format annotations for the prompt
        formatted_annotations = self._format_annotations(annotations)
        
        # Get relevant text excerpt
        text_context = original_text[:500] + "..." if original_text and len(original_text) > 500 else original_text or ""
        
        prompt = f"""Sei un tutor educativo che fornisce feedback per domande a scelta multipla basate su testi annotati. Il tuo obiettivo è chiarire incomprensioni rimandando con precisione alle annotazioni (5W) e al testo.

DOMANDA: {question}

OPZIONI:
{formatted_options}

RISPOSTA CORRETTA: {correct_answer}) {correct_answer_text}
RISPOSTA DELLO STUDENTE: {student_answer}) {student_answer_text}

ANNOTAZIONI DI RIFERIMENTO (5W):
{formatted_annotations}

CONTESTO TESTUALE:
{text_context}

ISTRUZIONI OPERATIVE (seguile alla lettera):
- Se la risposta dello studente è CORRETTA: scrivi UNA sola frase di conferma + un riferimento testuale/annotazione a supporto. Non aggiungere altro.
- Se la risposta è SBAGLIATA: produci le tre sezioni sottostanti.
- Non confondere mai STUDENT ANSWER e CORRECT ANSWER: nominale sempre esplicitamente quale stai commentando.
- Fai SEMPRE un riferimento concreto al testo/annotazioni: o 1 breve citazione tra virgolette (≤ 8 parole) o una parafrasi puntuale + il tag 5W.
- Se nessuna annotazione è pertinente, dichiaralo e usa il passaggio del testo più vicino.
- Non ripetere l'intera opzione corretta; spiega il perché in modo conciso.
- Italiano chiaro, tono professionale e incoraggiante. Niente emoji extra oltre alle intestazioni richieste. Max 2–3 frasi per sezione.

FORMATTO DA RISPETTARE ESATTAMENTE:

[Se CORRETTA → una riga]
✅ Corretto: [breve conferma + 1 riferimento testuale/annotazione]

[Se SBAGLIATA → le tre sezioni seguenti]

**☀️ RICONOSCIMENTO:**
[Riconosci sinteticamente l'impegno o la logica nella STUDENT ANSWER, se pertinente. 1 frase.]

**🎯 CHIARIMENTO:**
[Spiega in modo conciso perché la CORRECT ANSWER è giusta e in cosa la STUDENT ANSWER è imprecisa. Cita o parafrasa 1 punto del testo e richiama l'annotazione 5W. 1 o 2 frasi.]

**📍 RIFERIMENTO TESTUALE:**
[Indica dove trovarlo: "Vedi [citazione ≤8 parole] / vedi annotazione 5W su …". 1 frase.]

VINCOLI:
- Niente contenuti non presenti nel testo/annotazioni.
- Non elencare di nuovo tutte le opzioni.
- Se la scelta dello studente è vuota o non A,B,C oppure D, scrivi: "Risposta non valida: seleziona A,B,C oppure D" e chiudi.

FEEDBACK:"""

        return self.openrouter_client.generate(
            model=self.model_name,
            prompt=prompt,
            temperature=0.3,
            max_tokens=1024
        )

    def _format_annotations(self, annotations: Dict[str, List[str]]) -> str:
        """Format annotations for display in prompts."""
        if not annotations:
            return "Nessuna annotazione disponibile"
        
        formatted = []
        for tag, items in annotations.items():
            # Limit items to avoid overly long prompts
            limited_items = items[:3] if len(items) > 3 else items
            item_text = ", ".join(limited_items)
            if len(items) > 3:
                item_text += f" (e altri {len(items) - 3})"
            formatted.append(f"- {tag}: {item_text}")
        
        return "\n".join(formatted)


