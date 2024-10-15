"""
NOTE: Run via the run_scripts.sh script
"""

import pandas as pd
import pytest

from lexi_meter.back_end.quiz import Quiz


def test_incorrect_cols():
    """
    Test if validate columns raises an error when the columns are incorrect.
    """
    df = pd.read_csv("tests/data/test_quiz_questions.csv")
    df.drop(columns=["question_nr"], inplace=True)
    with pytest.raises(ValueError):
        q = Quiz(df)
        print(q)


def test_check_answers():
    """
    Test if the quiz computes the score correctly.
    NOTE: This will have to change once Timothy incorporates his database schema.
    """
    expected_participant_answers = 10

    df = pd.read_csv("tests/data/test_quiz_questions.csv")
    q = Quiz(df)
    participant_answers = [
        {"question_nr": 1, "chosen_option": "option_c"},
        {"question_nr": 2, "chosen_option": "option_b"},
        {"question_nr": 3, "chosen_option": "option_a"},
        {"question_nr": 4, "chosen_option": "option_a"},
        {"question_nr": 5, "chosen_option": "option_b"},
        {"question_nr": 6, "chosen_option": "option_a"},
        {"question_nr": 7, "chosen_option": "option_c"},
        {"question_nr": 8, "chosen_option": "option_b"},
        {"question_nr": 9, "chosen_option": "option_c"},
        {"question_nr": 10, "chosen_option": "option_a"},
    ]
    assert q.check_answers(participant_answers) == expected_participant_answers


def test_incorrect_answers_dict():
    """
    Test if the quiz computes the score correctly.
    NOTE: This will have to change once Timothy incorporates his database schema.
    """
    df = pd.read_csv("tests/data/test_quiz_questions.csv")
    q = Quiz(df)
    participant_answers = [
        {"question_nr": 11, "chosen_option": "option_c"},
    ]
    with pytest.raises(ValueError):
        _ = q.check_answers(participant_answers)
