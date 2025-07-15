from flask import Flask, render_template, request, redirect, url_for, session
from triage_assistant import create_web_graph, send_email
from dotenv import load_dotenv
import os

load_dotenv()
graph = create_web_graph()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dummy-secret")  # Needed for session use

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        email = request.form['email']
        symptoms_raw = request.form['symptoms']
        symptoms = [s.strip() for s in symptoms_raw.split(',') if s.strip()]

        state = {
            'name': name,
            'age': age,
            'email': email,
            'symptoms': symptoms,
            'done': True
        }

        # Save state to session for redirect
        session['form_data'] = state
        return redirect(url_for('result'))

    return render_template('index.html')


@app.route('/result')
def result():
    state = session.get('form_data')
    if not state:
        return redirect(url_for('index'))

    final_state = graph.invoke(state)

    # Clear session after use
    session.pop('form_data', None)

    return render_template('result.html', final_state=final_state)


if __name__ == '__main__':
    app.run(debug=True)
