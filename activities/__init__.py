"""Activity-specific quiz and feedback generators."""

from .activity_5w import QuizGenerator5W, FeedbackGenerator5W
from .activity_thesis import QuizGeneratorThesis, FeedbackGeneratorThesis
from .activity_argument import QuizGeneratorArgument, FeedbackGeneratorArgument
from .activity_connective import QuizGeneratorConnective, FeedbackGeneratorConnective

__all__ = [
    'QuizGenerator5W',
    'FeedbackGenerator5W',
    'QuizGeneratorThesis',
    'FeedbackGeneratorThesis',
    'QuizGeneratorArgument',
    'FeedbackGeneratorArgument',
    'QuizGeneratorConnective',
    'FeedbackGeneratorConnective'
]


