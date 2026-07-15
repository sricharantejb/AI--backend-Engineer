from flask import Flask, jsonify
from service import get_students

app = Flask(__name__)

@app.route("/students")
def students():
    return jsonify(get_students())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    