from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///messenger.db'
db = SQLAlchemy(app)

# Модель пользователя
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Модель сообщения
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('messages', lazy=True))

# Главная страница (чат)
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    messages = Message.query.all()
    return render_template('index.html', user=user, messages=messages)

# Регистрация
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nickname = request.form['nickname']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        
        # Создаем нового пользователя
        new_user = User(nickname=nickname, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('login'))
    return render_template('register.html')

# Вход в систему
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nickname = request.form['nickname']
        password = request.form['password']
        
        # Поиск пользователя по введенному нику
        user = User.query.filter_by(nickname=nickname).first()
        
        # Если пользователь найден и пароль совпадает
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id  # Сохранение ID пользователя в сессии
            return redirect(url_for('index'))  # Перенаправление на главную страницу
        else:
            # Если неверный ник или пароль, показываем сообщение
            return render_template('login.html', error="Неправильный ник или пароль")
    return render_template('login.html')

# Отправка сообщения
@app.route('/send', methods=['POST'])
def send_message():
    if 'user_id' in session:
        content = request.form['message']
        user_id = session['user_id']
        
        # Создание нового сообщения
        new_message = Message(content=content, user_id=user_id)
        db.session.add(new_message)
        db.session.commit()
        
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Создание таблиц, если их нет
    app.run(debug=True)
