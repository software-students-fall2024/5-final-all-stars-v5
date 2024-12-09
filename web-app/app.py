"""
Loads flask app for web-app
"""
from datetime import datetime
import os
import logging
from dotenv import load_dotenv
import requests
from dotenv import load_dotenv
from flask import Flask, render_template, Blueprint, request, jsonify
import pymongo
load_dotenv()

connection = pymongo.MongoClient(os.getenv('MONGO_CXN_STRING'))
db = connection["history"]

load_dotenv()

app = Blueprint("main", __name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

ML_CLIENT_URL = os.getenv('ML_CLIENT_PORT')

def create_app():
    """
    Generate test app
    """
    test_app = Flask(__name__)
    test_app.register_blueprint(app)
    return test_app


@app.route("/")
def home():
    """Return default web page"""
    return render_template("index.html")

@app.route("/history")
def history():
    """Returns history web page"""
    docs = db.history.find({})
    log = []
    for doc in docs:
        prompt = doc["Prompt"]
        response = doc["Response"]
        response = response["response"]
        log.append({prompt: response})
    return render_template("history.html", log = log)

@app.route("/call_model", methods=["POST"])
def call_model():
    """
    Post request saves user input and posts it to ml-client to await response
    """
    try:

        user_input = request.form["user_input"]

        if not user_input:
            logging.error("No user input received.")
            return jsonify({"response": "User input is required"}), 400

        logging.info("Input received: %s", user_input)

        ml_endpoint = ML_CLIENT_URL + "/respond"

        try:
            response = requests.post(
                ml_endpoint,
                json={"user_input": user_input},
                timeout=15,
            )
                        
            try:
                response_json = response.json()
                logging.info("Response JSON: %s", response_json)
            except ValueError:
                logging.error("Response not JSON: %s", response.text)
                return jsonify({"response": "Invalid response from ML client"}), 500

            if response.status_code == 200:
                # Saving prompt and response to database
                try:
                    doc = {
                        "Prompt": user_input,
                        "Response": response_json,
                        "timestamp": datetime.utcnow()
                    }
                    db.history.insert_one(doc)
                except Exception as db_error:
                    logging.error("Database error: %s", db_error)
                    # Continue even if DB save fails
                
                return jsonify(response_json)
            
            error_msg = f"ML client returned {response.status_code}: {response.text}"
            logging.error(error_msg)
            return jsonify({"response": error_msg}), response.status_code

        except requests.exceptions.Timeout:
            error_msg = "ML client request timed out after 15 seconds"
            logging.error(error_msg)
            return jsonify({"response": error_msg}), 504

        except requests.exceptions.ConnectionError as e:
            error_msg = f"Could not connect to ML client: {str(e)}"
            logging.error(error_msg)
            return jsonify({
                "response": "ML service is unavailable. Please check if the model is properly loaded."
            }), 503

    except Exception as e:
        error_msg = f"Unexpected error in call_model: {str(e)}"
        logging.error(error_msg, exc_info=True)
        return jsonify({"response": "An unexpected error occurred"}), 500

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5001, debug=True)
