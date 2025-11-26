"""
Linda - AI Assessment Educational Platform
Main application orchestrator with modular activity support.
"""

import os
import streamlit as st
import tempfile
import json
import time
import re
from typing import Dict, List, Any
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

# Import core components
from core import (
    PDFTextExtractor,
    AnnotationProcessor,
    OpenRouterClient,
    parse_quiz_text,
    format_structured_quiz,
    QuizExporter
)

# Import activity modules
from activities import (
    QuizGenerator5W, FeedbackGenerator5W,
    QuizGeneratorThesis, FeedbackGeneratorThesis,
    QuizGeneratorArgument, FeedbackGeneratorArgument,
    QuizGeneratorConnective, FeedbackGeneratorConnective
)


# Activity registry mapping tag types to their generators
ACTIVITY_REGISTRY = {
    "5W": {
        "quiz_generator_class": QuizGenerator5W,
        "feedback_generator_class": FeedbackGenerator5W
    },
    "Thesis": {
        "quiz_generator_class": QuizGeneratorThesis,
        "feedback_generator_class": FeedbackGeneratorThesis
    },
    "Argument": {
        "quiz_generator_class": QuizGeneratorArgument,
        "feedback_generator_class": FeedbackGeneratorArgument
    },
    "Connective": {
        "quiz_generator_class": QuizGeneratorConnective,
        "feedback_generator_class": FeedbackGeneratorConnective
    }
}

# Mapping between display names (user-facing) and internal identifiers
TAG_TYPE_DISPLAY_TO_INTERNAL = {
    "5W": "5W",
    "Argumentative Essay": "Argument",  # Display name → Internal identifier
    "Thesis": "Thesis",
    "Connective": "Connective"
}

# Reverse mapping for internal → display
TAG_TYPE_INTERNAL_TO_DISPLAY = {v: k for k, v in TAG_TYPE_DISPLAY_TO_INTERNAL.items()}


