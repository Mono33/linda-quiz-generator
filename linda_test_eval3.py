import os
import pandas as pd
import PyPDF2
import streamlit as st
import tempfile
import json
from typing import List, Dict, Tuple, Any
import re
import requests
import time

# Try to load .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, that's fine


class PDFTextExtractor:
    """Class to extract text from PDF files."""

    @staticmethod
    def extract_text(file_path: str) -> str:
        """
        Extract text from a PDF file.

        Args:
            file_path: Path to the PDF file

        Returns:
            Extracted text as a string
        """
        with open(file_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text


class AnnotationProcessor:
    """Class to process annotation data from CSV files."""

    @staticmethod
    def load_annotations(file_path: str) -> pd.DataFrame:
        """
        Load annotations from a CSV file.

        Args:
            file_path: Path to the CSV file containing annotations

        Returns:
            DataFrame containing the annotations
        """
        return pd.read_csv(file_path)

    @staticmethod
    def group_annotations_by_tag(annotations: pd.DataFrame) -> Dict[str, List[str]]:
        """
        Group annotation text by their tag categories.

        Args:
            annotations: DataFrame containing the annotations

        Returns:
            Dictionary with tag categories as keys and lists of text snippets as values
        """
        grouped = {}
        for _, row in annotations.iterrows():
            tag = row["title"]
            text = row["text"]
            if tag not in grouped:
                grouped[tag] = []
            grouped[tag].append(text)
        return grouped


class OpenRouterClient:
    """Client for interacting with OpenRouter API."""

    def __init__(self, api_key: str = None):
        """
        Initialize the OpenRouter client.

        Args:
            api_key: OpenRouter API key
        """
        # Priority order: passed parameter > environment variable > None
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1"
        
        if self.api_key:
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/Mono33/linda-quiz-generator",
                "X-Title": "Linda Quiz Generator"
            }
        else:
            self.headers = {}

    def is_available(self) -> bool:
        """Check if OpenRouter API is available and API key is valid."""
        if not self.api_key:
            return False
        try:
            response = requests.get(
                f"{self.base_url}/models",
                headers=self.headers,
                timeout=10
            )
            return response.status_code == 200
        except:
            return False

    def generate(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> str:
        """
        Generate text using the OpenRouter API.

        Args:
            model: Name of the model to use
            prompt: Prompt to send to the model
            temperature: Temperature for sampling
            max_tokens: Maximum number of tokens to generate

        Returns:
            Generated text
        """
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                st.error("No response generated from the model")
                return ""
                
        except requests.exceptions.RequestException as e:
            st.error(f"Error calling OpenRouter API: {e}")
            return ""


class QuizGenerator:
    """Class to generate quizzes using OpenRouter."""

    def __init__(self, model_name="mistralai/mistral-7b-instruct"):
        """
        Initialize the quiz generator with an OpenRouter model.

        Args:
            model_name: Name of the OpenRouter model to use
        """
        self.model_name = model_name
        self.openrouter_client = OpenRouterClient()

        # Check if OpenRouter is available
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

    def create_prompt(
        self, text: str, annotations: Dict[str, List[str]], tag_type: str = "5W"
    ) -> str:
        """
        Create a prompt for the language model to generate a quiz.

        Args:
            text: The full text for which to create a quiz
            annotations: Dictionary with tag categories as keys and lists of text snippets
            tag_type: Type of tags used for annotation

        Returns:
            A prompt string for the language model
        """
        annotation_examples = "\n".join(
            [f"- {tag}: {', '.join(items)}" for tag, items in annotations.items()]
        )

        return f"""Sei un assistente educativo che aiuta a creare quiz di comprensione basati su testi annotati.

TESTO:
{text}

ANNOTAZIONI ({tag_type}):
{annotation_examples}

ISTRUZIONI:
Crea un quiz di comprensione in italiano basato sul testo e sulle annotazioni fornite. Il quiz deve includere:
1. Esattamente 2 domande a scelta multipla (con 4 opzioni ciascuna)
2. Esattamente 1 domanda a risposta aperta
3. Ogni domanda deve valutare la comprensione del testo e/o degli elementi linguistici identificati dalle annotazioni
4. Le domande devono essere diverse e adattate al contenuto specifico del testo e al tipo di annotazioni fornite ({tag_type})
5. Fornisci le risposte corrette per ogni domanda

Formato del quiz:
- Numero e tipo di domanda (es. "1. [Scelta Multipla]" o "2. [Risposta Aperta]")
- Testo della domanda 
- Opzioni (solo per le 2 domande a scelta multipla) - presentate una per riga, come nel formato seguente:

    numero domanda. [Scelta Multipla] testo della domanda:
    - A) opzione A
    - B) opzione B
    - C) opzione C
    - D) opzione D
    ✅ Risposta corretta: lettera della risposta corretta

    ⚠️ La risposta corretta deve comparire sempre subito dopo le opzioni (come evidenziato sopra), e non in mezzo al quiz. La lettera indicata (A, B, C, D) deve corrispondere alla risposta realmente esatta, e non essere scelta arbitrariamente.
      
    ⚠️ È FONDAMENTALE che tu segua ESATTAMENTE questo formato per le opzioni delle domande a scelta multipla, con i trattini e gli spazi come indicato sopra.


- Per domande a risposta aperta, dopo il testo della domanda, deve seguire la risposta corretta con il seguente formato:

    numero domanda. [Risposta Aperta] testo della domanda:
    ✅ Risposta: testo della risposta corretta



NON usare un modello fisso di domande. Crea domande originali che si adattano specificamente al testo fornito.
NON aggiungere spiegazioni o commenti extra al quiz.
"""

    def generate_quiz(
        self, text: str, annotations: Dict[str, List[str]], tag_type: str = "5W"
    ) -> str:
        """
        Generate a quiz based on the provided text and annotations.

        Args:
            text: The text to create a quiz for
            annotations: Dictionary with tag categories as keys and lists of text snippets
            tag_type: Type of tags used for annotation

        Returns:
            Generated quiz as a string
        """
        if not self.openrouter_client.is_available():
            return "OpenRouter API non disponibile. Controlla la configurazione della tua API key."

        # Choose generation method based on tag type
        if tag_type == "5W":
            return self._generate_5w_quiz(text, annotations)
        elif tag_type == "Thesis":
            return self._generate_thesis_quiz(text, annotations)
        elif tag_type == "Argument":
            return self._generate_argument_quiz(text, annotations)
        elif tag_type == "Connective":
            return self._generate_connective_quiz(text, annotations)
        else:
            return self._generate_dynamic_quiz(text, annotations, tag_type)

    def _generate_dynamic_quiz(
        self, text: str, annotations: Dict[str, List[str]], tag_type: str
    ) -> str:
        """Generate a quiz dynamically based on the tag type."""
        prompt = self.create_prompt(text, annotations, tag_type)
        return self.openrouter_client.generate(
            model=self.model_name,
            prompt=prompt,
            temperature=0.7,
            max_tokens=2048
        )

    def _generate_5w_quiz(self, text: str, annotations: Dict[str, List[str]]) -> str:
        """Generate a quiz specifically for 5W annotations."""
        annotation_examples = "\n".join(
            [f"- {tag}: {', '.join(items)}" for tag, items in annotations.items()]
        )

        prompt = f"""Sei un assistente educativo specializzato nella creazione di quiz basati sulle 5W (Who, What, When, Where, Why).

TESTO:
{text}

ANNOTAZIONI 5W:
{annotation_examples}

ISTRUZIONI:
Crea un quiz di comprensione in italiano che valuti la comprensione delle 5W nel testo. Il quiz deve includere:

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

Ruolo lingua (OBBLIGATORIO):
- Se il testo è in italiano, il quiz generato deve essere in italiano. Se il testo è in inglese, il quiz generato deve essere in inglese.
- Se il testo è misto, scegli la lingua predominante; se l’equilibrio è incerto, usa l’italiano.
- NON tradurre i contenuti del testo: il quiz generato deve essere sempre nella lingua originale del testo.
- NON mescolare lingue all’interno dello stesso quiz.
- Conserva i nomi propri e le citazioni esattamente come nel testo.
- Eccezione: mantieni SEMPRE in italiano le etichette di struttura necessarie al sistema:
  * "[Scelta Multipla]" e "[Risposta Aperta]"
  * "✅ Risposta corretta:" e "✅ Risposta:"
  * I marcatori A) B) C) D)
  Tutto il resto (testo delle domande, opzioni, eventuali frasi) deve essere nella lingua del testo.
"""

        return self.openrouter_client.generate(
            model=self.model_name,
            prompt=prompt,
            temperature=0.7,
            max_tokens=2048
        )

    def _generate_thesis_quiz(
        self, text: str, annotations: Dict[str, List[str]]
    ) -> str:
        """Generate a quiz specifically for thesis annotations."""
        annotation_examples = "\n".join(
            [f"- {tag}: {', '.join(items)}" for tag, items in annotations.items()]
        )

        prompt = f"""Sei un assistente educativo specializzato nella creazione di quiz per l'analisi di tesi argomentative.

TESTO:
{text}

ANNOTAZIONI TESI:
{annotation_examples}

ISTRUZIONI:
Crea un quiz che valuti la comprensione della struttura argomentativa del testo:

1. **2 domande a scelta multipla** (4 opzioni ciascuna):
   - Una sulla tesi principale
   - Una sugli argomenti di supporto

2. **1 domanda a risposta aperta** sulla valutazione critica della tesi

FORMATO RICHIESTO:
[Usa lo stesso formato della funzione 5W]

Rispondi SOLO con il quiz formattato."""

        return self.openrouter_client.generate(
            model=self.model_name,
            prompt=prompt,
            temperature=0.7,
            max_tokens=2048
        )

    def _generate_argument_quiz(
        self, text: str, annotations: Dict[str, List[str]]
    ) -> str:
        """Generate a quiz specifically for argument annotations."""
        annotation_examples = "\n".join(
            [f"- {tag}: {', '.join(items)}" for tag, items in annotations.items()]
        )

        prompt = f"""Sei un assistente educativo specializzato nell'analisi di argomenti e ragionamenti.

TESTO:
{text}

ANNOTAZIONI ARGOMENTI:
{annotation_examples}

ISTRUZIONI:
Crea un quiz che valuti la comprensione degli argomenti presentati:

1. **2 domande a scelta multipla** (4 opzioni ciascuna):
   - Una sull'identificazione degli argomenti principali
   - Una sulla relazione tra argomenti

2. **1 domanda a risposta aperta** sulla valutazione della forza argomentativa

Rispondi SOLO con il quiz formattato."""

        return self.openrouter_client.generate(
            model=self.model_name,
            prompt=prompt,
            temperature=0.7,
            max_tokens=2048
        )

    def _generate_connective_quiz(
        self, text: str, annotations: Dict[str, List[str]]
    ) -> str:
        """Generate a quiz specifically for connective annotations."""
        annotation_examples = "\n".join(
            [f"- {tag}: {', '.join(items)}" for tag, items in annotations.items()]
        )

        prompt = f"""Sei un assistente educativo specializzato nell'analisi di connettivi testuali.

TESTO:
{text}

ANNOTAZIONI CONNETTIVI:
{annotation_examples}

ISTRUZIONI:
Crea un quiz che valuti la comprensione dei connettivi e della coesione testuale:

1. **2 domande a scelta multipla** (4 opzioni ciascuna):
   - Una sull'identificazione della funzione dei connettivi
   - Una sull'effetto dei connettivi sulla struttura del testo

2. **1 domanda a risposta aperta** sulla riscrittura con connettivi diversi

Rispondi SOLO con il quiz formattato."""

        return self.openrouter_client.generate(
            model=self.model_name,
            prompt=prompt,
            temperature=0.7,
            max_tokens=2048
        )


class FeedbackGenerator:
    """Class to generate feedback for student answers using OpenRouter."""

    def __init__(self, model_name="mistralai/mistral-7b-instruct"):
        """Initialize the feedback generator."""
        self.model_name = model_name
        self.openrouter_client = OpenRouterClient()

    def generate_feedback(
        self, 
        question: str, 
        correct_answer: str, 
        student_answer: str,
        annotations: Dict[str, List[str]] = None,
        original_text: str = None,
        tag_type: str = None,
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
            tag_type: Type of annotations used (5W, Thesis, Argument, Connective)
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
                annotations, original_text, tag_type
            )
        else:
            return self._generate_oe_feedback(
                question, correct_answer, student_answer, 
                annotations, original_text, tag_type
            )

    def _generate_oe_feedback(
        self, 
        question: str, 
        correct_answer: str, 
        student_answer: str,
        annotations: Dict[str, List[str]] = None,
        original_text: str = None,
        tag_type: str = None
    ) -> str:
        """Generate feedback for open-ended questions with annotation support."""
        
        # Format annotations for the prompt
        formatted_annotations = self._format_annotations(annotations, tag_type)
        
        # Get relevant text excerpt (first 500 chars as context)
        text_context = original_text[:500] + "..." if original_text and len(original_text) > 500 else original_text or ""
        
        prompt = f"""Sei un tutor educativo che fornisce feedback basato su testi annotati. Il tuo obiettivo è guidare lo studente verso una comprensione più precisa attraverso riferimenti specifici al testo e alle annotazioni ({tag_type}). Rispondi SOLO in italiano.

CONTESTO:
- Testo annotato con elementi specifici identificati ({tag_type})
- Domanda di comprensione che richiede analisi del testo
- Annotazioni di riferimento disponibili per guidare la comprensione
- CORRECT ANSWER (modello) di riferimento e STUDENT ANSWER (da valutare)

DOMANDA: {question}

RISPOSTA ATTESA (modello): {correct_answer}

RISPOSTA DELLO STUDENTE (da valutare): {student_answer}

ANNOTAZIONI DI RIFERIMENTO ({tag_type}):
{formatted_annotations}

CONTESTO TESTUALE (estratto): 
{text_context}

ISTRUZIONI DI OUTPUT (OBBLIGATORIE):
- Produci ESATTAMENTE tre sezioni con i seguenti titoli (usa questi titoli e nessun altro).
- In ogni sezione scrivi frasi brevi (max 3 o 4 frasi). Totale massimo ~120 parole.
- Fai SEMPRE riferimento a un’annotazione {tag_type} specifica e, se utile, cita al massimo UNA breve citazione dal testo (≤15 parole) tra virgolette.
- Non confondere mai la STUDENT ANSWER con la CORRECT ANSWER. Valuti SOLO la STUDENT ANSWER, citandola come tale.
- Se la STUDENT ANSWER è vuota, fuori tema o < 5 parole, segnala brevemente la criticità e fornisci un micro-passo per riprovare (rimandando al testo/annotazione).
- Mantieni tono professionale, incoraggiante ma non necessariamente entusiasta. 
- Linguaggio conciso, corretto e privo di errori grammaticali.
- Inizia sempre con il positivo.
- Non aggiungere testo prima/dopo le tre sezioni. Nessuna firma, nessuna spiegazione extra.

**☀️ ASPETTI POSITIVI:**
[Conferma uno o due elementi corretti presenti nella STUDENT ANSWER; se parziali, dillo. Indica l’annotazione {tag_type} pertinente e, se utile, una breve citazione.]

**🎯 SUGGERIMENTO PER MIGLIORARE:**
[Un solo suggerimento chiaro e operativo, collegato a una parte precisa del testo o a un’annotazione {tag_type} (nomina il tag, es. “Why: …”). Indica dove rileggere.]

**🤔 DOMANDA METACOGNITIVA:**
[Una sola domanda breve che rimandi a una sezione del testo o a un’annotazione {tag_type}; es.: “Rileggi il passaggio su ‘…’ (tag: Why). In che modo questo dettaglio sostiene/contraddice la tua risposta?”]

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
        original_text: str = None,
        tag_type: str = None
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
        formatted_annotations = self._format_annotations(annotations, tag_type)
        
        # Get relevant text excerpt
        text_context = original_text[:500] + "..." if original_text and len(original_text) > 500 else original_text or ""
        
        prompt = f"""Sei un tutor educativo che fornisce feedback per domande a scelta multipla basate su testi annotati. Il tuo obiettivo è chiarire incomprensioni rimandando con precisione alle annotazioni ({tag_type}) e al testo.

DOMANDA: {question}

OPZIONI:
{formatted_options}

RISPOSTA CORRETTA: {correct_answer}) {correct_answer_text}
RISPOSTA DELLO STUDENTE: {student_answer}) {student_answer_text}

