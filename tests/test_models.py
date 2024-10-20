"""Test creation of tables"""

import pytest
from sqlmodel import Session, SQLModel, create_engine

from lexi_meter.back_end.models import Quiz, QuizOption, QuizQuestion


@pytest.fixture
def engine():
    "Create engin and tables"
    sqlite_url = "sqlite:///:memory:"  # In-memory SQLite
    engine = create_engine(sqlite_url, echo=False)
    SQLModel.metadata.create_all(engine)  # Create tables
    return engine


@pytest.fixture
def session(engine):
    "Provide a new session for each test"
    with Session(engine) as session:
        yield session


def test_create_quiz(session):
    "Arrange: Create a quiz with a question and options"
    question = QuizQuestion(
        question_text="What is your favorite programming language?",
        options=[
            QuizOption(option_text="Python"),
            QuizOption(option_text="JavaScript"),
        ],
    )

    new_quiz = Quiz(
        title="Programming Survey", user_id="user_123", questions=[question]
    )

    # Add the quiz to the session and commit
    session.add(new_quiz)
    session.commit()

    quizzes = session.query(Quiz).all()
    assert len(quizzes) == 1

    quiz_from_db = quizzes[0]
    number_of_questions = 1
    assert quiz_from_db.title == "Programming Survey"
    assert len(quiz_from_db.questions) == number_of_questions

    question_from_db = quiz_from_db.questions[0]
    number_of_options = 2
    assert len(question_from_db.options) == number_of_options
    assert (
        question_from_db.question_text == "What is your favorite programming language?"
    )

    option_texts = [option.option_text for option in question_from_db.options]
    assert "Python" in option_texts
    assert "JavaScript" in option_texts
