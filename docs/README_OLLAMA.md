# Linda Test Eval - Quiz Generator (Ollama Version)

Una versione ottimizzata della Linda Test Eval che utilizza Ollama per eseguire modelli di linguaggio localmente.

## Panoramica

Linda Test Eval (versione Ollama) aiuta gli insegnanti a creare quiz di comprensione basati su testi annotati. Il sistema può:

1. Estrarre testo da documenti PDF
2. Elaborare dati di annotazione (es. tag 5W: Chi, Cosa, Quando, Dove, Perché)
3. Generare quiz di comprensione con domande a scelta multipla e a risposta aperta
4. Fornire feedback automatizzato sulle risposte degli studenti

A differenza della versione originale che utilizza Hugging Face Transformers, questa versione sfrutta Ollama per eseguire modelli di linguaggio localmente, offrendo una soluzione più efficiente e flessibile.

## Vantaggi dell'uso di Ollama

- **Efficienza delle risorse**: Ollama gestisce automaticamente la quantizzazione dei modelli
- **Facilità d'uso**: API semplificata per l'integrazione dei modelli
- **Flessibilità**: Possibilità di cambiare facilmente tra diversi modelli (Mistral, LLaMA, Gemma, etc.)
- **Prestazioni**: Ottimizzazioni specifiche per l'hardware locale
- **Riservatezza dei dati**: I dati vengono elaborati localmente senza dover essere inviati a servizi esterni

## Requisiti

- Python 3.9 o superiore
- [Ollama](https://ollama.ai/download) installato e configurato

## Installazione

1. Clona questo repository:
```bash
git clone <repository-url>
cd linda-test-eval
```

2. Installa Ollama seguendo le istruzioni su [ollama.ai/download](https://ollama.ai/download)

3. Scarica il modello Mistral o altro modello desiderato:
```bash
ollama pull mistral
```

4. Installa le dipendenze Python:
```bash
pip install -r requirements_ollama.txt
```

## Utilizzo

1. Avvia il server Ollama:
```bash
ollama serve
```

2. In un terminale separato, avvia l'applicazione Streamlit:
```bash
streamlit run linda_test_eval2.py
```

3. Utilizza l'interfaccia web per:
   - Caricare un file PDF contenente il testo
   - Caricare un file CSV contenente le annotazioni
   - Selezionare il tipo di tag (es. 5W, Tesi, Argomento)
   - Scegliere il modello Ollama da utilizzare
   - Generare e scaricare quiz
   - Testare le risposte degli studenti e ottenere feedback

### Modelli supportati

L'applicazione supporta vari modelli disponibili tramite Ollama:
- mistral (predefinito)
- mistral:7b
- llama3
- llama3:8b
- gemma:7b

Per utilizzare un modello specifico, assicurati di averlo scaricato con `ollama pull <model-name>` prima di selezionarlo nell'interfaccia.

### Formato dei file di input

#### Testo PDF
Qualsiasi documento PDF contenente testo che può essere estratto.

#### Annotazioni CSV
Un file CSV con le seguenti colonne:
- `code`: Il codice della categoria (es. WHO, WHAT, WHEN)
- `title`: Il titolo della categoria (spesso uguale al codice)
- `begin`: Posizione iniziale dell'annotazione nel testo
- `end`: Posizione finale dell'annotazione nel testo
- `text`: Il contenuto testuale dell'annotazione

Esempio:
```
code,title,begin,end,text
WHO,WHO,7,8,Samardo Samuels
WHEN,WHEN,0,0,Mercoledì
WHERE,WHERE,13,15,condominio di Milano
...
```

## Modalità Fallback

Se Ollama non è disponibile o non riesce a generare una risposta, l'applicazione passerà automaticamente a una modalità di fallback che utilizza template predefiniti per generare quiz basati sulle annotazioni fornite.

## Personalizzazione

L'applicazione è progettata per essere facilmente personalizzabile:

- **Modelli di Linguaggio**: Cambia facilmente tra diversi modelli Ollama tramite l'interfaccia
- **Tipi di Tag**: Aggiungi o modifica i tipi di tag nell'interfaccia Streamlit
- **Formato del Quiz**: Personalizza i template dei prompt nel metodo `create_prompt` per modificare il formato del quiz

## Risoluzione dei problemi

Se riscontri problemi con Ollama:

1. Verifica che il server Ollama sia in esecuzione con `ollama serve`
2. Assicurati di aver scaricato il modello che stai cercando di utilizzare
3. Controlla i requisiti di sistema per il modello scelto
4. In caso di errori di memoria, prova a utilizzare un modello più piccolo o quantizzato

## Licenza

[MIT License](LICENSE) 




<!-- ISTRUZIONI:
Crea un quiz di comprensione in italiano basato sul testo e sulle annotazioni fornite. Il quiz deve includere:
1. Almeno 2 domande a scelta multipla (con 4 opzioni ciascuna)
2. Almeno 1 domanda a risposta aperta
3. Ogni domanda deve valutare la comprensione del testo e/o degli elementi linguistici identificati dalle annotazioni
4. Le domande devono essere diverse e adattate al contenuto specifico del testo e al tipo di annotazioni fornite ({tag_type})
5. Fornisci le risposte corrette per ogni domanda

Formato del quiz:
- Numero e tipo di domanda (es. "1. [Scelta Multipla]" o "2. [Risposta Aperta]")
- Testo della domanda
- Opzioni (per domande a scelta multipla) con il formato:
    - A) opzione A
    - B) opzione B
    - C) opzione C
    - D) opzione D

    È FONDAMENTALE che tu segua ESATTAMENTE questo formato per le opzioni, con i trattini, come indicato sopra.