ANNOTAZIONI DI RIFERIMENTO ({tag_type}):
{formatted_annotations}

CONTESTO TESTUALE:
{text_context}

ISTRUZIONI OPERATIVE (seguile alla lettera):
- Se la risposta dello studente è CORRETTA: scrivi UNA sola frase di conferma + un riferimento testuale/annotazione a supporto. Non aggiungere altro.
- Se la risposta è SBAGLIATA: produci le tre sezioni sottostanti.
- Non confondere mai STUDENT ANSWER e CORRECT ANSWER: nominale sempre esplicitamente quale stai commentando.
- Fai SEMPRE un riferimento concreto al testo/annotazioni: o 1 breve citazione tra virgolette (≤ 8 parole) o una parafrasi puntuale + il tag {tag_type}.
- Se nessuna annotazione è pertinente, dichiaralo e usa il passaggio del testo più vicino.
- Non ripetere l’intera opzione corretta; spiega il perché in modo conciso.
- Italiano chiaro, tono professionale e incoraggiante. Niente emoji extra oltre alle intestazioni richieste. Max 2–3 frasi per sezione.

FORMATTO DA RISPETTARE ESATTAMENTE:

[Se CORRETTA → una riga]
✅ Corretto: [breve conferma + 1 riferimento testuale/annotazione]

