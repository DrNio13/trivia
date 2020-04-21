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
        self.database_path = "postgres://{}/{}".format(
            'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data["categories"]))

    def test_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data["questions"]))

    def test_400_questions(self):
        res = self.client().get('/questions&page=0')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)

    def test_delete(self):
        res = self.client().delete("/questions/5")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_create_question(self):
        res = self.client().post('/questions',
                                 json={"question": "how many basketball players play in a game?", "answer": "Five", "category": 1, "difficulty": 1})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_search_questions(self):
        res = self.client().post('/search/questions',
                                 json={"searchTerm": "title"})
        data = json.loads(res.data)
        questions = Question.query.filter(
            Question.question.ilike("title"))

        self.assertEqual(res.status_code, 200)

    def test_400_for_failed_search_questions(self):
        res = self.client().post('/search/questions',
                                 json={"searchTerm": ""})
        data = json.loads(res.data)
        questions = Question.query.filter(
            Question.question.ilike("title"))

        self.assertEqual(res.status_code, 400)

    def test_get_question_by_category_id(self):
        res = self.client().get("/categories/1/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)

    def test_400_get_question_by_category_id(self):
        res = self.client().get("/categories/-1/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)

    def test_get_quizz_question(self):
        res = self.client().post('/quizzes',
                                 json={"previous_questions": [], "quiz_category": {"type": "Sports", "id": 6}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)

    def test_error_get_quizz_question(self):
        res = self.client().post('/quizzes',
                                 json={"previous_questions": [], "quiz_category": {"type": "Sports", "id": -1}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 500)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