- Risposta corretta indicata così:
  1) Per domande a scelta multipla (La risposta corretta deve comparire sempre subito dopo le opzioni, e non in mezzo al quiz):
  ✅ Risposta corretta: lettera corretta (cioè , solo la lettera della risposta corretta non devi riscrivere tutto il testo)
   
  2) Per domande a risposta aperta:
  ✅ Risposta: inserire testo della risposta corretta


NON usare un modello fisso di domande. Crea domande originali che si adattano specificamente al testo fornito.
NON aggiungere spiegazioni o commenti extra al quiz. -->


<!-- - Risposta corretta (per tutte le domande, preceduta da "✅ Risposta corretta: " per MCQ o "✅ Risposta: " per domande aperte) -->



<!-- ISTRUZIONI:
Crea un quiz di comprensione in italiano basato sul testo e sulle annotazioni fornite. Il quiz deve includere:
1. Almeno 2 domande a scelta multipla (MCQ) con 4 opzioni ciascuna
2. Almeno 1 domanda a risposta aperta
3. Ogni domanda deve valutare la comprensione del testo e/o degli elementi linguistici identificati nelle annotazioni
4. Le domande devono essere varie e specifiche rispetto al contenuto del testo e alle annotazioni

⚠️ SEGUI IL FORMATO QUI SOTTO PER OGNI DOMANDA

📌 **DOMANDE A SCELTA MULTIPLA**:
Scrivi nel formato esatto seguente, senza eccezioni:
[Numero]. [Scelta Multipla] Testo della domanda
- A) Testo opzione A
- B) Testo opzione B
- C) Testo opzione C
- D) Testo opzione D  
✅ Risposta corretta: lettera della risposta corretta (A, B, C o D)

Esempio valido:
1. [Scelta Multipla] Chi è il protagonista del testo?  
- A) Un calciatore italiano  
- B) Un arbitro di basket  
- C) Il personaggio principale  
- D) Un attore famoso  
✅ Risposta corretta: C

📌 **DOMANDE A RISPOSTA APERTA**:
[Numero]. [Risposta Aperta] Testo della domanda  
✅ Risposta: Testo della risposta corretta

⚠️ NON inserire mai la risposta corretta prima delle opzioni. Deve SEMPRE comparire dopo le opzioni.
⚠️ NON cambiare il formato dei trattini (-), degli spazi e delle lettere (A, B, C, D).
⚠️ NON scrivere opzioni su una sola riga. Ogni opzione DEVE essere su una riga distinta.

NON aggiungere spiegazioni o commenti. NON ripetere il testo o le istruzioni. Scrivi solo il quiz. -->




<!-- ISTRUZIONI:
Crea un quiz di comprensione in italiano basato sul testo e sulle annotazioni fornite. Il quiz deve includere:
1. Almeno 2 domande a scelta multipla (con 4 opzioni ciascuna)
2. Almeno 1 domanda a risposta aperta
3. Ogni domanda deve valutare la comprensione del testo e/o degli elementi linguistici identificati dalle annotazioni
4. Le domande devono essere diverse e adattate al contenuto specifico del testo e al tipo di annotazioni fornite ({tag_type})
5. Fornisci le risposte corrette per ogni domanda

Formato del quiz:
- Numero e tipo di domanda (es. "1. [Scelta Multipla]" o "2. [Risposta Aperta]")
- Testo della domanda 
- Opzioni (solo per domande a scelta multipla) - presentate una per riga, come nel formato seguente:

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
NON aggiungere spiegazioni o commenti extra al quiz. -->