[Se SBAGLIATA → le tre sezioni seguenti]

**☀️ RICONOSCIMENTO:**
[Riconosci sinteticamente l’impegno o la logica nella STUDENT ANSWER, se pertinente. 1 frase.]

**🎯 CHIARIMENTO:**
[Spiega in modo conciso perché la CORRECT ANSWER è giusta e in cosa la STUDENT ANSWER è imprecisa. Cita o parafrasa 1 punto del testo e richiama l’annotazione {tag_type}. 1 o 2 frasi.]

**📍 RIFERIMENTO TESTUALE:**
[Indica dove trovarlo: “Vedi [citazione ≤8 parole] / vedi annotazione {tag_type} su …”. 1 frase.]

VINCOLI:
- Niente contenuti non presenti nel testo/annotazioni.
- Non elencare di nuovo tutte le opzioni.
- Se la scelta dello studente è vuota o non A,B,C oppure D, scrivi: “Risposta non valida: seleziona A,B,C oppure D” e chiudi.

FEEDBACK:"""

        return self.openrouter_client.generate(
            model=self.model_name,
            prompt=prompt,
            temperature=0.3, #0.7
            max_tokens=1024
        )

    def _format_annotations(self, annotations: Dict[str, List[str]], tag_type: str) -> str:
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

    def _generate_example_feedback(
        self, question: str, correct_answer: str, student_answer: str
    ) -> str:
        """Generate example feedback when OpenRouter is not available."""
        return f"""
        **Feedback di esempio:**
        
        La tua risposta mostra una comprensione parziale del testo. 
        
        **Aspetti positivi:** Hai identificato alcuni elementi chiave.
        
        **Suggerimenti per migliorare:** 
        - Rileggi attentamente il passaggio che riguarda [elemento specifico]
        - Considera il contesto più ampio della domanda
        - Cerca di essere più specifico nella tua risposta
        
        **Risposta corretta:** {correct_answer}
        
        Continua così, stai facendo progressi!
        """


def parse_quiz_text(quiz_text):
    """Parse the quiz text into a structured format for editing."""
    questions = []
    lines = quiz_text.strip().split('\n')
    
    current_question = None
    current_options = []
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Check for new question
        question_match = re.match(r'(\d+)\.\s+\[(Scelta Multipla|Risposta Aperta)\]\s+(.*)', line)
        if question_match:
            # Save previous question if exists
            if current_question:
                questions.append(current_question)
                
            q_num, q_type, q_text = question_match.groups()
            current_question = {
                "number": int(q_num),
                "type": "multiple_choice" if q_type == "Scelta Multipla" else "open_ended",
                "text": q_text,
                "options": [],
                "correct_answer": "A"  # Default to A to prevent empty string errors
            }
            current_options = []
            
        # Check for options in multiple choice
        elif line.startswith('- ') and current_question and current_question["type"] == "multiple_choice":
            option_match = re.match(r'-\s+([A-D])\)\s+(.*)', line)
            if option_match:
                option_letter, option_text = option_match.groups()
                current_question["options"].append({
                    "letter": option_letter,
                    "text": option_text
                })
                
        # Check for correct answer
        elif line.startswith('✅ Risposta corretta:') and current_question:
            if current_question["type"] == "multiple_choice":
                answer_match = re.match(r'✅ Risposta corretta:\s+([A-D])', line)
                if answer_match:
                    current_question["correct_answer"] = answer_match.group(1)
            else:  # open_ended
                current_question["correct_answer"] = line.replace('✅ Risposta corretta:', '').strip()
                
        # For open-ended questions that have answers on next line
        elif line.startswith('✅ Risposta:') and current_question and current_question["type"] == "open_ended":
            current_question["correct_answer"] = line.replace('✅ Risposta:', '').strip()
            
        i += 1
        
    # Add the last question
    if current_question:
        questions.append(current_question)
        
    return questions


def format_structured_quiz(structured_quiz):
    """Convert structured quiz back to formatted text."""
    formatted_text = ""
    
    for question in structured_quiz:
        q_type = "Scelta Multipla" if question["type"] == "multiple_choice" else "Risposta Aperta"
        formatted_text += f"{question['number']}. [{q_type}] {question['text']}\n\n"
        
        if question["type"] == "multiple_choice":
            for option in question["options"]:
                formatted_text += f"- {option['letter']}) {option['text']}\n"
            formatted_text += f"✅ Risposta corretta: {question['correct_answer']}\n\n"
        else:
            formatted_text += f"✅ Risposta: {question['correct_answer']}\n\n"
            
    return formatted_text


class LindaTestEvalApp:
    """Main Streamlit application class."""

    def __init__(self):
        """Initialize the application."""
        st.set_page_config(
            page_title="Linda Test Eval 3.0 - OpenRouter Edition",
            page_icon="📚",
            layout="wide"
        )
        
        # Initialize components
        self.pdf_extractor = PDFTextExtractor()
        self.annotation_processor = AnnotationProcessor()
        self.quiz_generator = QuizGenerator()
        self.feedback_generator = FeedbackGenerator()

    def validate_question(self, question, text, annotations, tag_type):
        """
        Validate if the answer to a question aligns with the text and annotations using AI.
        
        Args:
            question: The structured question with answer
            text: The original text
            annotations: The annotations dictionary
            tag_type: The type of annotations used
            
        Returns:
            Dictionary with validation results: {"is_valid": bool, "suggestion": str, "motivation": str}
        """
        model_name = st.session_state.get("model_name", "mistralai/mistral-7b-instruct")
        openrouter_client = OpenRouterClient()
        
        if not openrouter_client.is_available():
            return {"is_valid": False, "suggestion": "OpenRouter API non disponibile per la validazione.", "motivation": ""}
        
        # Format the question for validation
        if question["type"] == "multiple_choice":
            options_text = "\n".join([f"{opt['letter']}) {opt['text']}" for opt in question["options"]])
            chosen_answer = question["correct_answer"]
            chosen_answer_text = next((opt["text"] for opt in question["options"] 
                                    if opt["letter"] == chosen_answer), "Unknown")
                    
            validation_prompt = f"""Valuta se la risposta selezionata per questa domanda è corretta, basandoti sul testo e sulle annotazioni fornite.

