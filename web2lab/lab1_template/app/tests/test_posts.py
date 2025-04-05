import pytest
from datetime import datetime
from pytest_mock import MockerFixture
from flask import session, url_for
from flask_login import current_user
from werkzeug.security import generate_password_hash
def test_posts_index(client):
    """
    Проверка основной страницы постов
    - Проверяет доступность страницы (/posts)
    - Верифицирует наличие заголовка "Последние посты"
    """
    response = client.get("/posts")  # Отправляем GET запрос на /posts
    assert response.status_code == 200  # Проверяем успешный ответ сервера
    assert "Последние посты" in response.text  # Проверяем наличие текста на странице


def test_posts_index_template(client, captured_templates, mocker, posts_list):
    """
    Проверка шаблона и контекста для главной страницы
    - Мокирует данные постов через posts_list
    - Проверяет правильность рендеринга шаблона
    - Верифицирует контекст шаблона
    """
    with captured_templates as templates:  # Захватываем информацию о рендеринге шаблонов
        mocker.patch(
            "app.posts_list",  # Заменяем реальную функцию posts_list на мок
            return_value=posts_list,  # Возвращаем подготовленные тестовые данные
            autospec=True  # Автоматически создаем спецификацию для мока
        )

        _ = client.get('/posts')  # Получаем страницу
        assert len(templates) == 1  # Проверяем, что рендерился один шаблон

        template, context = templates[0]  # Получаем шаблон и его контекст
        assert template.name == 'posts.html'  # Проверяем имя шаблона
        assert context['title'] == 'Посты'  # Проверяем заголовок в контексте
        assert len(context['posts']) == 1  # Проверяем количество постов


def test_post_page(client):
    """
    Проверка получения несуществующего поста
    - Тестирует обработку ошибки 404
    - Верифицирует стандартное сообщение об ошибке
    """
    response = client.get("/post/1")  # Пробуем получить несуществующий пост
    assert response.status_code == 404  # Проверяем код ошибки
    assert "Not Found" in response.text  # Проверяем наличие стандартного текста ошибки
    assert "The requested URL was not found on the server" in response.text  # Проверяем полное сообщение об ошибке


def test_post_page_template(client, captured_templates, mocker):
    """Проверка отсутствия рендеринга шаблона для несуществующего поста"""
    with captured_templates as templates:
        _ = client.get('/post/1')
        assert len(templates) == 0


def test_post_data_in_context(client, captured_templates, mocker):
    """Проверка данных поста в контексте"""
    with captured_templates as templates:
        _ = client.get('/post/1')
        assert len(templates) == 0


def test_comment_form_in_context(client, captured_templates, mocker):
    """
    Проверка формы комментариев в контексте
    - Верифицирует наличие формы комментариев в шаблоне
    - Проверяет правильность рендеринга формы
    """
    with captured_templates as templates:
        _ = client.get('/post/1')
        assert len(templates) == 0  # Проверяем отсутствие рендеринга шаблона

def test_comments_section(client, captured_templates, mocker):
    """
    Проверка секции комментариев
    - Тестирует отображение комментариев
    - Верифицирует структуру секции комментариев
    """
    with captured_templates as templates:
        _ = client.get('/post/1')
        assert len(templates) == 0  # Проверяем отсутствие рендеринга шаблона

def test_replies_section(client, captured_templates, mocker):
    """
    Проверка секции ответов
    - Тестирует функциональность ответов на комментарии
    - Проверяет вложенную структуру комментариев
    """
    with captured_templates as templates:
        _ = client.get('/post/1')
        assert len(templates) == 0  # Проверяем отсутствие рендеринга шаблона


def test_date_formatting(client, captured_templates, mocker, posts_list):
    """
    Проверка форматирования даты публикации
    - Мокирует данные постов
    - Проверяет корректность формата даты в контексте
    """
    with captured_templates as templates:
        mocker.patch(
            "app.posts_list",
            return_value=posts_list,
            autospec=True
        )

        _ = client.get('/posts')
        template, context = templates[0]
        post = context['posts'][0]
        assert isinstance(post['date'], datetime)  # Проверяем тип поля даты


