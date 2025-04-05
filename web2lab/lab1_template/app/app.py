import random
import re
from functools import lru_cache
from flask import Flask, render_template, make_response, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from faker import Faker
from werkzeug.security import generate_password_hash, check_password_hash

fake = Faker()

app = Flask(__name__)
application = app
app.secret_key = 'your_secret_key_here'  # Замените на реальный секретный ключ

# Настройка Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Модель пользователя
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Создаем тестового пользователя
users = {
    1: User(1, 'user', 'qwerty')
}

@login_manager.user_loader
def load_user(user_id):
    return users.get(int(user_id))

images_ids = ['7d4e9175-95ea-4c5f-8be5-92a6b708bb3c',
              '2d2ab7df-cdbc-48a8-a936-35bba702def5',
              '6e12f3de-d5fd-4ebb-855b-8cbc485278b7',
              'afc2cfe7-5cac-4b80-9b9a-d5c65ef0c728',
              'cab5b7f2-774e-4884-a200-0c0180fa777f']

def generate_comments(replies=True):
    comments = []
    for _ in range(random.randint(1, 3)):
        comment = { 'author': fake.name(), 'text': fake.text() }
        if replies:
            comment['replies'] = generate_comments(replies=False)
        comments.append(comment)
    return comments

def generate_post(i):
    return {
        'title': 'Заголовок поста',
        'text': fake.paragraph(nb_sentences=100),
        'author': fake.name(),
        'date': fake.date_time_between(start_date='-2y', end_date='now'),
        'image_id': f'{images_ids[i]}.jpg',
        'comments': generate_comments()
    }

@lru_cache
def posts_list():
    return sorted([generate_post(i) for i in range(5)], key=lambda p: p['date'], reverse=True)

# Основные маршруты
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/posts')
def posts():
    return render_template('posts.html', title='Посты', posts=posts_list())

@app.route('/posts/<int:index>')
def post(index):
    p = posts_list()[index]
    return render_template('post.html', title=p['title'], post=p)

@app.route('/about')
def about():
    return render_template('about.html', title='Об авторе')

# Новые маршруты
@app.route('/visits')
def visits():
    session['visits'] = session.get('visits', 0) + 1
    return render_template('visits.html', visits=session['visits'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        
        user = None
        for u in users.values():
            if u.username == username:
                user = u
                break
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash('Вы успешно вошли в систему!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Неверное имя пользователя или пароль', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('index'))

@app.route('/secret')
@login_required
def secret():
    return render_template('secret.html')

# Остальные маршруты (url_params, headers, cookies, form_params, phone) остаются без изменений
@app.route('/url_params')
def url_params():
    return render_template('url_params.html', title='Параметры URL', params=request.args)

@app.route('/headers')
def headers():
    return render_template('headers.html', title='Заголовки', headers=request.headers)

@app.route('/cookies')
def cookies():
    response = make_response(render_template('cookies.html', title='Cookies', cookies=request.cookies))
    if 'test_cookie' not in request.cookies:
        response.set_cookie('test_cookie', 'test_value', max_age=60*60*24)
    else:
        response.delete_cookie('test_cookie')
    return response

@app.route('/form_params', methods=['GET', 'POST'])
def form_params():
    if request.method == 'POST':
        return render_template('form_params.html', title='Параметры формы', form_data=request.form)
    return render_template('form_params.html', title='Параметры формы')
@app.route('/phone', methods=['GET', 'POST'])
def phone():
    error = None
    formatted_phone = None
    
    if request.method == 'POST':
        phone_number = request.form.get('phone', '')
        
        # Remove all non-digit characters
        digits = re.sub(r'[^\d]', '', phone_number)
        
        # Check for invalid characters
        if not re.fullmatch(r'[\d\s\(\)\-\.\+]+', phone_number):
            error = 'Недопустимый ввод. В номере телефона встречаются недопустимые символы.'
        # Check digit count
        elif (phone_number.startswith(('+7', '8')) and len(digits) != 11) or \
             (not phone_number.startswith(('+7', '8')) and len(digits) != 10):
            error = 'Недопустимый ввод. Неверное количество цифр.'
        else:
            # Format the phone number
            if phone_number.startswith(('+7', '8')):
                digits = digits[1:]  # Remove country code for formatting
            formatted_phone = f"8-{digits[:3]}-{digits[3:6]}-{digits[6:8]}-{digits[8:]}"
    
    return render_template(
        'phone.html',
        title='Проверка номера телефона',
        error=error,
        formatted_phone=formatted_phone
    )
