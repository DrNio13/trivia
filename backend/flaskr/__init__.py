import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from sqlalchemy.sql.expression import func, select

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources=r'/api/*')

    @app.route("/")
    def get_status():
        return jsonify({"status": True})

    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Headers",
                             "Content-Type, Authorization")
        response.headers.add("Access-Control-Allow-Methods",
                             "GET, POST, DELETE, PUT, PATCH, OPTIONS")
        return response

    @app.route("/categories")
    def get_categories():
        categories = Category.query.all()
        formatted_categories = [category.format() for category in categories]

        return jsonify({
            "categories": formatted_categories
        })

    @app.route("/questions")
    def get_questions():
        page = request.args.get("page", 1, type=int)
        if (page <= 0):
            abort(400)
        start = (page - 1) * 10
        end = start + 10
        questions = Question.query.all()
        formatted_questions = [question.format() for question in questions]
        categories = set()
        for question in questions:
            category_type = get_category_type(question.category)
            categories.add(category_type)

        return jsonify({
            "questions": formatted_questions[start:end],
            "total_questions": len(formatted_questions),
            "categories": list(categories),
            "current_category": None
        })

    def get_category_type(id):
        categories = Category.query.all()
        category_found = ''

        for category in categories:
            if (category.id == id):
                category_found = category.type
        return category_found

    @app.route('/questions/<int:id>', methods=["DELETE"])
    def delete_question_by_id(id):
        try:
            Question.query.filter(Question.id == id).delete()
            db.session.commit()

            return jsonify({
                "success": True
            })

        except:
            abort(500)

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Sorry, we couldn't found what you are looking for"
        }), 404

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "It's not you, it's us"
        }), 500

    @app.errorhandler(422)
    def unable_to_process(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Your request is well-formed, however, due to semantic errors it is unable to be processed"
        }), 422

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            "success": False,
            "error": 401,
            "message": "Oops...you are not authorized to do that"
        }), 401

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Sorry, this time it is you"
        }), 400

    @app.route('/questions', methods=["POST"])
    def create_question():
        try:
            body = request.get_json()

            question = body.get('question', None)
            answer = body.get('answer', None)
            category = body.get('category', None)
            difficulty = body.get('difficulty', None)

            question = Question(question=question, answer=answer,
                                category=category, difficulty=difficulty)
            question.insert()
            return jsonify({
                "success": True
            })
        except:
            abort(500)

    @app.route('/search/questions', methods=["POST"])
    def search_question():
        try:
            body = request.get_json()

            searchTerm = body.get('searchTerm', '')
            if (searchTerm is None or searchTerm == ''):
                abort(400)

            search = "%{}%".format(searchTerm)
            all_questions = Question.query.all()
            questions_found = Question.query.filter(
                Question.question.ilike(search))
            questions_found_formatted = [
                question.format() for question in questions_found]

            return jsonify({
                "questions": questions_found_formatted,
                "total_questions": len(all_questions),
                "current_category": None
            })
        except:
            abort(400)

    @app.route('/categories/<int:id>/questions')
    def get_question_by_category_id(id):
        try:
            if(id < 0):
                abort(400)
            category_type = get_category_type(id)
            all_questions = Question.query.all()
            questions = Question.query.filter(
                Question.category == id).all()
            questions_formatted = [question.format() for question in questions]

            return jsonify({
                "questions": questions_formatted,
                "total_questions": len(all_questions),
                "current_category": category_type
            })
        except Exception as e:
            print(e)
            abort(500)

    @app.route('/quizzes', methods=["POST"])
    def get_quizz_question():
        try:
            body = request.get_json()
            previous_questions = body.get("previous_questions")
            category = body.get("quiz_category")
            if (previous_questions == None):
                abort(400)
            if (category == None):
                abort(400)

            category_id = category['id']
            if (category['id'] == 0):
                category_id = random.randint(1, 6)

            random_question = random.choice(
                Question.query.filter(Question.category == category_id).all())
            tries = 0
            max_tries = 100
            while ((random_question.id in previous_questions) or (tries > max_tries)):
                random_question = random.choice(Question.query.all())
                tries += 1
            else:
                return jsonify({
                    "question": random_question.format()
                })
        except Exception as e:
            print(e)
            abort(500)

    return app
