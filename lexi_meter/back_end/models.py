"""Defines schemas and data models for api"""

from datetime import datetime
from uuid import uuid4 as uuid

from sqlmodel import Field, Relationship, SQLModel, create_engine

# TODO: should we consider maybe changing to in memory
sql_file_name = "database.db"
sqlite_url = f"sqlite:///{sql_file_name}"

engine = create_engine(sqlite_url, echo=True)


def create_db_and_tables():
    """Creates sql tables"""
    SQLModel.metadata.create_all(engine)


def get_default_uuid():
    """Get uuid"""
    return str(uuid())


# TODO will see if this works. Maybe w should have a csv?
# Curently only creates one question
class QuizCreateBody(SQLModel):
    """Defines quize creation body"""

    quiz: str = Field(default=None, min_length=1, max_length=255)
    options: list[str] = Field(default=None, min_length=1, max_length=255, min_items=2, max_items=5)


class Quiz(SQLModel, table=True):
    "Stores quiz name and metadata"

    id: str | None = Field(default_factory=get_default_uuid, primary_key=True)
    title: str = Field(default=None, min_length=1, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: str = Field(nullable=False)
    questions: list["QuizQuestion"] = Relationship(
        back_populates="quiz", sa_relationship_kwargs={"cascade": "all,delete-orphan"}
    )


class QuizQuestion(SQLModel, table=True):
    "Stores questions for each quiz"

    id: str | None = Field(default_factory=get_default_uuid, primary_key=True)
    question_text: str = Field(nullable=False, min_length=1, max_length=255)
    quiz_id: str = Field(foreign_key="quiz.id", nullable=False)
    options: list["QuizOption"] = Relationship(
        back_populates="question",
        sa_relationship_kwargs={"cascade": "all,delete-orphan"},
    )
    quiz: Quiz = Relationship(back_populates="questions")


class QuizOption(SQLModel, table=True):
    "Stores answer options for each question"

    id: str | None = Field(default_factory=get_default_uuid, primary_key=True)
    option_text: str = Field(nullable=False)
    question_id: str = Field(foreign_key="quizquestion.id", nullable=False)
    question: QuizQuestion = Relationship(back_populates="options")
    answers: list["QuizAnswer"] = Relationship(
        back_populates="option", sa_relationship_kwargs={"cascade": "all,delete-orphan"}
    )


class Participant(SQLModel, table=True):
    "Stores Participant information"

    id: str | None = Field(default_factory=get_default_uuid, primary_key=True)
    name: str = Field(nullable=False)
    email: str | None = Field(default=None)
    answers: list["QuizAnswer"] = Relationship(
        back_populates="participant",
        sa_relationship_kwargs={"cascade": "all,delete-orphan"},
    )


class QuizAnswer(SQLModel, table=True):
    "Stores answers from participants"

    id: str | None = Field(default_factory=get_default_uuid, primary_key=True)
    question_id: str = Field(foreign_key="quizquestion.id", nullable=False)
    option_id: str = Field(foreign_key="quizoption.id", nullable=False)
    participant_id: str = Field(foreign_key="participant.id", nullable=False)
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    option: QuizOption = Relationship(back_populates="answers")
    participant: Participant = Relationship(back_populates="answers")
