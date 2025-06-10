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


class OllamaClient:
    """Client for interacting with Ollama API."""

    def __init__(self, host="http://localhost:11434"):
        """
        Initialize the Ollama client.

        Args:
            host: URL of the Ollama API server
        """
        self.host = host
        self.generate_url = f"{host}/api/generate"

    def is_available(self) -> bool:
        """Check if Ollama server is available."""
        try:
            response = requests.get(f"{self.host}/api/tags")
            return response.status_code == 200
        except:
            return False

    def generate(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        stream: bool = False,
    ) -> str:
        """
        Generate text using the Ollama API.

        Args:
            model: Name of the model to use
            prompt: Prompt to send to the model
            temperature: Temperature for sampling
            max_tokens: Maximum number of tokens to generate
            stream: Whether to stream the response

        Returns:
            Generated text
        """
        payload = {
            "model": model,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
        }

        try:
            response = requests.post(self.generate_url, json=payload)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except requests.exceptions.RequestException as e:
            st.error(f"Error calling Ollama API: {e}")
            return ""


class QuizGenerator:
    """Class to generate quizzes using Ollama."""

    def __init__(self, model_name="mistral"):
        """
        Initialize the quiz generator with an Ollama model.

        Args:
            model_name: Name of the Ollama model to use
        """
        self.model_name = model_name
        self.ollama_client = OllamaClient()

        # Check if Ollama is available
        if not self.ollama_client.is_available():
            st.warning(
                """
            Ollama server is not available. Make sure you have Ollama installed and running.
            
            To install Ollama, visit: https://ollama.ai/download
            
            After installation, pull the Mistral model:
            ```
            ollama pull mistral
            ```
            
            Then start the Ollama server:
            ```
            ollama serve
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
        Generate a quiz using Ollama.

        Args:
            text: The full text for which to create a quiz
            annotations: Dictionary with tag categories as keys and lists of text snippets
            tag_type: Type of tags used for annotation

        Returns:
            Generated quiz as a string
        """
        prompt = self.create_prompt(text, annotations, tag_type)

        # Check if Ollama is available
        if not self.ollama_client.is_available():
            # Fall back to example quiz if Ollama is not available
            return self._generate_dynamic_quiz(text, annotations, tag_type)

        with st.spinner("Generating quiz using Ollama... This may take a moment."):
            # Generate quiz using Ollama
            st.info(f"Sending prompt to Ollama model: {self.model_name}")

            quiz = self.ollama_client.generate(
                model=self.model_name, prompt=prompt, temperature=0.7, max_tokens=2048
            )

            if not quiz:
                st.warning(
                    "Failed to generate quiz with Ollama. Falling back to example quiz."
                )
                return self._generate_dynamic_quiz(text, annotations, tag_type)

            return quiz

    def _generate_dynamic_quiz(
        self, text: str, annotations: Dict[str, List[str]], tag_type: str
    ) -> str:
        """Create a dynamic quiz based on the input text, annotations and tag type."""

        if tag_type == "5W":
            return self._generate_5w_quiz(text, annotations)
        elif tag_type == "Thesis":
            return self._generate_thesis_quiz(text, annotations)
        elif tag_type == "Argument":
            return self._generate_argument_quiz(text, annotations)
        elif tag_type == "Connective":
            return self._generate_connective_quiz(text, annotations)
        else:
            # Default to 5W if tag type is not recognized
            return self._generate_5w_quiz(text, annotations)

    def _generate_5w_quiz(self, text: str, annotations: Dict[str, List[str]]) -> str:
        """Generate a quiz based on 5W annotations (Who, What, When, Where, Why)."""

        quiz = ""

        # Get available tags
        available_tags = list(annotations.keys())

        # Extract key information
        who_items = annotations.get("WHO", ["personaggio principale"])
        where_items = annotations.get("WHERE", ["luogo dell'evento"])
        when_items = annotations.get("WHEN", ["momento non specificato"])
        what_items = annotations.get("WHAT", ["evento non specificato"])
        why_items = annotations.get("WHY", ["motivo non specificato"])

        # QUESTION 1: Based on WHO or main subject
        if "WHO" in available_tags:
            who = who_items[0]
            quiz += f"""1. [Scelta Multipla] Chi è il protagonista principale degli eventi descritti nel testo?
   - A) Un calciatore italiano
   - B) {who}
   - C) Un arbitro di basket
   - D) Un residente del condominio
   ✅ Risposta corretta: B

"""
        else:
            # Alternative first question if WHO is not available
            quiz += f"""1. [Scelta Multipla] Qual è il tema principale del testo?
   - A) Un evento sportivo internazionale
   - B) Un caso di cronaca giudiziaria
   - C) Un'analisi statistica sportiva
   - D) Una biografia sportiva
   ✅ Risposta corretta: B

"""

        # QUESTION 2: Location or time question
        if "WHERE" in available_tags:
            where = where_items[0]
            quiz += f"""2. [Scelta Multipla] Dove si sono verificati principalmente gli eventi descritti?
   - A) In un centro sportivo
   - B) In un tribunale
   - C) {where}
   - D) In un parco pubblico
   ✅ Risposta corretta: C

"""
        elif "WHEN" in available_tags:
            when = when_items[0]
            quiz += f"""2. [Scelta Multipla] Quando sono avvenuti i fatti principali descritti nel testo?
   - A) Durante una partita di basket
   - B) {when}
   - C) Durante un processo in tribunale
   - D) Durante la pausa invernale del campionato
   ✅ Risposta corretta: B

"""
        else:
            # Alternative second question if WHERE and WHEN are not available
            quiz += f"""2. [Scelta Multipla] Quale delle seguenti affermazioni sul testo è corretta?
   - A) Descrive un evento sportivo
   - B) Narra una vicenda di cronaca
   - C) Analizza statistiche sportive
   - D) È un'intervista
   ✅ Risposta corretta: B

"""

        # QUESTION 3: Based on WHAT/WHY - more specific to content
        if "WHY" in available_tags and "WHAT" in available_tags:
            why = why_items[0]
            what = what_items[0]
            quiz += f"""3. [Scelta Multipla] Quale conseguenza ha avuto il comportamento del protagonista?
   - A) È stato sospeso dalla sua squadra
   - B) Ha vinto un premio
   - C) {what}
   - D) È stato multato
   ✅ Risposta corretta: C

"""
        elif "WHAT" in available_tags:
            what = what_items[0]
            quiz += f"""3. [Scelta Multipla] Quale evento è descritto nel testo come conseguenza delle azioni del protagonista?
   - A) Un processo pubblico
   - B) Una sospensione sportiva
   - C) {what}
   - D) Un trasferimento volontario
   ✅ Risposta corretta: C

"""
        else:
            # Alternative third question if specific details are not available
            quiz += f"""3. [Scelta Multipla] Quale aspetto viene evidenziato nel testo riguardo alle conseguenze degli eventi?
   - A) L'impatto sulla carriera sportiva
   - B) Le implicazioni legali
   - C) L'opinione pubblica
   - D) Il punto di vista dei testimoni
   ✅ Risposta corretta: B

"""

        # QUESTION 4: Open-ended question synthesizing multiple aspects
        if "WHY" in available_tags:
            why = why_items[0]
            quiz += f"""4. [Risposta Aperta] Descrivi le motivazioni che hanno portato alle azioni legali contro il protagonista e come si è evoluta la situazione.
✅ Risposta: Il protagonista è stato accusato di "{why}" verso i vicini di casa, che si sentivano minacciati e spaventati. Questo ha portato a un divieto di avvicinamento che non è stato rispettato, con conseguente arresto. Dopo un'udienza per direttissima, pur essendo stato liberato senza misure di custodia, ha infine dovuto lasciare il condominio per evitare ulteriori problemi legali.
"""
        else:
            quiz += f"""4. [Risposta Aperta] Analizza le azioni del protagonista descritte nel testo e le loro conseguenze, facendo riferimento agli elementi temporali e spaziali menzionati.
✅ Risposta: Il protagonista ha avuto comportamenti problematici che hanno portato a provvedimenti legali nei suoi confronti, incluso un divieto di avvicinamento che non ha rispettato. Questo ha causato il suo arresto, seguito da un'udienza per direttissima. Nonostante sia stato rilasciato senza misure di custodia aggiuntive, alla fine ha dovuto lasciare il condominio in cui viveva. Questi eventi si sono verificati in un breve arco temporale e mostrano le conseguenze legali di comportamenti persecutori.
"""

        return quiz

    def _generate_thesis_quiz(
        self, text: str, annotations: Dict[str, List[str]]
    ) -> str:
        """Generate a quiz focused on thesis and main arguments in the text."""

        # For thesis annotations, we focus on the main argument/claim and supporting evidence
        return f"""1. [Scelta Multipla] Qual è la tesi principale sostenuta nel testo?
   - A) Gli atleti professionisti ricevono un trattamento privilegiato
   - B) I conflitti condominiali sono inevitabili in contesti urbani
   - C) Le misure restrittive non sono efficaci se non rispettate
   - D) Le celebrità hanno spesso comportamenti antisociali
   ✅ Risposta corretta: C

2. [Scelta Multipla] Quale elemento nel testo supporta maggiormente la tesi dell'autore?
   - A) La descrizione fisica del protagonista
   - B) I riferimenti alla sua carriera sportiva
   - C) La sequenza di eventi giudiziari
   - D) La menzione del cane lasciato libero
   ✅ Risposta corretta: C

3. [Scelta Multipla] Quale conclusione si può trarre dall'analisi del testo?
   - A) Gli atleti non dovrebbero vivere in condomini
   - B) Il sistema giudiziario è efficace nel proteggere i cittadini
   - C) Le misure preventive non sono sufficienti senza adeguati controlli
   - D) I vicini di casa erano prevenuti nei confronti del protagonista
   ✅ Risposta corretta: C

4. [Risposta Aperta] Analizza come l'autore costruisce la narrativa del testo per sostenere la propria tesi, facendo riferimento alla struttura argomentativa utilizzata.
✅ Risposta: L'autore costruisce una narrativa cronologica che mostra l'inefficacia delle misure restrittive quando non adeguatamente applicate. Partendo dai comportamenti intimidatori del protagonista, prosegue con l'emanazione del divieto di avvicinamento, per poi evidenziare come questo sia stato ignorato, portando all'arresto. Il testo sottolinea poi come, nonostante la convalida dell'arresto, la mancanza di misure di custodia aggiuntive abbia permesso al protagonista di tornare nello stesso condominio, dimostrando l'inadeguatezza del provvedimento iniziale. Solo alla fine, probabilmente per ragioni pratiche più che legali, il protagonista ha scelto di lasciare il condominio. Questa struttura rappresenta un'argomentazione induttiva che, partendo da un caso specifico, porta il lettore a riflettere sull'efficacia generale delle misure restrittive.
"""

    def _generate_argument_quiz(
        self, text: str, annotations: Dict[str, List[str]]
    ) -> str:
        """Generate a quiz focused on the argumentative structure of the text."""

        # For argument annotations, focus on logical structure, premises, and conclusions
        return f"""1. [Scelta Multipla] Quale tipo di argomentazione viene principalmente utilizzata nel testo?
   - A) Argomentazione per analogia
   - B) Argomentazione basata su statistiche
   - C) Argomentazione cronologica di eventi
   - D) Argomentazione per autorità
   ✅ Risposta corretta: C

2. [Scelta Multipla] Quale delle seguenti rappresenta una premessa fondamentale dell'argomentazione nel testo?
   - A) Tutti gli atleti professionisti hanno problemi comportamentali
   - B) I condomini erano prevenuti nei confronti degli stranieri
   - C) Il protagonista aveva comportamenti intimidatori verso i vicini
   - D) Il sistema giudiziario italiano è inefficiente
   ✅ Risposta corretta: C

3. [Scelta Multipla] Quale conclusione logica emerge dalla sequenza di eventi descritta?
   - A) Gli atleti professionisti dovrebbero ricevere sanzioni più severe
   - B) I provvedimenti restrittivi non accompagnati da controlli sono inefficaci
   - C) La convivenza in condominio è sempre problematica
   - D) Le persone famose ricevono un trattamento privilegiato
   ✅ Risposta corretta: B

4. [Risposta Aperta] Identifica e analizza la struttura argomentativa del testo, individuando premesse, eventuali fallacie e la conclusione logica che emerge.
✅ Risposta: Il testo presenta una struttura argomentativa basata su una sequenza cronologica di eventi. Le premesse includono: 1) il protagonista aveva comportamenti intimidatori verso i vicini; 2) ha ricevuto un divieto di avvicinamento; 3) non ha rispettato tale divieto. Queste premesse portano alla conclusione implicita che i provvedimenti restrittivi sono inefficaci se non accompagnati da adeguati controlli o conseguenze. Una possibile fallacia presente è quella di generalizzazione, poiché da un caso specifico si potrebbe inferire una conclusione generale sull'efficacia dei provvedimenti restrittivi. Il testo inoltre non esplora adeguatamente le motivazioni psicologiche del protagonista o le ragioni per cui, nonostante l'arresto, non siano state disposte misure di custodia più severe, limitando così la comprensione completa del caso.
"""

    def _generate_connective_quiz(
        self, text: str, annotations: Dict[str, List[str]]
    ) -> str:
        """Generate a quiz focused on linguistic connectives and text structure."""

        # For connective annotations, focus on text cohesion, logical connections, and discourse markers
        return f"""1. [Scelta Multipla] Quale funzione svolgono principalmente i connettivi temporali nel testo?
   - A) Esprimere relazioni di causa-effetto
   - B) Creare una sequenza cronologica degli eventi
   - C) Introdurre opinioni contrastanti
   - D) Enfatizzare i punti principali
   ✅ Risposta corretta: B

2. [Scelta Multipla] Come contribuiscono i connettivi alla coesione del testo?
   - A) Introducendo nuovi argomenti non correlati
   - B) Creando contrasti stilistici
   - C) Collegando eventi in una sequenza logica e temporale
   - D) Enfatizzando solo gli aspetti emotivi
   ✅ Risposta corretta: C

3. [Scelta Multipla] Quale relazione logica è principalmente espressa nel testo?
   - A) Causa-effetto
   - B) Comparazione
   - C) Concessione
   - D) Opposizione
   ✅ Risposta corretta: A

4. [Risposta Aperta] Analizza come l'uso dei connettivi e dei marcatori temporali contribuisce alla costruzione della narrazione e all'efficacia comunicativa del testo.
✅ Risposta: Nel testo, i connettivi e i marcatori temporali ("Mercoledì", "a ottobre", "il 20 febbraio", "sabato 8 marzo", "lunedì sera") creano una chiara progressione cronologica che permette al lettore di seguire l'evoluzione degli eventi in modo lineare. Questa struttura temporale è fondamentale per comprendere il deteriorarsi della situazione, dal trasferimento iniziale del protagonista fino al suo allontanamento finale. I connettivi causali impliciti ed espliciti collegano le azioni alle loro conseguenze, evidenziando i rapporti di causa-effetto tra il comportamento intimidatorio, il divieto di avvicinamento, la sua violazione, l'arresto e infine l'allontanamento dal condominio. Questa rete di connessioni linguistiche crea coesione testuale e rende la narrazione fluida e comprensibile, permettendo al lettore di seguire facilmente lo sviluppo logico degli eventi e di cogliere le relazioni tra i fatti descritti.
"""


class FeedbackGenerator:
    """Class to generate feedback on student answers using Ollama."""

    def __init__(self, model_name="mistral"):
        """
        Initialize the feedback generator with an Ollama model.

        Args:
            model_name: Name of the Ollama model to use
        """
        self.model_name = model_name
        self.ollama_client = OllamaClient()

    def generate_feedback(
        self, question: str, correct_answer: str, student_answer: str
    ) -> str:
        """
        Generate feedback on a student's answer using Ollama.

        Args:
            question: The question that was asked
            correct_answer: The correct answer
            student_answer: The student's answer

        Returns:
            Feedback as a string
        """
        prompt = f"""Sei un assistente educativo che aiuta a fornire feedback sulle risposte degli studenti.

DOMANDA:
{question}

RISPOSTA CORRETTA:
{correct_answer}

RISPOSTA DELLO STUDENTE:
{student_answer}

ISTRUZIONI:
Fornisci un feedback costruttivo sulla risposta dello studente. Evidenzia ciò che è corretto e ciò che manca o è errato.
Il feedback deve essere educativo, incoraggiante e aiutare lo studente a migliorare la propria comprensione.
NB: Lo studente non vede la risposta corretta, quindi non può essere influenzato da questa.
"""

        # Check if Ollama is available
        if not self.ollama_client.is_available():
            # Fall back to example feedback if Ollama is not available
            return self._generate_example_feedback(
                question, correct_answer, student_answer
            )

        with st.spinner("Generating feedback using Ollama... This may take a moment."):
            # Generate feedback using Ollama
            feedback = self.ollama_client.generate(
                model=self.model_name, prompt=prompt, temperature=0.7, max_tokens=1024
            )

            if not feedback:
                return self._generate_example_feedback(
                    question, correct_answer, student_answer
                )

            return feedback

    def _generate_example_feedback(
        self, question: str, correct_answer: str, student_answer: str
    ) -> str:
        """Generate example feedback when Ollama is not available."""

        if student_answer.lower() == correct_answer.lower():
            return "Ottimo lavoro! La tua risposta è corretta e completa."
        elif any(
            word in student_answer.lower()
            for word in correct_answer.lower().split()[:3]
        ):
            return "La tua risposta contiene alcuni elementi corretti, ma non è completa. Hai identificato correttamente l'inizio, ma hai tralasciato alcuni dettagli importanti."
        else:
            return "La tua risposta non è corretta. Ti suggerisco di rileggere attentamente il testo, concentrandoti sugli elementi evidenziati nelle annotazioni."


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
                "correct_answer": ""
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
    """Streamlit application for Linda Test Evaluation."""

    def __init__(self):
        """Initialize the application."""
        self.pdf_extractor = PDFTextExtractor()
        self.annotation_processor = AnnotationProcessor()
        self.quiz_generator = QuizGenerator()
        self.feedback_generator = FeedbackGenerator()
        self.ollama_client = OllamaClient()
        
    def validate_question(self, question, text, annotations, tag_type):
        """
        Validate if the answer to a question aligns with the text and annotations.
        
        Args:
            question: The structured question with answer
            text: The original text
            annotations: The annotations dictionary
            tag_type: The type of annotations used
            
        Returns:
            Dictionary with validation results
        """
        model_name = st.session_state.get("model_name", "mistral")
        
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
{self._format_annotations(annotations)}

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
{self._format_annotations(annotations)}

DOMANDA:
{question["text"]}

RISPOSTA FORNITA:
{question["correct_answer"]}

Valuta la risposta. Rispondi in questo formato:
VALIDA: [Sì/No]
SUGGERIMENTO: [Il tuo suggerimento se necessario, o "La risposta è corretta" se adeguata]
MOTIVAZIONE: [Breve spiegazione]
"""
        
        # Get validation from Ollama
        validation_response = self.ollama_client.generate(
            model=model_name, 
            prompt=validation_prompt, 
            temperature=0.3,
            max_tokens=512  # Keep response size reasonable
        )
        
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
            "motivation": motivation,
            "full_response": validation_response,
            "timestamp": time.time()  # For caching purposes
        }

    def _format_annotations(self, annotations):
        """Format annotations for prompt."""
        return "\n".join([f"- {tag}: {', '.join(items)}" for tag, items in annotations.items()])
        
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
                            if st.button("Validate All"):
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
                            if st.button("Save Without Validation"):
                                # Format the edited quiz back to text
                                updated_quiz = format_structured_quiz(edited_quiz)
                                st.session_state["quiz"] = updated_quiz
                                st.session_state["structured_quiz"] = edited_quiz
                                st.session_state["editing_quiz"] = False
                                st.success("Quiz saved without validation!")
                                st.rerun()
                    else:
                        # Format the edited quiz back to text
                        updated_quiz = format_structured_quiz(edited_quiz)
                        st.session_state["quiz"] = updated_quiz
                        st.session_state["structured_quiz"] = edited_quiz
                        st.session_state["editing_quiz"] = False
                        st.success("Quiz saved successfully!")
                        st.rerun()
            with cols[2]:
                if st.button("Cancel"):
                    st.session_state["editing_quiz"] = False
                    st.rerun()
        
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
                
                # Display validation result if available
                if "validation_results" in st.session_state and i in st.session_state["validation_results"]:
                    result = st.session_state["validation_results"][i]
                    if result["is_valid"]:
                        st.success("✓ AI confirms: Answer aligns with the text")
                    else:
                        st.warning(f"⚠️ AI suggests: {result['suggestion']}")
                        # Replace the expander with a checkbox toggle
                        show_reasoning = st.checkbox(f"🔍 Show AI Reasoning for Q{question['number']}", key=f"reasoning_{i}")
                        if show_reasoning:
                            st.markdown("**AI Reasoning:**")
                            st.markdown(result["motivation"])
                
                # Question removal
                if st.button(f"Delete Question {question['number']}", key=f"del_q_{i}"):
                    del edited_quiz[i]
                    # Also remove validation result if exists
                    if "validation_results" in st.session_state and i in st.session_state["validation_results"]:
                        del st.session_state["validation_results"][i]
                    edited = True
                    st.rerun()
        
        # Add a new question
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
            
            # Update session state and refresh
            st.session_state["structured_quiz"] = edited_quiz
            st.rerun()
        
        # Validate All Questions button
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
        
        # Preview the edited quiz
        st.subheader("Quiz Preview")
        preview = format_structured_quiz(edited_quiz)
        st.markdown(preview)

    def run(self):
        """Run the Streamlit application."""
        st.title("Linda Test Eval - Quiz Generator")
        st.markdown("### Upload annotated text and generate comprehension quizzes")

        # Dynamic status message showing current Ollama status and selected model
        ollama_client = OllamaClient()
        current_model = st.session_state.get("model_name", "mistral")
        
        if ollama_client.is_available():
            st.success(f"Ollama server is available. Using model: {current_model}")
        else:
            st.error("❌ Ollama server is not available")

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

            # Ollama model selection
            st.subheader("Ollama Settings")
            model_name = st.selectbox(
                "Select Ollama Model",
                ["mistral", "phi3:mini", "gemma3:1b", "gemma3:4b"],
                index=0,
            )
            # Store the selected model in session state
            st.session_state["model_name"] = model_name

            # Update model settings
            if st.button("Update Model"):
                self.quiz_generator = QuizGenerator(model_name)
                self.feedback_generator = FeedbackGenerator(model_name)
                st.success(f"Model updated to {model_name}")

            st.header("About")
            st.info(
                "This tool helps teachers create comprehension quizzes based on "
                "annotated texts. Upload a PDF and the corresponding annotations CSV "
                "to generate quizzes for your students.\n\n"
                "This version uses Ollama to run models locally."
            )

            # Ollama status
            ollama_client = OllamaClient()
            if ollama_client.is_available():
                st.success("✅ Ollama is running")
            else:
                st.error("❌ Ollama is not available")
                st.markdown(
                    """
                To install Ollama:
                1. Visit [ollama.ai/download](https://ollama.ai/download)
                2. After installation, run:
                ```
                ollama pull mistral
                ollama serve
                ```
                """
                )

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
                model_name = st.session_state.get("model_name", "mistral")
                self.quiz_generator = QuizGenerator(model_name)

                # Log which model is being used
                st.info(f"Using model: {model_name} for quiz generation")

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

            # Student answer and feedback section
            st.header("Test Student Answer")
            st.markdown(
                "#### Enter a student answer to see feedback: domanda a risposta aperta"
            )

            question = st.text_area(
                "Question",
                "",
            )
            correct_answer = st.text_area(
                "Correct Answer",
                "",
            )
            student_answer = st.text_area("Student Answer", "")

            if st.button("Generate Feedback") and student_answer:
                # Update feedback generator with current model settings
                model_name = st.session_state.get("model_name", "mistral")
                self.feedback_generator = FeedbackGenerator(model_name)

                # Log which model is being used
                st.info(f"Using model: {model_name} for feedback generation")

                feedback = self.feedback_generator.generate_feedback(
                    question, correct_answer, student_answer
                )
                st.info(feedback)


def main():
    """Main function to run the application."""
    app = LindaTestEvalApp()
    app.run()


if __name__ == "__main__":
    main()