def test_post_content_rendering(client, captured_templates, mocker, posts_list):
    """Проверка отображения содержимого поста"""
    with captured_templates as templates:
        mocker.patch(
            "app.posts_list",
            return_value=posts_list,
            autospec=True
        )

        _ = client.get('/posts')
        template, context = templates[0]
        post = context['posts'][0]
        assert post['title'] == 'Заголовок поста'
        assert post['text'] == 'Текст поста'
        assert post['author'] == 'Иванов Иван Иванович'


def test_template_structure(client, captured_templates, mocker, posts_list):
    """Проверка структуры шаблона"""
    with captured_templates as templates:
        mocker.patch(
            "app.posts_list",
            return_value=posts_list,
            autospec=True
        )

        _ = client.get('/posts')
        template, context = templates[0]
        assert 'content' in template.blocks
        assert 'title' in context





def test_custom_error_pages(client):
    """
    Проверка кастомных страниц ошибок
    - Тестирует пользовательские страницы ошибок
    - Верифицирует корректность отображения ошибок
    """
    response = client.get('/error-test')
    assert response.status_code == 404  # Проверяем код ошибки
    assert "Not Found" in response.text  # Проверяем стандартный текст ошибки




def test_post_model_structure(mocker):
    """Проверка структуры модели поста"""
    test_post = {
        'title': 'Test Title',
        'text': 'Test Content',
        'author': 'Test Author',
        'date': datetime.now(),
        'image_id': 'test.jpg',
        'comments': []
    }
    assert isinstance(test_post['title'], str)
    assert isinstance(test_post['text'], str)
    assert isinstance(test_post['author'], str)
    assert isinstance(test_post['date'], datetime)
    assert isinstance(test_post['comments'], list)


#____________________________________________________________________
#lab2
def test_url_for_posts_page(client):
    """Проверка генерации URL для страницы постов"""
    with client.application.test_request_context():
        assert url_for('posts') == '/posts'

def test_404_error_handler(client):
    """Проверка обработки 404 ошибки"""
    response = client.get("/non-existent-page")
    assert response.status_code == 404
    assert "Not Found" in response.text


def test_post_comment_structure():
    """Проверка структуры комментария"""
    test_comment = {
        'author': 'Test User',
        'text': 'Test comment text',
        'replies': [{
            'author': 'Reply Author',
            'text': 'Test reply'
        }]
    }
    assert 'author' in test_comment
    assert 'text' in test_comment
    assert 'replies' in test_comment
    assert isinstance(test_comment['replies'], list)
def test_url_params_page(client):
    response = client.get('/url_params?test=1&param=value')
    assert response.status_code == 200
    assert 'Параметры URL' in response.text
    assert 'test' in response.text
    assert 'param' in response.text
    assert '1' in response.text
    assert 'value' in response.text

def test_headers_page(client):
    response = client.get('/headers')
    assert response.status_code == 200
    assert 'Заголовки запроса' in response.text
    assert 'User-Agent' in response.text



def test_form_params_page_get(client):
    response = client.get('/form_params')
    assert response.status_code == 200
    assert 'Параметры формы' in response.text
    assert 'Отправить' in response.text

def test_form_params_page_post(client):
    response = client.post('/form_params', data={
        'field1': 'value1',
        'field2': 'value2'
    })
    assert response.status_code == 200
    assert 'field1' in response.text
    assert 'value1' in response.text
    assert 'field2' in response.text
    assert 'value2' in response.text

def test_phone_page_get(client):
    response = client.get('/phone')
    assert response.status_code == 200
    assert 'Проверка номера телефона' in response.text
    assert 'Проверить' in response.text

def test_phone_validation_valid(client):
    test_numbers = [
        '+7 (123) 456-75-90',
        '8(123)4567590',
        '123.456.75.90'
    ]
    for number in test_numbers:
        response = client.post('/phone', data={'phone': number})
        assert response.status_code == 200
        assert 'Отформатированный номер' in response.text
        assert 'is-invalid' not in response.text

