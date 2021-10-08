from flask import Flask
from flask import jsonify
from flask import Blueprint
import json

list = [{
        "account": 10072636331,
        "lastDecision": "Accept",
        "delinquencyStatus": 1.0,
        "target": "Good",
        "loanToIncome": 31.82,
        "residentialStatus": "H",
        "score": 1
    },
    {
        "account": 10769083290,
        "delinquencyStatus": 0.0,
        "lastDecision": "Accept",
        "loanToIncome": 45.45,
        "residentialStatus": "H",
        "score": 0,
        "target": "Good"
    }]

app = Flask(__name__)

@app.route("/")
def index():
    return "Welcome Here"

@app.route("/test", methods=['GET'])
def get():
    return jsonify(list)

@app.route("/test/<int:person_id>", methods=['GET'])
def get_age():
    return jsonify({"Test": list["person_id"]})

@app.route("/test", methods=['POST'])
def create():
    test2 = { "name": "Petur",
             "last": "Petrov",
             "age": "24"}

    return jsonify({'Created': test2})

app.run(debug=True)