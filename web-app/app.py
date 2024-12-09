"""
Loads flask app for web-app
"""
import os
import logging
from dotenv import load_dotenv
import requests
from flask import Flask, render_template, Blueprint, request, jsonify
import pymongo
load_dotenv()

connection = pymongo.MongoClient(os.getenv('MONGO_CXN_STRING'))
db = connection["history"]
app = Blueprint("main", __name__)

# logging for dev -- delete later
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
        # Extract user input
        user_input = request.form["user_input"]
        logging.info("Input received: %s", user_input)

        # Make a call to the /respond endpoint on port 5002
        ml_endpoint = ML_CLIENT_URL + "/respond"
        response = requests.post(
            ml_endpoint,
            json={"user_input": user_input},  # Sending user input as JSON
            timeout=15,
        )

        # Handle response from the /respond endpoint
        if response.status_code == 200:
            # Saving prompt and response to database
            doc = {
                "Prompt": user_input,
                "Response": response.json()
            }
            db.history.insert_one(doc)
            return jsonify(response.json())  # Forward the successful response
        # Handle error responses from the /respond endpoint
        return (
            jsonify({"response": f"Failed to call /respond: {response.text}"}),
            response.status_code,
        )
    # NewConnectionError
    except requests.exceptions.ConnectionError as e:
        logging.error("error in /call_model: %s", e)
        return jsonify({"response": "Error connecting to ml-client"})
    except Exception as e:  # pylint: disable=broad-exception-caught
        # logging.error("Error in /call_model: %s", e)
        return jsonify({"response": str(e)}), 500


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5001, debug=True)
