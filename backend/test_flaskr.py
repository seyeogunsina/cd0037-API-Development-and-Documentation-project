import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format("student", "student", "localhost:5432", self.database_name)
        setup_db(self.app, self.database_path)
 
        # creates a new question instance
        self.new_question = {
            "question": "Who is the founder of Microsoft",
            "answer": "Bill Gates",
            "category": "1",
            "difficulty": 3
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["categories"]))

    def test_get_categories_405(self):
        res = self.client().post("/categories")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "method not allowed")

    def test_get_paginated_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["categories"]))

    def test_get_paginated_questions_404(self):
        res = self.client().get("/questions?page=1256")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_get_questions_by_category(self):
        res = self.client().get("/categories/2/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["total_questions"])
        self.assertEqual(data["current_category"], "Art")
        self.assertTrue(len(data["categories"]))

    def test_get_questions_by_category_404(self):
        res = self.client().get("/categories/200/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    # alter the question id for each trial
    def test_delete_question(self):
        res = self.client().delete("/questions/5")
        data = json.loads(res.data)

        question = Question.query.get(5)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(question, None)
    
    def test_delete_question_422(self):
        res = self.client().delete("/questions/2000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    def test_post_new_question(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_post_new_question_422(self):
        res = self.client().post("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    def test_question_search_with_results(self):
        res = self.client().post("/questions", json={"searchTerm": "name"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertEqual(len(data["questions"]), 2)

    def test_question_search_without_results(self):
        res = self.client().post("/questions", json={"searchTerm": "applejacksasgsf"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["total_questions"], 0)
        self.assertEqual(len(data["questions"]), 0)

    def test_play_quiz(self):
        data = {
            "quiz_category": {
                "id": 1
            },
            "previous_questions": []
        }
        res = self.client().post('/quizzes', json=data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["success"], True)

    def test_play_quiz_405(self):
        data = {
            "quiz_category": {
                "id": 1
            },
            "previous_questions": []
        }
        res = self.client().get('/quizzes', json=data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(res.get_json()["success"], False)
        self.assertEqual(res.get_json()["message"], "method not allowed")

    def test_play_quiz_422(self):
        data = {
            "quiz_category": {
                "id": None
            },
            "previous_questions": []
        }
        res = self.client().post('/quizzes', json=data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(res.get_json()["success"], False)
        self.assertEqual(res.get_json()["message"], "unprocessable")

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()