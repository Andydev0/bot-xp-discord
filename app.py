from flask import Flask, render_template
import json

app = Flask(__name__)

@app.route('/')
def leaderboard():
    with open('user_levels.json', 'r') as file:
        user_levels = json.load(file)
    sorted_users = sorted(user_levels.items(), key=lambda x: x[1]['level'], reverse=True)
    return render_template('leaderboard.html', users=sorted_users)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
