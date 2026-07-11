from flask import Flask, jsonify
app = Flask(__name__)
@app.route("/")
def home():
    return jsonify({
        "message": "Welcome to my first backend API!"
    })
@app.route("/about")
def about():
    return jsonify({
        "name": "Sri Charan Tej",
        "track": "Backend AI Engineering",
        "week": 1
    })
if __name__ == "__main__":
    app.run(debug=True)