from flask import Flask, render_template, request, redirect, session
from flask_socketio import SocketIO, send, emit
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
socketio = SocketIO(app)
db = SQLAlchemy(app)

# Database model for storing messages
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    text = db.Column(db.String(500), nullable=False)

# Route for login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect('/chat')
    return render_template('login.html')

# Route for chat
@app.route('/chat')
def chat():
    if 'username' not in session:
        return redirect('/')
    messages = Message.query.all()
    return render_template('chat.html', messages=messages, username=session['username'])

# Handle messages
@socketio.on('message')
def handle_message(data):
    username = data['username']
    text = data['text']
    new_message = Message(username=username, text=text)
    db.session.add(new_message)
    db.session.commit()
    send({'username': username, 'text': text}, broadcast=True)

# Handle chat reset
@socketio.on('reset')
def handle_reset():
    print("Chat reset requested!")
    emit('message', {'username': 'System', 'text': 'Chat has been reset.'}, broadcast=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("Server starting...")
    socketio.run(app, debug=True)
