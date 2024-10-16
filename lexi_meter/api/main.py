"""The main script for the project"""

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, status

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
    pass


@app.post("/create-quiz/", status_code=status.HTTP_201_CREATED)
async def create_quiz():
    """Creates a new quiz"""
    pass


@app.get("/get-available-quiz/", status_code=status.HTTP_200_OK)
async def get_available_quiz():
    """Retrieve list of available quizzes"""
    pass


@app.get("/get-quiz/{quiz_id}", status_code=status.HTTP_200_OK)
async def get_quiz(quiz_id):
    """Retrieves specific quiz"""
    pass


@app.delete("/delete-quiz/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quiz(quiz_id: str = None):
    """Deletes quiz"""
    pass


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
