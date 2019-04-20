from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/game')
def game():
    question = '_____ is the most populous city in Texas and the fourth largest in the U.S., while San Antonio is the second-most populous in the state and seventh largest in the U.S. Dallas–Fort Worth and Greater Houston are the fourth and fifth largest metropolitan statistical areas in the country, respectively.'
    answer = 'Houston'
    selection = ["Houston", "Dallas", "Bryan", "College Station","Austin"]
    return render_template('game.html', question = question, selection = selection, answer = answer)

@app.route('/correct')
def correct():
    return render_template('correct.html')

@app.route('/wrong')
def wrong():
    return render_template('wrong.html')

if __name__ == '__main__':
    app.debug = True
    app.run()