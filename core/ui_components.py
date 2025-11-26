"""Shared UI components and utilities."""

import re
from typing import List, Dict


def parse_quiz_text(quiz_text: str) -> List[Dict]:
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


def format_structured_quiz(structured_quiz: List[Dict]) -> str:
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


