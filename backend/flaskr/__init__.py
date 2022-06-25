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

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    # CORS(app)
    # """
    # @TODO: Use the after_request decorator to set Access-Control-Allow
    # """
    # @app.after_request
    # def after_request(response):
    #     response.headers.add(
    #         "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
    #     )
    #     response.headers.add(
    #         "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
    #     )
    #     return response
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
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
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.
    
    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions', methods=['GET'])
    def get_questions():
        page = request.args.get('page', 1, type=int)

        categories = Category.query.order_by(Category.type).all()
        formatted_categories = [category.format() for category in categories]

        questions = Question.query.order_by(Question.id).paginate(page, QUESTIONS_PER_PAGE, error_out=False)
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
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.
    
    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
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
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def create_question():
        error = False
        body = request.get_json()
        searchTerm = body.get('searchTerm', None)
        try:
            new_question = body.get('question')
            new_question_ans = body.get('answer')
            new_question_cat = body.get('category')
            new_question_diff = body.get('difficulty')
        except:
            abort(422)

        if not searchTerm:
            try:
                question = Question(
                    question=new_question, 
                    answer=new_question_ans,
                    category=new_question_cat,
                    difficulty=new_question_diff)
                question.insert()
            except:
                db.session.rollback()
                error = True
            finally:
                db.session.close()
            
            if error:
                abort(500)
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
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:cat_id>/questions', methods=['GET'])
    def get_questions_by_category(cat_id):
        page = request.args.get('page', 1, type=int)
        # current_category = Category.query.with_entities(Category.type).filter(Category.id==cat_id).one_or_none()
        questions = Question.query.filter_by(category=cat_id).order_by(Question.id).paginate(page, QUESTIONS_PER_PAGE, error_out=False)
        if not questions:
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
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def get_quiz():
        try:
            body = request.get_json()

            if not ('quiz_category' in body and 'previous_questions' in body):
                abort(422)

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
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

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
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "internal server error"
        }), 500

    return app
