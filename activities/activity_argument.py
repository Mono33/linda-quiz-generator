"""Argument Activity (Testo Argomentativo): Quiz and Feedback Generators (Generic prompts - to be customized)."""

from typing import Dict, List
from core.openrouter_client import OpenRouterClient
import streamlit as st


class QuizGeneratorArgument:
    """Quiz generator for Argument annotations with language detection."""

    def __init__(self, model_name="mistralai/mistral-7b-instruct"):
        """Initialize the Argument quiz generator."""
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
        """Get language-specific instructions for Argument quiz generation."""
        if detected_lang == 'en':
            return {
                "task_instruction": "Create a comprehension quiz in ENGLISH that assesses understanding of arguments and reasoning in the text.",
                "language_rules": """LANGUAGE RULE:
- Generate the quiz in ENGLISH (matching the input text language).
- Keep structural labels in Italian: "[Scelta Multipla]", "[Risposta Aperta]", "✅ Risposta corretta:", "✅ Risposta:"
- Everything else (questions, options) must be in ENGLISH."""
            }
        else:
            return {
                "task_instruction": "Crea un quiz di comprensione in italiano che valuti la comprensione degli argomenti e del ragionamento nel testo.",
                "language_rules": """Ruolo lingua:
- Il quiz deve essere generato in italiano (lingua del testo).
- Mantieni le etichette strutturali: "[Scelta Multipla]", "[Risposta Aperta]", "✅ Risposta corretta:", "✅ Risposta:"
- Tutto il resto deve essere nella lingua del testo."""
            }

    def generate_quiz(self, text: str, annotations: Dict[str, List[str]]) -> str:
        """Generate an Argument quiz (GENERIC - to be customized)."""
        if not self.openrouter_client.is_available():
            return "OpenRouter API non disponibile."

        detected_lang = self.detect_text_language(text)
        lang_instructions = self._get_language_instructions(detected_lang)
        
        annotation_examples = "\n".join(
            [f"- {tag}: {', '.join(items)}" for tag, items in annotations.items()]
        )

        prompt = f"""Sei un assistente educativo esperto nell'analisi del TESTO ARGOMENTATIVO secondo i criteri della didattica italiana.

Il testo argomentativo è un tipo di testo in cui l'autore presenta una TESI e la sostiene con ARGOMENTI, prove ed esempi, 
eventualmente considerando CONTROARGOMENTAZIONI per poi confutarle o riconoscerle.

TESTO DA ANALIZZARE:
{text}

ANNOTAZIONI IDENTIFICATE (elementi argomentativi):
{annotation_examples}

---
OBIETTIVO DIDATTICO:
{lang_instructions["task_instruction"]} 

Il quiz deve valutare la capacità dello studente di:
- Identificare la TESI (posizione/opinione dell'autore) o l'ANTITESI (posizione opposta)
- Riconoscere gli ARGOMENTI a sostegno della tesi o dell'antitesi (causa, analogia, esempio, dato, citazione)
- Distinguere tra ARGOMENTI a favore e CONTROARGOMENTI (argomenti che confutano)
- Comprendere la STRUTTURA LOGICA del testo (tesi → argomenti → controargomenti → conclusione)
- Valutare la FORZA e l'EFFICACIA degli argomenti e delle prove presentate

---
STRUTTURA RICHIESTA DEL QUIZ:

Genera esattamente 3 domande basate sulle annotazioni fornite:

1. **DOMANDA 1 - [Scelta Multipla] - IDENTIFICAZIONE TESI/ANTITESI**
   Testa la capacità di identificare:
   - La TESI principale dell'autore (esplicita o implicita), OPPURE
   - L'ANTITESI (tesi opposta) presente nel testo, OPPURE
   - La tipologia della tesi (descrittiva/prescrittiva/valutativa), OPPURE
   - La distinzione tra TESI e ARGOMENTI che la sostengono
   
   Usa le annotazioni per costruire opzioni plausibili ma solo UNA corretta.

2. **DOMANDA 2 - [Scelta Multipla] - ARGOMENTI E STRUTTURA LOGICA**
   Testa la comprensione di:
   - Il TIPO di argomento utilizzato (causa, sintomo, analogia, esempio, dato, citazione autorevole), OPPURE
   - Il RUOLO di un elemento specifico (argomento a favore, controargomento, esempio, prova), OPPURE
   - Come un CONTROARGOMENTO viene usato (per supportare l'antitesi O per rafforzare la tesi anticipando obiezioni), OPPURE
   - La CONNESSIONE LOGICA tra argomenti e tesi (come gli argomenti si collegano e si rafforzano reciprocamente)
   
   Includi distrattori che sembrano plausibili ma sono logicamente scorretti.

3. **DOMANDA 3 - [Risposta Aperta] - VALUTAZIONE E ANALISI CRITICA**
   Richiedi allo studente di:
   - Valutare la FORZA/EFFICACIA di un argomento specifico E spiegare perché (con riferimento al testo e alle annotazioni), OPPURE
   - Confrontare due argomenti e identificare quale è più CONVINCENTE, giustificando la scelta con prove testuali, OPPURE
   - Spiegare come una PROVA/ESEMPIO/DATO specifico sostiene o indebolisce la tesi, OPPURE
   - Valutare se un CONTROARGOMENTO confuta efficacemente la tesi opposta O rafforza la tesi anticipando obiezioni, OPPURE
   - Analizzare la STRUTTURA complessiva (tesi → argomenti → controargomenti → conclusione) e valutarne la coerenza
   
   La risposta deve richiedere pensiero critico SUPPORTATO DA GIUSTIFICAZIONE basata su elementi trovabili nel testo, non solo opinione personale.

---
FORMATO DI OUTPUT RICHIESTO:

1. [Scelta Multipla] Testo della domanda?
   - A) Opzione A
   - B) Opzione B
   - C) Opzione C
   - D) Opzione D
   
   ✅ Risposta corretta: [lettera]

2. [Scelta Multipla] Testo della domanda?
   - A) Opzione A
   - B) Opzione B
   - C) Opzione C
   - D) Opzione D
   
   ✅ Risposta corretta: [lettera]

3. [Risposta Aperta] Testo della domanda?
   
   ✅ Risposta: [risposta modello dettagliata che dimostri comprensione profonda]

---
REGOLE IMPORTANTI:

✅ OGNI domanda DEVE riferirsi esplicitamente alle annotazioni fornite
✅ Le domande devono testare COMPRENSIONE, non solo memoria
✅ Per le scelte multiple: opzioni plausibili, UNA SOLA corretta, evita opzioni ovviamente sbagliate
✅ Per la risposta aperta: richiedi GIUSTIFICAZIONE e RAGIONAMENTO, non solo identificazione
✅ NON aggiungere titoli, introduzioni, spiegazioni extra o commenti al di fuori del formato richiesto
✅ NON numerare le opzioni delle domande a scelta multipla (usa solo A, B, C, D)

⚠️ VARIAZIONE E DINAMICITÀ:
- Le domande devono essere ORIGINALI e DINAMICHE ad ogni generazione
- Anche usando le stesse annotazioni, VARIA l'angolo di analisi:
  * Per TESI/ANTITESI: alterna tra identificazione diretta, tipologia, distinzione da argomenti
  * Per ARGOMENTI: alterna tra tipo, ruolo, connessione logica, forza
  * Per CONTROARGOMENTI: alterna tra funzione (confuta antitesi vs rafforza tesi), efficacia
- ESPLORA aspetti diversi delle stesse annotazioni in generazioni successive
- EVITA di formulare sempre la stessa domanda per la stessa annotazione

{lang_instructions["language_rules"]}
"""

        return self.openrouter_client.generate(
            model=self.model_name,
            prompt=prompt,
            temperature=0.7,
            max_tokens=2048
        )


