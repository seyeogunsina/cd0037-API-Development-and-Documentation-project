import os
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from sqlalchemy import null

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    
    # Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs

    CORS(app, resources={r"*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, PUT, PATCH, DELETE, OPTIONS')
        return response

    # Endpoint to handle GET requests for all available categories
    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories = Category.query.order_by(Category.type).all()
        formatted_categories = [category.format() for category in categories]

        category_keys = []
        category_values = []

        for category in formatted_categories:
            category_keys.append(category['id'])
            category_values.append(category['type'])

        categories_dict = dict(zip(category_keys, category_values))
        return jsonify({
            'success': True,
            'categories': categories_dict
        })

    """
    An endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    It returns a list of questions,
    number of total questions, current category, categories.
    """
    @app.route('/questions', methods=['GET'])
    def get_questions():
        page = request.args.get('page', 1, type=int)

        categories = Category.query.order_by(Category.type).all()
        formatted_categories = [category.format() for category in categories]

        questions = Question.query.order_by(Question.id).paginate(page, QUESTIONS_PER_PAGE, error_out=True)
        formatted_questions = [question.format() for question in questions.items]

        category_keys = []
        category_values = []

        for category in formatted_categories:
            category_keys.append(category['id'])
            category_values.append(category['type'])

        categories_dict = dict(zip(category_keys, category_values))
        return jsonify({
            'success': True,
            'questions': formatted_questions,
            'total_questions': questions.total,
            'current_category': None,
            'categories': categories_dict
        })

    # An endpoint to DELETE question using a question ID.

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        error = False
        try:
            question = Question.query.get(question_id)
            if question is None:
                abort(404)
            question.delete()
        except:
            db.session.rollback()
            error = True
        finally:
            db.session.close()
        
        if error:
            abort(422)
        else:
            return jsonify({
                'success': True
            })

    """
    An endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    Also, If the searchTerm parameter is defined, it is used to handle search for questions using POST method.
    """
    @app.route('/questions', methods=['POST'])
    def create_question():
        error = False
        body = request.get_json()
        if body:
            searchTerm = body.get('searchTerm', None)
        else:
            searchTerm = None

        if not searchTerm:
            try:
                question = Question(
                    question=body.get('question'), 
                    answer=body.get('answer'),
                    category=body.get('category'),
                    difficulty=body.get('difficulty'))
                question.insert()
            except:
                db.session.rollback()
                error = True
            finally:
                db.session.close()
            
            if error:
                abort(422)
            else:
                return jsonify({'success': True})
        else:
            page = request.args.get('page', 1, type=int)
            questions = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(searchTerm))).paginate(page, QUESTIONS_PER_PAGE, error_out=False)
            formatted_questions = [question.format() for question in questions.items]
            return jsonify({
            'success': True,
            'questions': formatted_questions,
            'total_questions': questions.total,
            'current_category': None,
        })
  
    # A GET endpoint to get questions based on category.

    @app.route('/categories/<int:cat_id>/questions', methods=['GET'])
    def get_questions_by_category(cat_id):
        page = request.args.get('page', 1, type=int)
        # current_category = Category.query.with_entities(Category.type).filter(Category.id==cat_id).one_or_none()
        questions = Question.query.filter_by(category=cat_id).order_by(Question.id).paginate(page, QUESTIONS_PER_PAGE, error_out=False)
        if not questions.items:
            abort(404)
        formatted_questions = [question.format() for question in questions.items]

        categories = Category.query.order_by(Category.type).all()
        formatted_categories = [category.format() for category in categories]

        category_keys = []
        category_values = []

        for category in formatted_categories:
            category_keys.append(category['id'])
            category_values.append(category['type'])

        categories_dict = dict(zip(category_keys, category_values))
        return jsonify({
            'success': True,
            'questions': formatted_questions,
            'total_questions': questions.total,
            'current_category': categories_dict[cat_id],
            'categories': categories_dict
        })

    """
    A POST endpoint to get questions to play the quiz.
    This endpoint takes category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.
    """
    @app.route('/quizzes', methods=['POST'])
    def get_quiz():
        try:
            body = request.get_json()

            if not ('quiz_category' in body and 'previous_questions' in body):
                abort(400)

            category = int(body.get('quiz_category')['id'])
            previous_questions = body.get('previous_questions')

            if category == 0:
                outstanding_questions = Question.query.filter(
                    Question.id.notin_(previous_questions)).all()
            else:
                outstanding_questions = Question.query.filter_by(
                    category=category).filter(Question.id.notin_(previous_questions)).all()

            if len(outstanding_questions) > 0:
                question = outstanding_questions[random.randrange(
                    0, len(outstanding_questions))].format()
            else:
                question = None
            
            return jsonify({
                'success': True,
                'question': question
            })
        except:
            abort(422)
    
    """
    Error handlers
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        }), 405

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "internal server error"
        }), 500

    return app
