"""The main script for the project"""

import uvicorn
from fastapi import (
    FastAPI,
    HTTPException,
    Response,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from sqlmodel import Session, select

from lexi_meter.back_end.models import (
    Participant,
    Quiz,
    QuizAnswer,
    QuizCreateBody,
    QuizOption,
    QuizQuestion,
    SubmitAnswersBody,
    create_db_and_tables,
    engine,
)

app = FastAPI()


class QuizManager:
    """Manages all participant connections"""

    def __init__(self):
        self.participant_connections: dict[any, list] = {}

    async def connect(self, websocket: WebSocket, quiz_id):
        """Connects to quiz"""
        await websocket.accept()

        if not self.participant_connections.get(quiz_id):
            self.participant_connections[quiz_id] = []
        self.participant_connections[quiz_id].append(websocket)

    async def disconnect(self, websocket: WebSocket, quiz_id):
        """Disconnect form quiz"""
        self.participant_connections[quiz_id].remove(websocket)

    async def broadcast(self, message: str, quiz_id: int):
        """Broadcast message to participants"""
        pass


manager = QuizManager()


@app.on_event("startup")
def on_startup():
    """Creates database on start-up"""
    create_db_and_tables()


@app.post("/create-quiz/", status_code=status.HTTP_201_CREATED)
async def create_quiz(data: QuizCreateBody):
    """Creates a new quiz with multiple questions and options."""
    with Session(engine) as session:
        questions = [
            QuizQuestion(
                question_text=question["question_text"],
                options=[QuizOption(option_text=option_text) for option_text in question["options"]],
            )
            for question in data.questions
        ]

        quiz = Quiz(title=data.title, user_id=data.user_id, questions=questions)

        session.add(quiz)
        session.commit()
        session.refresh(quiz)

        return {"quiz_id": quiz.id, "message": "Quiz created successfully"}


@app.get("/get-available-quiz/", status_code=status.HTTP_200_OK)
async def get_available_quiz():
    """Retrieve list of available quizzes"""
    with Session(engine) as session:
        statement = select(Quiz)
        result = session.exec(statement)
        quizzes = result.all()
        return [{"id": quiz.id, "title": quiz.title} for quiz in quizzes]


@app.get("/get-quiz/{quiz_id}", status_code=status.HTTP_200_OK)
async def get_quiz(quiz_id: str):
    """Retrieve detailed information for a specific quiz."""
    with Session(engine) as session:
        quiz = session.get(Quiz, quiz_id)
        if not quiz:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")

        quiz_details = {"id": quiz.id, "title": quiz.title, "questions": []}

        for question in quiz.questions:
            question_info = {
                "id": question.id,
                "text": question.question_text,
                "options": [],
            }

            for option in question.options:
                vote_count = session.exec(
                    select(QuizAnswer).where(QuizAnswer.option_id == option.id)
                ).count()

                option_info = {
                    "id": option.id,
                    "text": option.option_text,
                    "vote_count": vote_count,
                }

                answers = session.exec(select(QuizAnswer).where(QuizAnswer.option_id == option.id)).all()

                participants = [
                    {
                        "id": answer.participant_id,
                        "name": session.get(Participant, answer.participant_id).name,
                    }
                    for answer in answers
                ]
                option_info["participants"] = participants

                question_info["options"].append(option_info)

            quiz_details["questions"].append(question_info)

        return quiz_details


@app.delete("/delete-quiz/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quiz(quiz_id: str):
    """Deletes a quiz by ID."""
    with Session(engine) as session:
        quiz = session.get(Quiz, quiz_id)
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")

        session.delete(quiz)
        session.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post("/submit-answers/", status_code=status.HTTP_201_CREATED)
async def submit_answers(data: SubmitAnswersBody):
    """Submit answers for a quiz."""
    with Session(engine) as session:
        participant = session.exec(
            select(Participant).where(Participant.name == data.participant.name)
        ).first()

        if not participant:
            participant = Participant(name=data.participant.name)
            session.add(participant)
            session.commit()
            session.refresh(participant)

        for answer in data.answers:
            option = session.exec(
                select(QuizOption)
                .where(QuizOption.id == answer.option_id)
                .where(QuizOption.question_id == answer.question_id)
            ).first()

            if not option:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"""Invalid option_id '{answer.option_id}' for 
                                question_id '{answer.question_id}'.""",
                )

            quiz_answer = QuizAnswer(
                question_id=answer.question_id,
                option_id=answer.option_id,
                participant_id=participant.id,
            )
            session.add(quiz_answer)

        session.commit()
        return {"message": "Answers submitted successfully"}


@app.websocket("/quiz/{quiz_id}/ws/{participant_id}")
async def quiz(websocket: WebSocket, quiz_id: int, participant_id: int):
    await manager.connect(websocket, quiz_id)
    try:
        while True:
            # TODO: uncomment when we start using this. It is causing linting errors.
            # data = await websocket.receive_json()
            """Where the magic happens when client is connected"""

    except WebSocketDisconnect:
        await manager.disconnect(websocket, quiz_id)
        await manager.broadcast("Participant has left the quiz", quiz_id=quiz_id)


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