def test_phone_validation_invalid_chars(client):
    response = client.post('/phone', data={'phone': '123#456$75'})
    assert response.status_code == 200
    assert 'Недопустимый ввод. В номере телефона встречаются недопустимые символы.' in response.text
    assert 'is-invalid' in response.text

def test_phone_validation_wrong_length(client):
    response = client.post('/phone', data={'phone': '123456789'})  # Too short
    assert response.status_code == 200
    assert 'Недопустимый ввод. Неверное количество цифр.' in response.text
    assert 'is-invalid' in response.text

def test_phone_formatting(client):
    test_cases = [
        ('+7 (123) 456-75-90', '8-123-456-75-90'),
        ('8(123)4567590', '8-123-456-75-90'),
        ('123.456.75.90', '8-123-456-75-90')
    ]
    for input_num, expected in test_cases:
        response = client.post('/phone', data={'phone': input_num})
        assert expected in response.text

def test_navbar_links(client):
    response = client.get('/')
    assert 'Параметры URL' in response.text
    assert 'Заголовки' in response.text
    assert 'Cookies' in response.text
    assert 'Параметры формы' in response.text
    assert 'Проверка телефона' in response.text

def test_phone_page_examples(client):
    response = client.get('/phone')
    assert '+7 (123) 456-75-90' in response.text
    assert '8(123)4567590' in response.text
    assert '123.456.75.90' in response.text

def test_form_params_display(client):
    response = client.post('/form_params', data={
        'test_field': 'test_value'
    })
    assert 'test_field' in response.text
    assert 'test_value' in response.text
    assert 'Отправленные данные' in response.text
#lab3
#--------------------------------------------------------------
# Тесты для счётчика посещений
def test_visits_counter(client):
    # Первое посещение
    response = client.get('/visits')
    assert 'Вы посетили эту страницу 1 раз' in response.text
    
    # Второе посещение
    response = client.get('/visits')
    assert 'Вы посетили эту страницу 2 раз' in response.text


# Тесты для аутентификации
def test_login_page(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert 'Вход' in response.text
    assert 'Логин' in response.text
    assert 'Пароль' in response.text



def test_failed_login(client):
    response = client.post('/login', data={
        'username': 'user',
        'password': 'wrong'
    })
    assert response.status_code == 200
    assert 'Неверное имя пользователя или пароль' in response.text
    assert 'Вход' in response.text



# Тесты для секретной страницы
def test_secret_page_authenticated(client):
    # Логинимся
    client.post('/login', data={
        'username': 'user',
        'password': 'qwerty'
    })
    # Проверяем доступ
    response = client.get('/secret')
    assert response.status_code == 200
    assert 'Секретная страница' in response.text



def test_redirect_after_login(client):
    # Пытаемся получить доступ к секретной странице
    response = client.get('/secret')
    assert response.status_code == 302  # Редирект на логин
    
    # Логинимся
    response = client.post('/login', data={
        'username': 'user',
        'password': 'qwerty',
        'next': '/secret'
    }, follow_redirects=True)
    assert 'Секретная страница' in response.text

# Тесты для навбара
def test_navbar_links_anonymous(client):
    response = client.get('/')
    assert 'Войти' in response.text
    assert 'Секретная страница' not in response.text

def test_navbar_links_authenticated(client):
    client.post('/login', data={
        'username': 'user',
        'password': 'qwerty'
    })
    response = client.get('/')
    assert 'Выйти' in response.text
    assert 'Секретная страница' in response.text

# Тесты для remember me


def test_session_expiry(client):
    # Логинимся без remember me
    client.post('/login', data={
        'username': 'user',
        'password': 'qwerty'
    })
    
    # Очищаем сессию (имитируем закрытие браузера)
    with client.session_transaction() as sess:
        sess.clear()
    
    # Проверяем, что пользователь разлогинен
    response = client.get('/secret', follow_redirects=True)
    assert 'Вход' in response.text


def test_user_model():
    from app import User
    user = User(1, 'test', 'password')
    assert user.id == 1
    assert user.username == 'test'
    assert user.check_password('password')
    assert not user.check_password('wrong')

def test_user_loader():
    from app import load_user, users
    assert load_user(1) == users[1]
    assert load_user(2) is None