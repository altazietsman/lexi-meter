class Quiz:
    """
    The Quiz class defines the main game (or quiz) logic for the backend
    of the application.
    """

    def __init__(self, quiz_df):
        """The constructor for the Quiz class.

        Args:
            quiz_df (pd.DataFrame): The quiz data frame that contains the multiple choice questions.
            The columns of the data frame should be as follows:
                - question_nr: The number of the question (also the index and UID of the data frame).
                - question: The question that is being asked.
                - option_a: The first option for the question.
                - option_b: The second option for the question.
                - option_c: The third option for the question.
                - correct_option: The correct option for the question.
        """
        self.quiz_df = quiz_df
        self.validate_quiz_df()

    def validate_quiz_df(self):
        """
        Validates the quiz data frame.
        """
        expected_columns = [
            "question_nr",
            "question",
            "option_a",
            "option_b",
            "option_c",
            "correct_option",
        ]
        if not set(expected_columns).issubset(self.quiz_df.columns):
            raise ValueError(
                f"Columns of the quiz data frame should be {expected_columns}"
            )

    def check_answers(self, participant_answers):
        """
        Checks the answers of the participants and returns the results.
        Also counts the number of correct answers.
        """
        num_correct_answers = 0
        for participant_answer in participant_answers:
            question_nr = participant_answer["question_nr"]
            chosen_option = participant_answer["chosen_option"]

            # Defensive check for matching question_nr
            correct_row = self.quiz_df[self.quiz_df["question_nr"] == question_nr]

            if correct_row.empty:
                raise ValueError(
                    f"No matching question found for question_nr {question_nr}"
                )

            correct_option = correct_row["correct_option"].values[0]

            # Compare chosen with the correct and increment if answer is the same
            if chosen_option == correct_option:
                num_correct_answers += 1

        return num_correct_answers
