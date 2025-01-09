import os
from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from openai import OpenAI
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a random secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chats.db'
db = SQLAlchemy(app)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    response = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message']
    user_id = session.get('user_id', 'default_user')

    # Call OpenAI API
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a knowledgeable fitness assistant. Provide helpful and accurate information about workouts, diet plans, and general fitness advice.Dont entertain any question which is not related to fitness.You can also chat in Roman Urdu and Urdu.Also provide video tutorial links from youtube of recommended exercises."},
            {"role": "user", "content": user_message}
        ]
    )

    ai_message = response.choices[0].message.content

    # Store the chat in the database
    chat = Chat(user_id=user_id, message=user_message, response=ai_message)
    db.session.add(chat)
    db.session.commit()

    return jsonify({'response': ai_message})

@app.route('/history')
def history():
    user_id = session.get('user_id', 'default_user')
    chats = Chat.query.filter_by(user_id=user_id).order_by(Chat.timestamp.desc()).all()
    return render_template('history.html', chats=chats)

if __name__ == '__main__':
    app.run(debug=True)