class LindaMainApp:
    """Main application orchestrator with dynamic activity loading."""

    def __init__(self):
        """Initialize the application."""
        st.set_page_config(
            page_title="Linda - AI Assessment Educational Platform",
            page_icon="📚",
            layout="wide"
        )
        
        # Initialize core components
        self.pdf_extractor = PDFTextExtractor()
        self.annotation_processor = AnnotationProcessor()
        self.quiz_exporter = QuizExporter()
        
        # Activity generators will be loaded dynamically based on tag selection
        self.quiz_generator = None
        self.feedback_generator = None
    
    @staticmethod
    def get_clean_filename(tag_type: str) -> str:
        """Convert tag type to clean filename format (lowercase with underscores)."""
        # Get display name if internal identifier is passed
        display_name = TAG_TYPE_INTERNAL_TO_DISPLAY.get(tag_type, tag_type)
        # Convert to lowercase and replace spaces with underscores
        return display_name.lower().replace(' ', '_')

    def _load_activity_generators(self, tag_type: str, model_name: str):
        """
        Dynamically load quiz and feedback generators for the selected activity.
        
        Args:
            tag_type: The type of activity/tag (5W, Thesis, Argument, Connective)
            model_name: The OpenRouter model to use
        """
        if tag_type in ACTIVITY_REGISTRY:
            activity = ACTIVITY_REGISTRY[tag_type]
            self.quiz_generator = activity["quiz_generator_class"](model_name)
            self.feedback_generator = activity["feedback_generator_class"](model_name)
        else:
            st.error(f"Unknown activity type: {tag_type}")
            # Fallback to 5W
            self.quiz_generator = QuizGenerator5W(model_name)
            self.feedback_generator = FeedbackGenerator5W(model_name)

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
{text[:3000]}

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
{text[:3000]}

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
            max_tokens=512
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
        
        # Create backup of original quiz when first entering editor (if not already backed up)
        if st.session_state.get("original_quiz_backup") is None:
            import copy
            st.session_state["original_quiz_backup"] = copy.deepcopy(st.session_state["structured_quiz"])
        
        edited = False
        edited_quiz = st.session_state["structured_quiz"].copy()
        
        # Settings for validation
        with st.sidebar:
            st.subheader("Validation Settings")
            auto_validate = st.checkbox("Enable automatic validation", 
                                       value=st.session_state.get("auto_validate", False),
                                       help="When enabled, questions will be automatically validated when answers change")
            st.session_state["auto_validate"] = auto_validate
        
        # Display validation summary if available (BEFORE Save Changes button)
        if "validation_summary" in st.session_state:
            summary = st.session_state["validation_summary"]
            total = summary["total"]
            valid = summary["valid"]
            invalid = summary["invalid"]
            
            if invalid == 0:
                st.success(f"✅ **Validation Complete:** All {total} questions are valid!")
            else:
                st.warning(f"⚠️ **Validation Complete:** {valid}/{total} valid, {invalid} need{'s' if invalid == 1 else ''} attention")
            
            # Clear summary button
            if st.button("Dismiss Summary", key="dismiss_summary_btn"):
                st.session_state.pop("validation_summary", None)
                st.rerun()
        
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
                                valid_count = 0
                                invalid_count = 0
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
                                            
                                            # Count valid/invalid
                                            if result["is_valid"]:
                                                valid_count += 1
                                            else:
                                                invalid_count += 1
                                
                                # Store summary for display
                                total_validated = valid_count + invalid_count
                                st.session_state["validation_summary"] = {
                                    "total": total_validated,
                                    "valid": valid_count,
                                    "invalid": invalid_count
                                }
                                st.rerun()
                        with col2:
                            if st.button("Save Without Validation", key="save_wo_val_btn"):
                                # Renumber before saving
                                for idx, q in enumerate(edited_quiz):
                                    q["number"] = idx + 1
                                updated_quiz = format_structured_quiz(edited_quiz)
                                st.session_state["quiz"] = updated_quiz
                                st.session_state["structured_quiz"] = edited_quiz
                                st.session_state["has_edited_quiz"] = True
                                st.session_state["edited_at"] = time.strftime("%H:%M")
                                st.session_state["editing_quiz"] = False
                                st.session_state["original_quiz_backup"] = None  # Clear backup
                                st.session_state.pop("validation_summary", None)  # Clear summary
                                st.success("Quiz saved without validation!")
                                st.rerun()
                    else:
                        # All questions validated, save directly
                        for idx, q in enumerate(edited_quiz):
                            q["number"] = idx + 1
                        updated_quiz = format_structured_quiz(edited_quiz)
                        st.session_state["quiz"] = updated_quiz
                        st.session_state["structured_quiz"] = edited_quiz
                        st.session_state["has_edited_quiz"] = True
                        st.session_state["edited_at"] = time.strftime("%H:%M")
                        st.session_state["editing_quiz"] = False
                        st.session_state["original_quiz_backup"] = None  # Clear backup after successful save
                        st.session_state.pop("validation_summary", None)  # Clear summary
                        st.success("Quiz saved successfully!")
                        st.rerun()
            with cols[2]:
                if st.button("Back to Quiz", key="back_to_quiz_btn"):
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
                        st.session_state["original_quiz_backup"] = None  # Clear backup
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
                        st.session_state["original_quiz_backup"] = None  # Clear backup
                        st.success("Quiz saved.")
                        st.rerun()
                with b2:
                    if st.button("Discard Changes", key="confirm_discard"):
                        # Restore quiz from backup
                        if st.session_state.get("original_quiz_backup") is not None:
                            import copy
                            st.session_state["structured_quiz"] = copy.deepcopy(st.session_state["original_quiz_backup"])
                            st.session_state["quiz"] = format_structured_quiz(st.session_state["structured_quiz"])
                        st.session_state["confirm_back_unsaved"] = False
                        st.session_state["editing_quiz"] = False
                        st.session_state["original_quiz_backup"] = None  # Clear backup
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
                    
                    # Auto-validation
                    if (st.session_state.get("auto_validate") and correct != previous_answer and 
                        question["text"] != "New question text"):
                        with st.spinner("Validating answer..."):
                            validation_result = self.validate_question(
                                edited_quiz[i],
                                st.session_state["extracted_text"],
                                st.session_state["grouped_annotations"],
                                st.session_state["tag_type"]
                            )
                            
                            if "validation_results" not in st.session_state:
                                st.session_state["validation_results"] = {}
                            st.session_state["validation_results"][i] = validation_result
                            st.rerun()
                    
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
                    
                    # Auto-validate
                    if (st.session_state.get("auto_validate") and question["text"] != "New question text" and 
                        (abs(len(correct_answer) - len(previous_answer)) > 20 or 
                         (len(previous_answer) > 10 and not correct_answer.startswith(previous_answer[:10])))):
                        with st.spinner("Validating answer..."):
                            validation_result = self.validate_question(
                                edited_quiz[i],
                                st.session_state["extracted_text"],
                                st.session_state["grouped_annotations"],
                                st.session_state["tag_type"]
                            )
                            
                            if "validation_results" not in st.session_state:
                                st.session_state["validation_results"] = {}
                            st.session_state["validation_results"][i] = validation_result
                            st.rerun()
                
                # Validate button
                if question["text"] != "New question text":
                    if st.button(f"Validate Question {question['number']} with AI", key=f"validate_{i}"):
                        with st.spinner("Validating with AI..."):
                            validation_result = self.validate_question(
                                edited_quiz[i],
                                st.session_state["extracted_text"],
                                st.session_state["grouped_annotations"],
                                st.session_state["tag_type"]
                            )
                            
                            if "validation_results" not in st.session_state:
                                st.session_state["validation_results"] = {}
                            st.session_state["validation_results"][i] = validation_result
                            st.rerun()
                
                # Display validation results
                if "validation_results" in st.session_state and i in st.session_state["validation_results"]:
                    result = st.session_state["validation_results"][i]
                    if result["is_valid"]:
                        st.success("✓ AI confirms: Answer aligns with the text")
                    else:
                        st.warning(f"⚠️ AI suggests: {result['suggestion']}")
                        show_reasoning = st.checkbox(f"🔍 Show AI Reasoning for Q{question['number']}", key=f"reasoning_{i}")
                        if show_reasoning:
                            st.markdown("**AI Reasoning:**")
                            st.markdown(result["motivation"])
                
                # Delete button with confirmation
                confirm_flag_key = f"confirm_delete_{i}"
                if st.button(f"Delete Question {question['number']}", key=f"del_q_{i}"):
                    st.session_state[confirm_flag_key] = True

                if st.session_state.get(confirm_flag_key):
                    st.warning(f"Are you sure you want to delete question {question['number']}?")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("Yes, delete", key=f"yes_del_{i}"):
                            del edited_quiz[i]
                            for idx, q in enumerate(edited_quiz):
                                q["number"] = idx + 1
                            st.session_state["structured_quiz"] = edited_quiz
                            if "validation_results" in st.session_state:
                                st.session_state["validation_results"] = {
                                    new_idx: res for new_idx, res in enumerate([
                                        st.session_state["validation_results"].get(old_idx)
                                        for old_idx in sorted(st.session_state["validation_results"].keys())
                                    ]) if res is not None
                                }
                            st.session_state.pop(confirm_flag_key, None)
                            st.success("Question deleted.")
                            st.rerun()
                    with c2:
                        if st.button("No, keep it", key=f"no_del_{i}"):
                            st.session_state.pop(confirm_flag_key, None)
                            st.rerun()
        
        # Add new question
        if st.button("Add New Question"):
            new_num = max([q["number"] for q in edited_quiz], default=0) + 1
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
            for idx, q in enumerate(edited_quiz):
                q["number"] = idx + 1
            st.session_state["structured_quiz"] = edited_quiz
            st.rerun()
        
        # Validate all questions
        if edited_quiz and st.button("Validate All Questions with AI"):
            if "validation_results" not in st.session_state:
                st.session_state["validation_results"] = {}
            
            valid_count = 0
            invalid_count = 0
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
                        
                        # Count valid/invalid
                        if result["is_valid"]:
                            valid_count += 1
                        else:
                            invalid_count += 1
            
            # Store summary for display
            total_validated = valid_count + invalid_count
            st.session_state["validation_summary"] = {
                "total": total_validated,
                "valid": valid_count,
                "invalid": invalid_count
            }
            st.rerun()
        
        # Preview
        st.subheader("Quiz Preview")
        preview = format_structured_quiz(edited_quiz)
        st.markdown(preview)

    def run(self):
        """Run the Streamlit application."""
        st.title("Linda - AI Assessment Educational Platform")
        st.markdown("### Upload annotated text and generate comprehension quizzes")

        # Dynamic status - check for API key in all possible locations
        api_key = None
        try:
            if hasattr(st, 'secrets') and "OPENROUTER_API_KEY" in st.secrets:
                api_key = st.secrets["OPENROUTER_API_KEY"]
            else:
                api_key = os.getenv("OPENROUTER_API_KEY")
        except Exception:
            # If secrets aren't available, use environment variable
            api_key = os.getenv("OPENROUTER_API_KEY")
        
        current_model = st.session_state.get("model_name", "mistralai/mistral-7b-instruct")
        
        if api_key:
            openrouter_client = OpenRouterClient()
            if openrouter_client.is_available():
                st.success(f"OpenRouter API is available. Using model: {current_model}")
            else:
                st.error("❌ OpenRouter API is not available")
        else:
            st.error("❌ OpenRouter API key not found")

        # Initialize session state
        for key, default in [
            ("quiz", ""), ("editing_quiz", False), ("structured_quiz", []),
            ("extracted_text", ""), ("grouped_annotations", {}), ("use_example", False),
            ("tag_type", "5W"), ("uploaded_pdf_bytes", None), ("uploaded_annotations_bytes", None),
            ("model_name", "mistralai/mistral-7b-instruct"), ("original_quiz_backup", None)
        ]:
            if key not in st.session_state:
                st.session_state[key] = default
            
        # Show editor if editing
        if st.session_state.get("editing_quiz", False):
            self.show_quiz_editor()
            return

        # Sidebar configuration
        with st.sidebar:
            st.header("Configuration")
            
            # Get current display name (convert from internal if needed)
            current_internal = st.session_state.get("tag_type", "5W")
            current_display = TAG_TYPE_INTERNAL_TO_DISPLAY.get(current_internal, current_internal)
            display_options = list(TAG_TYPE_DISPLAY_TO_INTERNAL.keys())
            current_index = display_options.index(current_display) if current_display in display_options else 0
            
            # Show display names in dropdown
            tag_type_display = st.selectbox(
                "Tag Type", display_options, index=current_index
            )
            
            # Convert display name to internal identifier
            tag_type_internal = TAG_TYPE_DISPLAY_TO_INTERNAL[tag_type_display]
            st.session_state["tag_type"] = tag_type_internal

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
            
            # Get the current model from session state
            current_model = st.session_state.get("model_name", "mistralai/mistral-7b-instruct")
            
            # Find the index of the current model in the options list
            model_list = list(model_options.keys())
            try:
                current_index = model_list.index(current_model)
            except ValueError:
                current_index = 0  # Fallback to first option if not found
            
            model_name = st.selectbox(
                "Select OpenRouter Model",
                options=model_list,
                format_func=lambda x: model_options[x],
                index=current_index,
            )
            st.session_state["model_name"] = model_name

            # Update model button
            if st.button("Update Model"):
                # Load appropriate activity generators
                self._load_activity_generators(tag_type_internal, model_name)
                st.success(f"Model updated to {model_options[model_name]}")

            st.header("About")
            st.info(
                "This tool helps teachers create comprehension quizzes based on "
                "annotated texts. Upload a PDF and the corresponding annotations CSV "
                "to generate quizzes for your students."
            )

            # API Key status
            if api_key:
                st.success("✅ OpenRouter API Key found")
                masked_key = f"{api_key[:8]}...{api_key[-4:]}"
                st.info(f"🔐 Key: {masked_key}")
            else:
                st.error("❌ OpenRouter API Key not found")
                with st.expander("📋 Setup Instructions"):
                    st.markdown("""
                    **Get your API Key:**
                    1. Visit [openrouter.ai](https://openrouter.ai/)
                    2. Create an account
                    3. Generate an API key
                    
                    **Local Development - Create a `.env` file:**
                    ```
                    OPENROUTER_API_KEY=your_key_here
                    ```
                    
                    **Or set as environment variable (Windows PowerShell):**
                    ```
                    $env:OPENROUTER_API_KEY="your_key_here"
                    ```
                    
                    **Streamlit Cloud - Use Secrets:**
                    Add to your app settings: `OPENROUTER_API_KEY = "your_key_here"`
                    """)

        # File upload section
        st.header("Upload Files")
        col1, col2 = st.columns(2)

        with col1:
            uploaded_pdf = st.file_uploader("Upload PDF Text", type=["pdf"])
            if uploaded_pdf:
                # Clear cached data when new PDF is uploaded
                if st.session_state.get("uploaded_pdf_bytes") != uploaded_pdf.getvalue():
                    st.session_state["extracted_text"] = ""
                    st.session_state["grouped_annotations"] = {}
                    st.session_state["quiz"] = ""
                    st.session_state["structured_quiz"] = []
                st.session_state["uploaded_pdf_bytes"] = uploaded_pdf.getvalue()

        with col2:
            uploaded_annotations = st.file_uploader("Upload Annotations", type=["csv"])
            if uploaded_annotations:
                # Clear cached data when new annotations are uploaded
                if st.session_state.get("uploaded_annotations_bytes") != uploaded_annotations.getvalue():
                    st.session_state["extracted_text"] = ""
                    st.session_state["grouped_annotations"] = {}
                    st.session_state["quiz"] = ""
                    st.session_state["structured_quiz"] = []
                st.session_state["uploaded_annotations_bytes"] = uploaded_annotations.getvalue()

        # Example data option
        use_example = st.checkbox("Use example data", value=st.session_state.get("use_example", False))
        
        # Clear cache if switching between example data and uploaded data
        if use_example != st.session_state.get("use_example"):
            st.session_state["extracted_text"] = ""
            st.session_state["grouped_annotations"] = {}
            st.session_state["quiz"] = ""
            st.session_state["structured_quiz"] = []
        
        st.session_state["use_example"] = use_example

        # Process files
        text = st.session_state.get("extracted_text", "")
        grouped_annotations = st.session_state.get("grouped_annotations", {})
        
        if not text or not grouped_annotations:
            with st.spinner("Processing input files..."):
                if use_example:
                    pdf_path = "docs/example.pdf"
                    annotations_path = "docs/annotations.csv"

                    text = self.pdf_extractor.extract_text(pdf_path)
                    annotations_df = self.annotation_processor.load_annotations(annotations_path)
                elif uploaded_pdf and uploaded_annotations:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
                        temp_pdf.write(uploaded_pdf.getvalue())
                        pdf_path = temp_pdf.name

                    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_annotations:
                        temp_annotations.write(uploaded_annotations.getvalue())
                        annotations_path = temp_annotations.name

                    text = self.pdf_extractor.extract_text(pdf_path)
                    annotations_df = self.annotation_processor.load_annotations(annotations_path)

                    os.unlink(pdf_path)
                    os.unlink(annotations_path)
                    
                elif st.session_state.get("uploaded_pdf_bytes") and st.session_state.get("uploaded_annotations_bytes"):
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
                        temp_pdf.write(st.session_state["uploaded_pdf_bytes"])
                        pdf_path = temp_pdf.name

                    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_annotations:
                        temp_annotations.write(st.session_state["uploaded_annotations_bytes"])
                        annotations_path = temp_annotations.name

                    text = self.pdf_extractor.extract_text(pdf_path)
                    annotations_df = self.annotation_processor.load_annotations(annotations_path)

                    os.unlink(pdf_path)
                    os.unlink(annotations_path)
                
                if text and 'annotations_df' in locals():
                    grouped_annotations = self.annotation_processor.group_annotations_by_tag(annotations_df)
                    st.session_state["extracted_text"] = text
                    st.session_state["grouped_annotations"] = grouped_annotations

        # Display extracted text and annotations
        if text and grouped_annotations:
            st.header("Extracted Text")
            st.text_area("", text, height=200)

            st.header("Annotations")
            for tag, items in grouped_annotations.items():
                st.subheader(f"{tag}")
                st.write(", ".join(items))

            # Generate quiz section
            st.header("Generated Quiz")
            
            quiz_action_col1, quiz_action_col2 = st.columns([1, 1])
            
            with quiz_action_col1:
                generate_button = st.button("Generate Quiz")
            
            with quiz_action_col2:
                if st.session_state.get("quiz"):
                    edit_button = st.button("✏️ Edit Quiz")
                    if edit_button:
                        st.session_state["editing_quiz"] = True
                        st.session_state["original_quiz_backup"] = None  # Clear any old backup when entering editor
                        st.rerun()
            
            # Generate quiz
            if generate_button:
                model_name = st.session_state.get("model_name", "mistralai/mistral-7b-instruct")
                tag_type = st.session_state["tag_type"]
                
                # Load activity generators dynamically
                self._load_activity_generators(tag_type, model_name)

                st.info(f"Using model: {model_options.get(model_name, model_name)} for quiz generation")

                quiz = self.quiz_generator.generate_quiz(text, grouped_annotations)
                
                st.session_state["quiz"] = quiz
                st.session_state["structured_quiz"] = parse_quiz_text(quiz)
                
                st.markdown(quiz)
                
                # Download quiz with dropdown menu
                with st.popover("Download Quiz", use_container_width=False):
                    st.write("Select format:")
                    
                    # PDF download
                    pdf_data = self.quiz_exporter.export_to_pdf(
                        st.session_state["structured_quiz"],
                        st.session_state["tag_type"],
                        text
                    )
                    st.download_button(
                        label="📄 PDF",
                        data=pdf_data,
                        file_name=f"quiz_{self.get_clean_filename(st.session_state['tag_type'])}_{time.strftime('%Y%m%d')}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                        key="download_pdf_gen"
                    )
                    
                    # DOCX download
                    docx_data = self.quiz_exporter.export_to_docx(
                        st.session_state["structured_quiz"],
                        st.session_state["tag_type"],
                        text
                    )
                    st.download_button(
                        label="📝 DOCX",
                        data=docx_data,
                        file_name=f"quiz_{self.get_clean_filename(st.session_state['tag_type'])}_{time.strftime('%Y%m%d')}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True,
                        key="download_docx_gen"
                    )
                    
                    # JSON download
                    json_data = self.quiz_exporter.export_to_json(
                        quiz,
                        text,
                        grouped_annotations,
                        st.session_state["tag_type"]
                    )
                    st.download_button(
                        label="📋 JSON",
                        data=json_data,
                        file_name=f"quiz_{self.get_clean_filename(st.session_state['tag_type'])}_{time.strftime('%Y%m%d')}.json",
                        mime="application/json",
                        use_container_width=True,
                        key="download_json_gen"
                    )
                
                st.rerun()
            
            # Display stored quiz
            elif st.session_state.get("quiz") and not st.session_state.get("editing_quiz"):
                st.markdown(st.session_state["quiz"])
                
                # Download quiz with dropdown menu
                with st.popover("Download Quiz", use_container_width=False):
                    st.write("Select format:")
                    
                    # PDF download
                    pdf_data = self.quiz_exporter.export_to_pdf(
                        st.session_state["structured_quiz"],
                        st.session_state["tag_type"],
                        text
                    )
                    st.download_button(
                        label="📄 PDF",
                        data=pdf_data,
                        file_name=f"quiz_{self.get_clean_filename(st.session_state['tag_type'])}_{time.strftime('%Y%m%d')}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                        key="download_pdf_display"
                    )
                    
                    # DOCX download
                    docx_data = self.quiz_exporter.export_to_docx(
                        st.session_state["structured_quiz"],
                        st.session_state["tag_type"],
                        text
                    )
                    st.download_button(
                        label="📝 DOCX",
                        data=docx_data,
                        file_name=f"quiz_{self.get_clean_filename(st.session_state['tag_type'])}_{time.strftime('%Y%m%d')}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True,
                        key="download_docx_display"
                    )
                    
                    # JSON download
                    json_data = self.quiz_exporter.export_to_json(
                        st.session_state["quiz"],
                        text,
                        grouped_annotations,
                        st.session_state["tag_type"]
                    )
                    st.download_button(
                        label="📋 JSON",
                        data=json_data,
                        file_name=f"quiz_{self.get_clean_filename(st.session_state['tag_type'])}_{time.strftime('%Y%m%d')}.json",
                        mime="application/json",
                        use_container_width=True,
                        key="download_json_display"
                    )

            # Student Feedback Mode
            if st.session_state.get("structured_quiz"):
                with st.expander("🚀 Student Feedback Mode: Load from Generated Quiz"):
                    st.write("Select a question from your generated quiz to test feedback:")
                    
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
                        
                        st.session_state["loaded_question"] = selected_q["text"]
                        st.session_state["loaded_correct_answer"] = selected_q["correct_answer"]
                        st.session_state["loaded_question_type"] = "Multiple Choice" if selected_q["type"] == "multiple_choice" else "Open-Ended"
                        
                        if selected_q["type"] == "multiple_choice":
                            st.session_state["loaded_options"] = selected_q["options"]
                        
                        st.success(f"Loaded Q{selected_q['number']} - Now fill in the student answer below!")
                        st.rerun()

            # Feedback input section
            if "loaded_question" in st.session_state:
                question = st.text_area(
                    "Question",
                    value=st.session_state.get("loaded_question", ""),
                    help="Enter the question text (loaded from quiz)"
                )
                
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
                model_name = st.session_state.get("model_name", "mistralai/mistral-7b-instruct")
                tag_type = st.session_state["tag_type"]
                
                # Load feedback generator dynamically
                self._load_activity_generators(tag_type, model_name)

                st.info(f"Using model: {model_options.get(model_name, model_name)} for feedback generation")

                api_question_type = "multiple_choice" if question_type == "Multiple Choice" else "open_ended"

                feedback = self.feedback_generator.generate_feedback(
                    question, 
                    correct_answer, 
                    student_answer,
                    annotations=st.session_state.get("grouped_annotations"),
                    original_text=st.session_state.get("extracted_text"),
                    question_type=api_question_type,
                    options=options if question_type == "Multiple Choice" else None
                )
                st.info(feedback)


def main():
    """Main function to run the application."""
    app = LindaMainApp()
    app.run()


if __name__ == "__main__":
    main()