TESTO:
{text[:3000]}  # Limit text size to avoid token limits

ANNOTAZIONI ({tag_type}):
{self._format_annotations(annotations, tag_type)}

DOMANDA:
{question["text"]}

OPZIONI:
{options_text}

RISPOSTA SELEZIONATA: {chosen_answer}) {chosen_answer_text}

Valuta se la risposta è corretta in base al testo. Rispondi in questo formato:
VALIDA: [Sì/No]
SUGGERIMENTO: [La tua raccomandazione se "No", o "La risposta è corretta" se "Sì"]
MOTIVAZIONE: [Breve spiegazione]
"""
        else:  # open_ended
            validation_prompt = f"""Valuta se la risposta fornita per questa domanda a risposta aperta è corretta.

TESTO:
{text[:3000]}  # Limit text size to avoid token limits

ANNOTAZIONI ({tag_type}):
{self._format_annotations(annotations, tag_type)}

DOMANDA:
{question["text"]}

RISPOSTA FORNITA:
{question["correct_answer"]}

Valuta la risposta. Rispondi in questo formato:
VALIDA: [Sì/No]
SUGGERIMENTO: [Il tuo suggerimento se necessario, o "La risposta è corretta" se adeguata]
MOTIVAZIONE: [Breve spiegazione]
"""
        
        # Get validation from OpenRouter
        validation_response = openrouter_client.generate(
            model=model_name, 
            prompt=validation_prompt, 
            temperature=0.3,
            max_tokens=512  # Keep response size reasonable
        )
        
        if not validation_response:
            return {"is_valid": False, "suggestion": "Errore nella validazione AI.", "motivation": ""}
        
        # Parse response
        is_valid = "VALIDA: Sì" in validation_response or "VALIDA: Si" in validation_response
        
        # Extract suggestion
        suggestion_match = re.search(r"SUGGERIMENTO: (.*?)(?:\n|$)", validation_response)
        suggestion = suggestion_match.group(1) if suggestion_match else "No specific suggestion provided."
        
        # Extract motivation
        motivation_match = re.search(r"MOTIVAZIONE: (.*?)(?:\n|$)", validation_response)
        motivation = motivation_match.group(1) if motivation_match else "No explanation provided."
        
        return {
            "is_valid": is_valid,
            "suggestion": suggestion,
            "motivation": motivation
        }

    def _format_annotations(self, annotations: Dict[str, List[str]], tag_type: str) -> str:
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
        
    def show_quiz_editor(self):
        """Display the interactive quiz editor."""
        st.subheader("Quiz Editor")
        
        if "structured_quiz" not in st.session_state:
            st.error("No quiz available to edit.")
            return
        
        edited = False
        edited_quiz = st.session_state["structured_quiz"].copy()
        
        # Settings for validation
        with st.sidebar:
            st.subheader("Validation Settings")
            auto_validate = st.checkbox("Enable automatic validation", 
                                       value=st.session_state.get("auto_validate", False),
                                       help="When enabled, questions will be automatically validated when answers change")
            st.session_state["auto_validate"] = auto_validate
        
        # Editor controls
        with st.container():
            cols = st.columns([3, 1, 1])
            with cols[0]:
                st.write("Edit your quiz below")
            with cols[1]:
                if st.button("Save Changes"):
                    # Check for unvalidated questions
                    has_unvalidated = False
                    for i, question in enumerate(edited_quiz):
                        if question["text"] != "New question text" and (
                            "validation_results" not in st.session_state or 
                            i not in st.session_state.get("validation_results", {})
                        ):
                            has_unvalidated = True
                            break
                            
                    if has_unvalidated:
                        # Offer to validate all questions before saving
                        st.warning("Some questions haven't been validated. Would you like to validate them now?")
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("Validate All", key="validate_all_btn"):
                                # Initialize validation results if needed
                                if "validation_results" not in st.session_state:
                                    st.session_state["validation_results"] = {}
                                    
                                # Validate each question
                                for i, question in enumerate(edited_quiz):
                                    if question["text"] != "New question text":
                                        with st.spinner(f"Validating question {i+1}..."):
                                            result = self.validate_question(
                                                question,
                                                st.session_state["extracted_text"],
                                                st.session_state["grouped_annotations"],
                                                st.session_state["tag_type"]
                                            )
                                            st.session_state["validation_results"][i] = result
                                st.success("All questions validated!")
                                st.rerun()  # Show validation results
                        with col2:
                            if st.button("Save Without Validation", key="save_wo_val_btn"):
                                # Renumber before saving to ensure contiguous numbering
                                for idx, q in enumerate(edited_quiz):
                                    q["number"] = idx + 1
                                # Persist both string and structured forms
                                updated_quiz = format_structured_quiz(edited_quiz)
                                st.session_state["quiz"] = updated_quiz
                                st.session_state["structured_quiz"] = edited_quiz
                                # Mark edited banner
                                st.session_state["has_edited_quiz"] = True
                                st.session_state["edited_at"] = time.strftime("%H:%M")
                                st.session_state["editing_quiz"] = False
                                st.success("Quiz saved without validation!")
                                st.rerun()
                    else:
                        # Format the edited quiz back to text
                        # Renumber before saving
                        for idx, q in enumerate(edited_quiz):
                            q["number"] = idx + 1
                        updated_quiz = format_structured_quiz(edited_quiz)
                        st.session_state["quiz"] = updated_quiz
                        st.session_state["structured_quiz"] = edited_quiz
                        st.session_state["has_edited_quiz"] = True
                        st.session_state["edited_at"] = time.strftime("%H:%M")
                        st.session_state["editing_quiz"] = False
                        st.success("Quiz saved successfully!")
                        st.rerun()
            with cols[2]:
                # Back with unsaved-changes confirmation
                if st.button("Back to Quiz", key="back_to_quiz_btn"):
                    # Detect potentially unsaved validation state
                    pending_unvalidated = False
                    for i, q in enumerate(edited_quiz):
                        if q["text"] != "New question text" and (
                            "validation_results" not in st.session_state or
                            i not in st.session_state.get("validation_results", {})
                        ):
                            pending_unvalidated = True
                            break
                    if pending_unvalidated:
                        st.session_state["confirm_back_unsaved"] = True
                    else:
                        st.session_state["editing_quiz"] = False
                        st.rerun()

            # Unsaved changes confirmation UI
            if st.session_state.get("confirm_back_unsaved"):
                st.warning("You have unsaved changes. Save, discard, or stay on this page?")
                b1, b2, b3 = st.columns(3)
                with b1:
                    if st.button("Save Without Validation", key="confirm_save_wo_val"):
                        for idx, q in enumerate(edited_quiz):
                            q["number"] = idx + 1
                        updated_quiz = format_structured_quiz(edited_quiz)
                        st.session_state["quiz"] = updated_quiz
                        st.session_state["structured_quiz"] = edited_quiz
                        st.session_state["has_edited_quiz"] = True
                        st.session_state["edited_at"] = time.strftime("%H:%M")
                        st.session_state["confirm_back_unsaved"] = False
                        st.session_state["editing_quiz"] = False
                        st.success("Quiz saved.")
                        st.rerun()
                with b2:
                    if st.button("Discard Changes", key="confirm_discard"):
                        st.session_state["confirm_back_unsaved"] = False
                        st.session_state["editing_quiz"] = False
                        st.rerun()
                with b3:
                    if st.button("Stay Here", key="confirm_stay"):
                        st.session_state["confirm_back_unsaved"] = False
        
        # The actual editor for each question
        for i, question in enumerate(edited_quiz):
            with st.expander(f"Question {question['number']}", expanded=True):
                # Question type
                q_type = st.selectbox(
                    "Question Type",
                    options=["Multiple Choice", "Open Ended"],
                    index=0 if question["type"] == "multiple_choice" else 1,
                    key=f"q_type_{i}"
                )
                
                # Question text
                q_text = st.text_area(
                    "Question Text", 
                    value=question["text"],
                    key=f"q_text_{i}"
                )
                
                # Handle different question types
                if q_type == "Multiple Choice":
                    # Multiple choice options
                    options = question.get("options", [])
                    if not options:
                        # Initialize options if converting from open-ended
                        options = [
                            {"letter": "A", "text": ""},
                            {"letter": "B", "text": ""},
                            {"letter": "C", "text": ""},
                            {"letter": "D", "text": ""}
                        ]
                    
                    # Edit each option
                    for j, option in enumerate(options):
                        cols = st.columns([1, 10])
                        with cols[0]:
                            st.write(f"{option['letter']})")
                        with cols[1]:
                            option_text = st.text_input(
                                f"Option {option['letter']}", 
                                value=option["text"],
                                key=f"opt_{i}_{j}"
                            )
                            options[j]["text"] = option_text
                    
                    # Correct answer selection
                    previous_answer = question.get("correct_answer", "A")
                    correct = st.radio(
                        "Correct Answer", 
                        options=["A", "B", "C", "D"],
                        index=ord(question.get("correct_answer", "A")) - ord("A"),
                        key=f"correct_{i}"
                    )
                    
                    # Update the question
                    edited_quiz[i].update({
                        "type": "multiple_choice" if q_type == "Multiple Choice" else "open_ended",
                        "text": q_text,
                        "options": options,
                        "correct_answer": correct
                    })
                    
                    # If auto-validation is enabled and answer changed
                    if auto_validate and correct != previous_answer and question["text"] != "New question text":
                        with st.spinner("Validating answer..."):
                            validation_result = self.validate_question(
                                edited_quiz[i],
                                st.session_state["extracted_text"],
                                st.session_state["grouped_annotations"],
                                st.session_state["tag_type"]
                            )
                            
                            # Store validation result
                            if "validation_results" not in st.session_state:
                                st.session_state["validation_results"] = {}
                            st.session_state["validation_results"][i] = validation_result
                            st.rerun()  # Show validation result
                    
                else:
                    # Open-ended correct answer
                    previous_answer = question.get("correct_answer", "")
                    correct_answer = st.text_area(
                        "Correct Answer", 
                        value=previous_answer,
                        key=f"oe_answer_{i}"
                    )
                    
                    # Update the question
                    edited_quiz[i].update({
                        "type": "open_ended",
                        "text": q_text,
                        "options": [],
                        "correct_answer": correct_answer
                    })
                    
                    # Auto-validate if enabled and significant answer changes
                    if (auto_validate and question["text"] != "New question text" and 
                        (abs(len(correct_answer) - len(previous_answer)) > 20 or 
                         (len(previous_answer) > 10 and not correct_answer.startswith(previous_answer[:10])))):
                        with st.spinner("Validating answer..."):
                            validation_result = self.validate_question(
                                edited_quiz[i],
                                st.session_state["extracted_text"],
                                st.session_state["grouped_annotations"],
                                st.session_state["tag_type"]
                            )
                            
                            # Store validation result
                            if "validation_results" not in st.session_state:
                                st.session_state["validation_results"] = {}
                            st.session_state["validation_results"][i] = validation_result
                            st.rerun()  # Show validation result
                
                # Add Validate button for each question (primary approach)
                if question["text"] != "New question text":  # Don't show for template questions
                    if st.button(f"Validate Question {question['number']} with AI", key=f"validate_{i}"):
                        with st.spinner("Validating with AI..."):
                            validation_result = self.validate_question(
                                edited_quiz[i],
                                st.session_state["extracted_text"],
                                st.session_state["grouped_annotations"],
                                st.session_state["tag_type"]
                            )
                            
                            # Store validation result
                            if "validation_results" not in st.session_state:
                                st.session_state["validation_results"] = {}
                            st.session_state["validation_results"][i] = validation_result
                            st.rerun()  # Show validation result
                
                # Display validation results if available
                if "validation_results" in st.session_state and i in st.session_state["validation_results"]:
                    result = st.session_state["validation_results"][i]
                    if result["is_valid"]:
                        st.success("✓ AI confirms: Answer aligns with the text")
                    else:
                        st.warning(f"⚠️ AI suggests: {result['suggestion']}")
                        # Add the "Show AI Reasoning" checkbox toggle
                        show_reasoning = st.checkbox(f"🔍 Show AI Reasoning for Q{question['number']}", key=f"reasoning_{i}")
                        if show_reasoning:
                            st.markdown("**AI Reasoning:**")
                            st.markdown(result["motivation"])
                
                # Question removal (DELETE QUESTION BUTTON with confirmation)
                confirm_flag_key = f"confirm_delete_{i}"
                if st.button(f"Delete Question {question['number']}", key=f"del_q_{i}"):
                    st.session_state[confirm_flag_key] = True

                if st.session_state.get(confirm_flag_key):
                    st.warning(f"Are you sure you want to delete question {question['number']}?")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("Yes, delete", key=f"yes_del_{i}"):
                            # Perform deletion
                            del edited_quiz[i]
                            # Re-number remaining questions to keep sequence clean
                            for idx, q in enumerate(edited_quiz):
                                q["number"] = idx + 1
                            # Persist to session state immediately
                            st.session_state["structured_quiz"] = edited_quiz
                            # Remove any stored validation for this and subsequent indices
                            if "validation_results" in st.session_state:
                                st.session_state["validation_results"] = {
                                    new_idx: res for new_idx, res in enumerate([
                                        st.session_state["validation_results"].get(old_idx)
                                        for old_idx in sorted(st.session_state["validation_results"].keys())
                                    ]) if res is not None
                                }
                            # Clear confirm flag and refresh
                            st.session_state.pop(confirm_flag_key, None)
                            st.success("Question deleted.")
                            st.rerun()
                    with c2:
                        if st.button("No, keep it", key=f"no_del_{i}"):
                            st.session_state.pop(confirm_flag_key, None)
                            st.experimental_rerun()
        
        # Add a new question (ADD NEW QUESTION BUTTON)
        if st.button("Add New Question"):
            # Determine new question number
            new_num = max([q["number"] for q in edited_quiz], default=0) + 1
            
            # Add a template question
            edited_quiz.append({
                "number": new_num,
                "type": "multiple_choice",
                "text": "New question text",
                "options": [
                    {"letter": "A", "text": "Option A"},
                    {"letter": "B", "text": "Option B"},
                    {"letter": "C", "text": "Option C"},
                    {"letter": "D", "text": "Option D"}
                ],
                "correct_answer": "A"
            })
            # Re-number just in case previous operations left gaps
            for idx, q in enumerate(edited_quiz):
                q["number"] = idx + 1
            
            # Update session state and refresh
            st.session_state["structured_quiz"] = edited_quiz
            st.rerun()
        
        # Validate All Questions button (VALIDATE ALL QUESTIONS WITH AI BUTTON)
        if edited_quiz and st.button("Validate All Questions with AI"):
            # Initialize validation results if needed
            if "validation_results" not in st.session_state:
                st.session_state["validation_results"] = {}
                
            # Validate each non-template question
            for i, question in enumerate(edited_quiz):
                if question["text"] != "New question text":
                    with st.spinner(f"Validating question {i+1}..."):
                        result = self.validate_question(
                            question,
                            st.session_state["extracted_text"],
                            st.session_state["grouped_annotations"],
                            st.session_state["tag_type"]
                        )
                        st.session_state["validation_results"][i] = result
            st.success("All questions validated!")
            st.rerun()  # Show validation results
        
        # Preview the edited quiz (QUIZ PREVIEW SECTION)
        st.subheader("Quiz Preview")
        preview = format_structured_quiz(edited_quiz)
        st.markdown(preview)

    def run(self):
        """Run the Streamlit application."""
        st.title("Linda Test Eval 3.0 - OpenRouter Edition")
        st.markdown("### Upload annotated text and generate comprehension quizzes")

        # Dynamic status message showing current OpenRouter status and selected model
        env_api_key = os.getenv("OPENROUTER_API_KEY")
        current_model = st.session_state.get("model_name", "mistralai/mistral-7b-instruct")
        
        if env_api_key:
            openrouter_client = OpenRouterClient()
            if openrouter_client.is_available():
                st.success(f"OpenRouter API is available. Using model: {current_model}")
            else:
                st.error("❌ OpenRouter API is not available")
        else:
            st.error("❌ OpenRouter API key not found")

        # Initialize session state variables for quiz editing
        if "quiz" not in st.session_state:
            st.session_state["quiz"] = ""
        if "editing_quiz" not in st.session_state:
            st.session_state["editing_quiz"] = False
        if "structured_quiz" not in st.session_state:
            st.session_state["structured_quiz"] = []
        # Add session state for storing extracted text and annotations
        if "extracted_text" not in st.session_state:
            st.session_state["extracted_text"] = ""
        if "grouped_annotations" not in st.session_state:
            st.session_state["grouped_annotations"] = {}
        if "use_example" not in st.session_state:
            st.session_state["use_example"] = False
        if "tag_type" not in st.session_state:
            st.session_state["tag_type"] = "5W"
        # Add session state for raw file bytes
        if "uploaded_pdf_bytes" not in st.session_state:
            st.session_state["uploaded_pdf_bytes"] = None
        if "uploaded_annotations_bytes" not in st.session_state:
            st.session_state["uploaded_annotations_bytes"] = None
            
        # Show the editor if editing mode is active
        if st.session_state.get("editing_quiz", False):
            self.show_quiz_editor()
            return

        # Sidebar for configuration
        with st.sidebar:
            st.header("Configuration")
            tag_type = st.selectbox(
                "Tag Type", ["5W", "Thesis", "Argument", "Connective"], index=0
            )
            # Store tag type in session state
            st.session_state["tag_type"] = tag_type

            # OpenRouter model selection
            st.subheader("OpenRouter Settings")
            model_options = {
                "mistralai/mistral-7b-instruct": "Mistral 7B",
                "anthropic/claude-3.5-haiku": "Claude 3.5 Haiku",
                "anthropic/claude-3.5-sonnet": "Claude 3.5 Sonnet",
                "openai/gpt-3.5-turbo": "GPT-3.5 Turbo",
                "openai/gpt-4o": "GPT-4o",
                "openai/gpt-4o-mini": "GPT-4o Mini",
                "google/gemma-3n-e4b-it:free": "Gemma 3 4B (Free)"
            }
            
            model_name = st.selectbox(
                "Select OpenRouter Model",
                options=list(model_options.keys()),
                format_func=lambda x: model_options[x],
                index=0,
            )
            # Store the selected model in session state
            st.session_state["model_name"] = model_name

            # Update model settings
            if st.button("Update Model"):
                self.quiz_generator = QuizGenerator(model_name)
                self.feedback_generator = FeedbackGenerator(model_name)
                st.success(f"Model updated to {model_options[model_name]}")

            st.header("About")
            st.info(
                "This tool helps teachers create comprehension quizzes based on "
                "annotated texts. Upload a PDF and the corresponding annotations CSV "
                "to generate quizzes for your students.\n\n"
                "This version uses OpenRouter to access AI models in the cloud."
            )

            # OpenRouter status and setup
            if env_api_key:
                st.success("✅ OpenRouter API Key found")
                masked_key = f"{env_api_key[:8]}...{env_api_key[-4:]}"
                st.info(f"🔐 Key: {masked_key}")
            else:
                st.error("❌ OpenRouter API Key not found")
                with st.expander("📋 Setup Instructions"):
                    st.markdown("""
                    **Get your API Key:**
                    1. Visit [openrouter.ai](https://openrouter.ai/)
                    2. Create an account
                    3. Generate an API key
                    
                    **Set as environment variable:**
                    
                    Windows PowerShell:
                    ```
                    $env:OPENROUTER_API_KEY="your_key_here"
                    ```
                    
                    Or create a `.env` file:
                    ```
                    OPENROUTER_API_KEY=your_key_here
                    ```
                    """)

        # File upload section
        st.header("Upload Files")
        col1, col2 = st.columns(2)

        with col1:
            uploaded_pdf = st.file_uploader("Upload PDF Text", type=["pdf"])
            # Store the raw PDF bytes when uploaded
            if uploaded_pdf:
                st.session_state["uploaded_pdf_bytes"] = uploaded_pdf.getvalue()

        with col2:
            uploaded_annotations = st.file_uploader("Upload Annotations", type=["csv"])
            # Store the raw annotation bytes when uploaded
            if uploaded_annotations:
                st.session_state["uploaded_annotations_bytes"] = uploaded_annotations.getvalue()

        # Example data option
        use_example = st.checkbox("Use example data", value=st.session_state.get("use_example", False))
        st.session_state["use_example"] = use_example

        # Process files if needed or use stored data
        text = st.session_state.get("extracted_text", "")
        grouped_annotations = st.session_state.get("grouped_annotations", {})
        
        # Process files - either from new uploads, stored bytes, or example data
        if not text or not grouped_annotations:
            with st.spinner("Processing input files..."):
                if use_example:
                    # Use the example files included in the data_input folder
                    pdf_path = "data_input/Il_giocatore_di_basket_Samardo_Samuels_ha_lasciato_la_casa_d.pdf"
                    annotations_path = "data_input/annotations.csv"

                    text = self.pdf_extractor.extract_text(pdf_path)
                    annotations_df = self.annotation_processor.load_annotations(
                        annotations_path
                    )
                elif uploaded_pdf and uploaded_annotations:
                    # Process newly uploaded files
                    with tempfile.NamedTemporaryFile(
                        delete=False, suffix=".pdf"
                    ) as temp_pdf:
                        temp_pdf.write(uploaded_pdf.getvalue())
                        pdf_path = temp_pdf.name

                    with tempfile.NamedTemporaryFile(
                        delete=False, suffix=".csv"
                    ) as temp_annotations:
                        temp_annotations.write(uploaded_annotations.getvalue())
                        annotations_path = temp_annotations.name

                    text = self.pdf_extractor.extract_text(pdf_path)
                    annotations_df = self.annotation_processor.load_annotations(
                        annotations_path
                    )

                    # Clean up temporary files
                    os.unlink(pdf_path)
                    os.unlink(annotations_path)
                    
                elif st.session_state.get("uploaded_pdf_bytes") and st.session_state.get("uploaded_annotations_bytes"):
                    # Process files from stored bytes if available
                    with tempfile.NamedTemporaryFile(
                        delete=False, suffix=".pdf"
                    ) as temp_pdf:
                        temp_pdf.write(st.session_state["uploaded_pdf_bytes"])
                        pdf_path = temp_pdf.name

                    with tempfile.NamedTemporaryFile(
                        delete=False, suffix=".csv"
                    ) as temp_annotations:
                        temp_annotations.write(st.session_state["uploaded_annotations_bytes"])
                        annotations_path = temp_annotations.name

                    text = self.pdf_extractor.extract_text(pdf_path)
                    annotations_df = self.annotation_processor.load_annotations(
                        annotations_path
                    )

                    # Clean up temporary files
                    os.unlink(pdf_path)
                    os.unlink(annotations_path)
                
                if text and 'annotations_df' in locals():
                    # Group annotations by tag
                    grouped_annotations = (
                        self.annotation_processor.group_annotations_by_tag(annotations_df)
                    )
                    
                    # Store in session state
                    st.session_state["extracted_text"] = text
                    st.session_state["grouped_annotations"] = grouped_annotations

        # Display extracted text and annotations if available
        if text and grouped_annotations:
            st.header("Extracted Text")
            st.text_area("", text, height=200)

            st.header("Annotations")
            for tag, items in grouped_annotations.items():
                st.subheader(f"{tag}")
                st.write(", ".join(items))

            # Generate quiz
            st.header("Generated Quiz")
            
            # Create a row with two columns for buttons
            quiz_action_col1, quiz_action_col2 = st.columns([1, 1])
            
            with quiz_action_col1:
                generate_button = st.button("Generate Quiz")
            
            with quiz_action_col2:
                # Show Edit Quiz button if we have a quiz in session state
                if st.session_state.get("quiz"):
                    edit_button = st.button("✏️ Edit Quiz")
                    if edit_button:
                        st.session_state["editing_quiz"] = True
                        st.rerun()
            
            # Display the quiz and action buttons afterwards
            if generate_button:
                # Update quiz generator with current model settings
                model_name = st.session_state.get("model_name", "mistralai/mistral-7b-instruct")
                self.quiz_generator = QuizGenerator(model_name)

                # Log which model is being used
                st.info(f"Using model: {model_options.get(model_name, model_name)} for quiz generation")

                quiz = self.quiz_generator.generate_quiz(
                    text, grouped_annotations, st.session_state["tag_type"]
                )
                
                # Store the quiz in session state for editing
                st.session_state["quiz"] = quiz
                
                # Parse quiz into structured format for easier editing
                st.session_state["structured_quiz"] = parse_quiz_text(quiz)
                
                # Display the generated quiz
                st.markdown(quiz)
                
                # Save quiz option
                quiz_data = {
                    "text": text,
                    "annotations": grouped_annotations,
                    "quiz": quiz,
                    "tag_type": st.session_state["tag_type"],
                }
                st.download_button(
                    label="Download Quiz",
                    data=json.dumps(quiz_data, indent=2),
                    file_name="generated_quiz.json",
                    mime="application/json",
                )
                
                # Force a rerun to update the UI with the Edit button
                st.rerun()
            
            # Display the stored quiz if it exists and we're not in editing mode
            elif st.session_state.get("quiz") and not st.session_state.get("editing_quiz"):
                st.markdown(st.session_state["quiz"])
                
                # Save quiz option
                quiz_data = {
                    "text": text,
                    "annotations": grouped_annotations,
                    "quiz": st.session_state["quiz"],
                    "tag_type": st.session_state["tag_type"],
                }
                st.download_button(
                    label="Download Quiz",
                    data=json.dumps(quiz_data, indent=2),
                    file_name="generated_quiz.json",
                    mime="application/json",
                )

            # Quick load from generated quiz
            if st.session_state.get("structured_quiz"):
                with st.expander("🚀 Student Feedback Mode: Load from Generated Quiz"):
                    st.write("Select a question from your generated quiz to test feedback:")
                    
                    # Create display options for quiz questions
                    quiz_options = []
                    for i, q in enumerate(st.session_state["structured_quiz"]):
                        q_type_display = "MC" if q["type"] == "multiple_choice" else "OE"
                        display_text = f"Q{q['number']} ({q_type_display}): {q['text'][:60]}..."
                        quiz_options.append((i, display_text, q))
                    
                    selected_quiz_q = st.selectbox(
                        "Choose question:",
                        options=quiz_options,
                        format_func=lambda x: x[1],
                        key="quiz_question_selector"
                    )
                    
                    if st.button("Load Selected Question"):
                        selected_q = selected_quiz_q[2]
                        
                        # Update session state with selected question data
                        st.session_state["loaded_question"] = selected_q["text"]
                        st.session_state["loaded_correct_answer"] = selected_q["correct_answer"]
                        st.session_state["loaded_question_type"] = "Multiple Choice" if selected_q["type"] == "multiple_choice" else "Open-Ended"
                        
                        if selected_q["type"] == "multiple_choice":
                            st.session_state["loaded_options"] = selected_q["options"]
                        
                        st.success(f"Loaded Q{selected_q['number']} - Now fill in the student answer below!")
                        st.rerun()

            # Pre-populate fields if question was loaded from quiz
            if "loaded_question" in st.session_state:
                question = st.text_area(
                    "Question",
                    value=st.session_state.get("loaded_question", ""),
                    help="Enter the question text (loaded from quiz)"
                )
                
                # Set question type from loaded data
                if "loaded_question_type" in st.session_state:
                    default_type_index = 0 if st.session_state["loaded_question_type"] == "Open-Ended" else 1
                    question_type = st.radio(
                        "Question Type:",
                        ["Open-Ended", "Multiple Choice"],
                        index=default_type_index,
                        horizontal=True,
                        help="Question type (loaded from quiz)"
                    )
            else:
                question = st.text_area(
                    "Question",
                    "",
                    help="Enter the question text"
                )
                
                # Question type selection
                question_type = st.radio(
                    "Question Type:",
                    ["Open-Ended", "Multiple Choice"],
                    horizontal=True,
                    help="Select the type of question you want to test feedback for"
                )

            if question_type == "Multiple Choice":
                st.write("**Question Options:**")
                col1, col2 = st.columns(2)
                
                with col1:
                    option_a = st.text_input("A)", placeholder="Option A text", key="opt_a")
                    option_c = st.text_input("C)", placeholder="Option C text", key="opt_c")
                
                with col2:
                    option_b = st.text_input("B)", placeholder="Option B text", key="opt_b")
                    option_d = st.text_input("D)", placeholder="Option D text", key="opt_d")
                
                # Create options list for the feedback system
                options = [
                    {"letter": "A", "text": option_a},
                    {"letter": "B", "text": option_b},
                    {"letter": "C", "text": option_c},
                    {"letter": "D", "text": option_d}
                ]
                
                col1, col2 = st.columns(2)
                with col1:
                    correct_answer = st.radio("Correct Answer:", ["A", "B", "C", "D"], key="correct_mc")
                with col2:
                    student_answer = st.radio("Student Selected:", ["A", "B", "C", "D"], key="student_mc")
                    
            else:  # Open-Ended
                correct_answer = st.text_area(
                    "Correct Answer",
                    "",
                    help="Enter the expected correct answer"
                )
                student_answer = st.text_area(
                    "Student Answer", 
                    "",
                    help="Enter the student's actual answer"
                )
                options = None

            if st.button("Generate Feedback") and student_answer and question:
                # Update feedback generator with current model settings
                model_name = st.session_state.get("model_name", "mistralai/mistral-7b-instruct")
                self.feedback_generator = FeedbackGenerator(model_name)

                # Log which model is being used
                st.info(f"Using model: {model_options.get(model_name, model_name)} for feedback generation")

                # Determine question type for the API
                api_question_type = "multiple_choice" if question_type == "Multiple Choice" else "open_ended"

                feedback = self.feedback_generator.generate_feedback(
                    question, 
                    correct_answer, 
                    student_answer,
                    annotations=st.session_state.get("grouped_annotations"),
                    original_text=st.session_state.get("extracted_text"),
                    tag_type=st.session_state.get("tag_type", "5W"),
                    question_type=api_question_type,
                    options=options if question_type == "Multiple Choice" else None
                )
                st.info(feedback)


def main():
    """Main function to run the application."""
    app = LindaTestEvalApp()
    app.run()


if __name__ == "__main__":
    main() 