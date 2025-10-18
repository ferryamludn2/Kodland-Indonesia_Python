import os
import requests
import random
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sqlalchemy import func
from flask_sqlalchemy import SQLAlchemy
from bcrypt import hashpw, checkpw, gensalt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'kunciFerryAMALudin'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'quiz.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from models import db, User, Question, Answer
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
def get_weather(city):
    try:
        geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
        geo_params = {'name': city, 'count': 1, 'language': 'en', 'format': 'json'}
        geo_response = requests.get(geocoding_url, params=geo_params)
        geo_response.raise_for_status()
        geo_data = geo_response.json()

        if not geo_data.get('results'):
            return None

        location = geo_data['results'][0]
        latitude = location['latitude']
        longitude = location['longitude']
        weather_url = "https://api.open-meteo.com/v1/forecast"
        weather_params = {
            'latitude': latitude,
            'longitude': longitude,
            'daily': 'temperature_2m_max,temperature_2m_min',
            'timezone': 'auto',
            'forecast_days': 3
        }
        weather_response = requests.get(weather_url, params=weather_params)
        weather_response.raise_for_status()
        data = weather_response.json()
        
        forecasts = []
        daily_data = data['daily']
        for i in range(len(daily_data['time'])):
            forecast = {
                'date': daily_data['time'][i],
                'day_name': datetime.strptime(daily_data['time'][i], '%Y-%m-%d').strftime('%A'),
                'temp_day': daily_data['temperature_2m_max'][i],
                'temp_night': daily_data['temperature_2m_min'][i]
            }
            forecasts.append(forecast)
        return forecasts
    except requests.exceptions.RequestException as e:
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    weather_data = None
    city = 'Jakarta'
    if request.method == 'POST':
        city = request.form.get('city')
    
    weather_data = get_weather(city)
    return render_template('index.html', weather=weather_data, city=city)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        nickname = request.form.get('nickname')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not all([username, nickname, password, confirm_password]):
            flash('Semua kolom harus diisi!', 'danger')
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('Kata sandi tidak cocok!', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(username=username).first():
            flash('Username sudah digunakan.', 'danger')
            return redirect(url_for('register'))

        if User.query.filter_by(nickname=nickname).first():
            flash('Nickname sudah digunakan.', 'danger')
            return redirect(url_for('register'))

        if len(password) < 6:
            flash('Kata sandi harus memiliki minimal 6 karakter.', 'danger')
            return redirect(url_for('register'))
        hashed_password = hashpw(password.encode('utf-8'), gensalt())
        new_user = User(username=username, nickname=nickname, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registrasi berhasil! Silakan login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and checkpw(password.encode('utf-8'), user.password):
            login_user(user)
            flash('Login berhasil!', 'success')
            return redirect(url_for('quiz'))
        else:
            flash('Login gagal. Periksa kembali username dan password Anda.', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('answered_questions', None)
    session.pop('streak', None)
    flash('Anda telah logout.', 'info')
    return redirect(url_for('index'))

@app.route('/quiz', methods=['GET', 'POST'])
@login_required
def quiz():
    if request.method == 'GET' and ('start_time' not in session or request.args.get('new_game')):
        session['start_time'] = datetime.utcnow().isoformat()
        session['current_quiz_score'] = 0
        session['answered_questions'] = []
        session['streak'] = 0
        if request.args.get('new_game'):
            return redirect(url_for('quiz'))
    if request.method == 'POST':
        question_id = request.form.get('question_id')
        selected_answer_id = request.form.get('answer')

        session['answered_questions'].append(int(question_id))
        session.modified = True
        answer = Answer.query.get(selected_answer_id)
        
        if answer and answer.is_correct:
            session['streak'] += 1
            base_score = 10
            bonus = session['streak'] * 2
            score_earned = base_score + bonus
            session['current_quiz_score'] += score_earned
            flash(f'Jawaban Benar! +{score_earned} poin (Streak x{session["streak"]})', 'success')
        else:
            session['streak'] = 0
            flash('Jawaban Salah!', 'danger')

        return redirect(url_for('quiz'))

    answered_ids = session.get('answered_questions', [])
    random_question = Question.query.filter(Question.id.notin_(answered_ids)).order_by(func.random()).first()

    if not random_question:
        return redirect(url_for('quiz_results'))

    return render_template('quiz.html', question=random_question)

@app.route('/quiz/results')
@login_required
def quiz_results():
    final_score = session.get('current_quiz_score', 0)
    start_time_str = session.get('start_time')

    if not start_time_str:
        return redirect(url_for('quiz'))
    start_time = datetime.fromisoformat(start_time_str)
    end_time = datetime.utcnow()
    duration = end_time - start_time
    duration_seconds = int(duration.total_seconds())
    if final_score > current_user.total_score:
        current_user.total_score = final_score
        db.session.commit()
        flash('Skor tertinggi baru telah disimpan!', 'success')
    session.pop('start_time', None)
    session.pop('current_quiz_score', None)
    session.pop('answered_questions', None)
    session.pop('streak', None)

    return render_template('quiz_results.html', score=final_score, duration=duration_seconds)

@app.route('/leaderboard')
@login_required
def leaderboard():
    users = User.query.order_by(User.total_score.desc()).all()
    return render_template('leaderboard.html', users=users)
def setup_database(app):
    with app.app_context():
        instance_path = os.path.dirname(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', ''))
        if not os.path.exists(instance_path):
            os.makedirs(instance_path)
            
        db.create_all()
        if Question.query.count() < 20:
            db.session.query(Answer).delete()
            db.session.query(Question).delete()
            questions_data = [
                {"text": "Manakah library Python yang populer untuk Machine Learning?", "answers": [("Scikit-learn", True), ("Flask", False), ("Requests", False), ("Pygame", False)]},
                {"text": "Fungsi apa yang digunakan untuk mencetak output di Python?", "answers": [("print()", True), ("console.log()", False), ("System.out.println()", False), ("echo", False)]},
                {"text": "Tipe data apa yang digunakan untuk menyimpan teks di Python?", "answers": [("String", True), ("Integer", False), ("Boolean", False), ("Float", False)]},
                {"text": "Library Python manakah yang digunakan untuk membuat aplikasi web?", "answers": [("Flask", True), ("NumPy", False), ("Pandas", False), ("TensorFlow", False)]},
                {"text": "Struktur data Python mana yang bersifat 'mutable' (dapat diubah)?", "answers": [("List", True), ("Tuple", False), ("String", False), ("Frozenset", False)]},
                {"text": "Apa kepanjangan dari AI?", "answers": [("Artificial Intelligence", True), ("Automated Interface", False), ("Algorithmic Inquiry", False), ("Applied Information", False)]},
                {"text": "Manakah dari berikut ini yang merupakan sub-bidang dari AI?", "answers": [("Machine Learning", True), ("Cybersecurity", False), ("Web Development", False), ("Data Entry", False)]},
                {"text": "Library Python mana yang sangat populer untuk komputasi numerik?", "answers": [("NumPy", True), ("Django", False), ("Kivy", False), ("Pillow", False)]},
                {"text": "Apa itu 'Deep Learning'?", "answers": [("Sub-bidang Machine Learning yang menggunakan neural network dengan banyak lapisan", True), ("Metode untuk menyimpan data di cloud", False), ("Teknik hacking", False), ("Cara membuat game 3D", False)]},
                {"text": "Manakah framework Deep Learning yang dikembangkan oleh Google?", "answers": [("TensorFlow", True), ("PyTorch", False), ("Theano", False), ("Caffe", False)]},
                {"text": "Apa fungsi dari library 'Pandas'?", "answers": [("Analisis dan manipulasi data", True), ("Membuat antarmuka grafis", False), ("Mengirim email", False), ("Mengontrol robot", False)]},
                {"text": "Dalam Machine Learning, apa itu 'supervised learning'?", "answers": [("Belajar dari data yang sudah diberi label", True), ("Belajar dari data tanpa label", False), ("Belajar melalui trial and error", False), ("Belajar dari video tutorial", False)]},
                {"text": "Operator apa yang digunakan untuk eksponensial (pangkat) di Python?", "answers": [("**", True), ("^", False), ("%", False), ("//", False)]},
                {"text": "Bagaimana cara menulis komentar satu baris di Python?", "answers": [("Dengan tanda #", True), ("Dengan tanda //", False), ("Dengan tanda /* ... */", False), ("Dengan tanda <!-- ... -->", False)]},
                {"text": "Manakah framework Deep Learning yang dikembangkan oleh Facebook?", "answers": [("PyTorch", True), ("Keras", False), ("MXNet", False), ("CNTK", False)]},
                {"text": "Apa itu 'Natural Language Processing' (NLP)?", "answers": [("Cabang AI yang berfokus pada interaksi komputer dengan bahasa manusia", True), ("Proses mengoptimalkan database", False), ("Bahasa pemrograman baru", False), ("Prosesor komputer", False)]},
                {"text": "Tipe data apa yang hanya bisa bernilai 'True' atau 'False'?", "answers": [("Boolean", True), ("String", False), ("List", False), ("Dictionary", False)]},
                {"text": "Bagaimana cara mendapatkan panjang sebuah list bernama 'my_list'?", "answers": [("len(my_list)", True), ("my_list.length()", False), ("size(my_list)", False), ("my_list.size", False)]},
                {"text": "Apa itu 'API' dalam konteks pengembangan web?", "answers": [("Application Programming Interface", True), ("Automated Python Installer", False), ("Applied Program Interaction", False), ("Antarmuka Pengguna Aplikasi", False)]},
                {"text": "Library mana yang digunakan untuk visualisasi data seperti membuat grafik dan plot?", "answers": [("Matplotlib", True), ("SQLAlchemy", False), ("bcrypt", False), ("Pillow", False)]}
            ]

            for q_data in questions_data:
                question = Question(text=q_data["text"])
                db.session.add(question)
                for ans_text, is_correct in q_data["answers"]:
                    answer = Answer(question=question, text=ans_text, is_correct=is_correct)
                    db.session.add(answer)

            db.session.commit()
           
if __name__ == '__main__':
    setup_database(app)
    app.run(debug=True)
