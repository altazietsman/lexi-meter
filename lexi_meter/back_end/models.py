"""Defines schemas and data models for api"""

from datetime import datetime
from typing import Optional, List
from uuid import uuid4 as uuid
from sqlmodel import Field, SQLModel, create_engine, Relationship


# TODO: should we consider maybe changing to in memory
sql_file_name = "database.db"
sqlite_url = f"sqlite:///{sql_file_name}"

engine = create_engine(sqlite_url, echo=True)


def create_db_and_tables():
    """Creates sql tables"""
    SQLModel.metadata.create_all(engine)


def get_defult_uuid():
    """Get uuid"""
    return str(uuid())


# TODO will see if this works. Maybe w should have a csv?
# Curently only creates one question
class QuizCreateBody(SQLModel):
    """Defines quize creation body"""

    quiz: str = Field(default=None, min_length=1, max_length=255)
    options: List[str] = Field(
        default=None, min_length=1, max_length=255, min_items=2, max_items=5
    )


class Quiz(SQLModel, table=True):
    "Stores quiz name and metadata"
    id: Optional[str] = Field(default_factory=get_defult_uuid, primary_key=True)
    title: str = Field(default=None, min_length=1, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)

    questions: List["QuizQuestion"] = Relationship(
        back_populates="quiz", sa_relationship_kwargs={"cascade": "all,delete-orphan"}
    )


class QuizQuestion(SQLModel, table=True):
    "Stores questions for each quiz"
    id: Optional[str] = Field(default_factory=get_defult_uuid, primary_key=True)
    question: str = Field(default=None, min_length=1, max_length=255)
    quiz_id: str = Field(foreign_key="quiz.id", nullable=False)

    options: List["QuizOption"] = Relationship(
        back_populates="question",
        sa_relationship_kwargs={"cascade": "all,delete-orphan"},
    )

    quiz: Quiz = Relationship(back_populates="questions")


class QuizOption(SQLModel, table=True):
    "Stores answer options for each qustion"
    id: Optional[str] = Field(default_factory=get_defult_uuid, primary_key=True)
    question_id: str = Field(foreign_key="question.id", nullable=False)
    option_text: str = Field(nullable=False)

    question: QuizQuestion = Relationship(back_populates="options")
    answers: List["QuizAnswer"] = Relationship(
        back_populates="option", sa_relationship_kwargs={"cascade": "all,delete-orphan"}
    )


class Participant(SQLModel, table=True):
    "Stores Participant information"
    id: Optional[str] = Field(default_factory=get_defult_uuid, primary_key=True)
    participant_name: str = Field(default=None, min_length=1, max_length=255)

    answers: List["QuizAnswer"] = Relationship(
        back_populates="participant",
        sa_relationship_kwargs={"cascade": "all,delete-orphan"},
    )


class QuizAnswer(SQLModel, table=True):
    "Stores answers from participants"
    id: Optional[str] = Field(default_factory=get_defult_uuid, primary_key=True)
    participant_id: str = Field(foreign_key="participant.id", nullable=False)
    option_id: str = Field(foreign_key="quizoption.id", nullable=False)

    option: QuizOption = Relationship(back_populates="answers")
    participant: Participant = Relationship(back_populates="answers")