class FeedbackGeneratorArgument:
    """Feedback generator for Argument activity (GENERIC - to be customized)."""

    def __init__(self, model_name="mistralai/mistral-7b-instruct"):
        """Initialize the Argument feedback generator."""
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
        """Generate feedback for open-ended questions with annotation support (Argumentative text)."""
        formatted_annotations = self._format_annotations(annotations)
        text_context = original_text[:500] + "..." if original_text and len(original_text) > 500 else original_text or ""
        
        prompt = f"""Sei un tutor educativo che fornisce feedback basato su testi argomentativi annotati. Il tuo obiettivo è guidare lo studente verso una comprensione più precisa della struttura argomentativa attraverso riferimenti specifici al testo e alle annotazioni (TESI, ANTITESI, ARGOMENTI, CONTROARGOMENTI). Rispondi SOLO in italiano.

CONTESTO:
- Testo argomentativo annotato con elementi specifici identificati (Tesi, Antitesi, Argomenti, Controargomenti, Conclusione)
- Domanda di comprensione che richiede analisi della struttura argomentativa
- Annotazioni di riferimento disponibili per guidare la comprensione
- CORRECT ANSWER (modello) di riferimento e STUDENT ANSWER (da valutare)

DOMANDA: {question}

RISPOSTA ATTESA (modello): {correct_answer}

RISPOSTA DELLO STUDENTE (da valutare): {student_answer}

ANNOTAZIONI DI RIFERIMENTO (Argomenti):
{formatted_annotations}

CONTESTO TESTUALE (estratto): 
{text_context}

ISTRUZIONI DI OUTPUT (OBBLIGATORIE):
- Produci ESATTAMENTE tre sezioni con i seguenti titoli (usa questi titoli e nessun altro).
- In ogni sezione scrivi frasi brevi (max 3 o 4 frasi). Totale massimo ~120 parole.
- Fai SEMPRE riferimento a un'annotazione specifica (Tesi, Antitesi, Argomento, Controargomento) e, se utile, cita al massimo UNA breve citazione dal testo (≤15 parole) tra virgolette.
- Non confondere mai la STUDENT ANSWER con la CORRECT ANSWER. Valuti SOLO la STUDENT ANSWER, citandola come tale.
- Se la STUDENT ANSWER è vuota, fuori tema o < 5 parole, segnala brevemente la criticità e fornisci un micro-passo per riprovare (rimandando al testo/annotazione).
- Valuta se lo studente ha compreso: la tesi/antitesi, la forza degli argomenti, la funzione dei controargomenti, le prove a sostegno.
- Se la risposta è errata o parziale, identifica e menziona il tipo di errore:
  * Errore logico: ragionamento fallace o contraddizioni (es. trarre una conclusione non supportata dalle evidenze, confondere causa ed effetto)
  * Errore di contenuto: inesattezza fattuale o omissione di informazioni chiave presenti nel testo
  * Errore di interpretazione: fraintendimento del significato, ruolo o funzione di una parte del testo (es. confondere la tesi con un argomento, non riconoscere un'antitesi, fraintendere la funzione di un controargomento)
  * Errore di pertinenza: risposta fuori tema o che non risponde alla domanda
  * Problema di espressione: formulazione poco chiara o organizzazione confusa che ostacola la comprensione
- Mantieni tono professionale, incoraggiante ma non necessariamente entusiasta. 
- Linguaggio conciso, corretto e privo di errori grammaticali.
- Inizia sempre con il positivo.
- Non aggiungere testo prima/dopo le tre sezioni. Nessuna firma, nessuna spiegazione extra.

**☀️ ASPETTI POSITIVI:**
[Conferma uno o due elementi corretti presenti nella STUDENT ANSWER; se parziali, dillo. Indica l'annotazione pertinente (Tesi, Argomento, Controargomento, ecc.) e, se utile, una breve citazione. Se lo studente ha riconosciuto correttamente la tesi o un argomento, riconoscilo esplicitamente.]

**🎯 SUGGERIMENTO PER MIGLIORARE:**
[Se presente un errore, identificalo brevemente specificando il tipo (es. "Errore di interpretazione: hai confuso un argomento di supporto con la tesi principale"). Poi fornisci un solo suggerimento chiaro e operativo per migliorare la comprensione argomentativa, collegato a una parte precisa del testo o a un'annotazione specifica (nomina il tag, es. "Tesi: …", "Argomento di tipo causa: …", "Controargomento: …"). Indica dove rileggere per cogliere la struttura argomentativa.]

**🤔 DOMANDA METACOGNITIVA:**
[Una sola domanda breve che stimoli il ragionamento critico sulla struttura argomentativa, rimandando a una sezione del testo o a un'annotazione; es.: "Rileggi l'argomento '…' (tipo: causa). In che modo questo rafforza la tesi dell'autore?" oppure "Il controargomento citato confuta l'antitesi o anticipa obiezioni alla tesi? Perché?"]

FEEDBACK:"""

        return self.openrouter_client.generate(model=self.model_name, prompt=prompt, temperature=0.7, max_tokens=1024)

    def _generate_mc_feedback(self, question: str, correct_answer: str, student_answer: str,
                               options: List[Dict[str, str]] = None, annotations: Dict[str, List[str]] = None, 
                               original_text: str = None) -> str:
        """Generate feedback for multiple choice questions with annotation support (Argumentative text)."""
        formatted_options = "\n".join([f"{opt['letter']}) {opt['text']}" for opt in options]) if options else ""
        formatted_annotations = self._format_annotations(annotations)
        text_context = original_text[:500] + "..." if original_text and len(original_text) > 500 else original_text or ""
        
        correct_text = next((opt["text"] for opt in options if opt["letter"] == correct_answer), "") if options else ""
        student_text = next((opt["text"] for opt in options if opt["letter"] == student_answer), "") if options else ""
        
        prompt = f"""Sei un tutor educativo che fornisce feedback per domande a scelta multipla basate su testi argomentativi annotati. Il tuo obiettivo è chiarire incomprensioni sulla struttura argomentativa rimandando con precisione alle annotazioni (TESI, ANTITESI, ARGOMENTI, CONTROARGOMENTI) e al testo.

DOMANDA: {question}

OPZIONI:
{formatted_options}

RISPOSTA CORRETTA: {correct_answer}) {correct_text}
RISPOSTA DELLO STUDENTE: {student_answer}) {student_text}

ANNOTAZIONI DI RIFERIMENTO (Argomenti):
{formatted_annotations}

CONTESTO TESTUALE:
{text_context}

ISTRUZIONI OPERATIVE (seguile alla lettera):
- Se la risposta dello studente è CORRETTA: scrivi UNA sola frase di conferma + un riferimento all'annotazione o al testo che supporta la risposta corretta (es.: riferimento alla tesi, a un argomento specifico, a un controargomento). Non aggiungere altro.
- Se la risposta è SBAGLIATA: produci le tre sezioni sottostanti.
- Non confondere mai STUDENT ANSWER e CORRECT ANSWER: nominale sempre esplicitamente quale stai commentando.
- Fai SEMPRE un riferimento concreto alle annotazioni argomenti e/o al testo: o 1 breve citazione tra virgolette (≤ 8 parole) o una parafrasi puntuale + il tag annotazione (Tesi, Argomento, Controargomento, ecc.).
- Se nessuna annotazione è pertinente, dichiaralo e usa il passaggio del testo più vicino.
- Spiega l'errore specificando il tipo:
  * Errore di interpretazione: confusione tesi/antitesi, fraintendimento del tipo di argomento (causa/analogia/esempio), incomprensione della funzione del controargomento (supporta antitesi o rafforza tesi)
  * Errore di contenuto: informazione fattuale errata o omissione di elementi chiave del testo
  * Errore logico: conclusione non supportata dalle evidenze testuali, ragionamento fallace
  * Errore di pertinenza: scelta di un'opzione non pertinente alla domanda
- Italiano chiaro, tono professionale e incoraggiante. Niente emoji extra oltre alle intestazioni richieste. Max 2–3 frasi per sezione.

FORMATO DA RISPETTARE ESATTAMENTE:

[Se CORRETTA → una riga]
✅ Corretto: [breve conferma + 1 riferimento all'annotazione argomentativa pertinente (Tesi/Argomento/Controargomento) o citazione dal testo]

[Se SBAGLIATA → le tre sezioni seguenti]

**☀️ RICONOSCIMENTO:**
[Riconosci sinteticamente l'impegno o la logica nella STUDENT ANSWER, se pertinente. Se lo studente ha parzialmente compreso un elemento della struttura argomentativa (es.: ha identificato un argomento ma non la tesi), riconoscilo. 1 frase.]

**🎯 CHIARIMENTO:**
[Identifica il tipo di errore (es.: "Errore di interpretazione:", "Errore di contenuto:", "Errore logico:") e spiega in modo conciso perché la CORRECT ANSWER è giusta in termini di struttura argomentativa (es.: "La risposta B identifica correttamente la tesi prescrittiva, mentre la tua scelta confonde un argomento di supporto con la tesi principale"). Cita o parafrasa 1 elemento del testo e richiama l'annotazione pertinente (Tesi, Argomento tipo causa/analogia/esempio, Controargomento). 1 o 2 frasi.]

**📍 RIFERIMENTO TESTUALE:**
[Indica dove trovare l'elemento corretto: "Vedi [citazione ≤8 parole] / vedi annotazione Tesi/Argomento/Controargomento su …". Se applicabile, suggerisci di rileggere la struttura: tesi → argomenti → controargomenti → conclusione. 1 frase.]

VINCOLI:
- Niente contenuti non presenti nel testo/annotazioni.
- Non elencare di nuovo tutte le opzioni.
- Se la scelta dello studente è vuota o non A,B,C oppure D, scrivi: "Risposta non valida: seleziona A,B,C oppure D" e chiudi.
- Usa terminologia corretta: TESI/ANTITESI, ARGOMENTO (causa/sintomo/analogia/esempio/dato/citazione), CONTROARGOMENTO (supporta antitesi o rafforza tesi).

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


