from app.main import main
from flask import current_app, jsonify, request, Response
from app.utils import check_return
from app.exceptions import CodeNoneError, ParameterError, RequestFormatError, FindError
from app.utils import in_site_search, zhuishu_search, easo_search, http_get, code2openid, get_book_info
from app import db
from app.models import User, Book
from flask_login import login_user, login_required, current_user
import requests


@main.route("/", methods=['GET'])
@check_return(need_login=False)
def index():
    info = {
        "developer": "copie"
    }
    return info


@main.route('/login', methods=['POST'])
@check_return(need_login=False)
def login():
    code = request.json.get('code')
    if not isinstance(code, str):
        raise CodeNoneError
    open_id = code2openid(code)
    user = db.session.query(User).filter(User.login_id == open_id).first()
    if user is None:
        user = User(login_id=open_id)
        db.session.add(user)
        db.session.commit()
    login_user(user, remember=True)


@main.route('/search', methods=['GET'])
@check_return()
def search():

    try:
        search_type = str(request.args['searchType'])
        book_name = str(request.args['bookName'])
        page_no = int(request.args['pageNo'])
    except Exception as e:
        raise ParameterError from e

    if search_type == 'biquge':
        ret = in_site_search(book_name, page_no)
    elif search_type == 'zhuishu':
        ret = zhuishu_search(book_name, page_no)
    elif search_type == 'sou':
        ret = easo_search(book_name, page_no)
    else:
        raise ParameterError(f'search_type: {search_type}')

    return ret


@main.route('/getbookid', methods=['GET'])
@check_return()
def get_bookid():
    try:
        book_name = str(request.args['Name'])
        author = str(request.args['Author'])
    except Exception as e:
        raise ParameterError from e

    url = 'http://quapp.1122dh.com/BookAction.aspx'
    payload = {
        'action': 'bookid',
        'author': author,
        'bookname': book_name
    }
    data = http_get(url, payload)
    ret = {}
    bookid = None
    try:
        data = data.get('data')
        if data is None:
            raise FindError
        bookid = data['bookid']
    except FindError as e:
        raise FindError from e
    except Exception as e:
        raise RequestFormatError from e
    ret['bookid'] = bookid

    return ret


@main.route('/bookinfo', methods=['GET'])
@check_return()
def book_info():
    try:
        bookid = int(request.args['bookID'])
    except Exception as e:
        raise ParameterError from e
    ret = get_book_info(bookid)
    return ret


@main.route('/bookcontents', methods=['GET'])
@check_return()
def book_contents():
    try:
        bookid = int(request.args['bookID'])
    except Exception as e:
        raise ParameterError from e
    url = 'http://quapp.1122dh.com/book/{bookid}/'.format(bookid=bookid)

    data = http_get(url)
    ret = {}
    try:
        data = data['data']
        ret['data'] = data
    except Exception as e:
        raise RequestFormatError from e
    return ret


@main.route('/content', methods=['GET'])
@check_return()
def content():
    try:
        bookid = int(request.args['bookID'])
        chapter = int(request.args['chapter'])
    except Exception as e:
        raise ParameterError from e
    url = 'http://quapp.1122dh.com/book/{bookid}/{chapter}.html'.format(bookid=bookid, chapter=chapter)

    data = http_get(url)
    ret = {}
    try:
        data = data['data']
        ret['data'] = data
    except Exception as e:
        raise RequestFormatError from e
    return ret


@main.route('/booklist', methods=['GET'])
@check_return()
def book_list():
    user = current_user
    books = user.books
    books_info = [get_book_info(book.book_id) for book in books]
    return {'books': books_info}


@main.route('/addbook', methods=['GET'])
@check_return()
def add_book():
    try:
        bookid = int(request.args['bookID'])
    except Exception as e:
        raise ParameterError from e
    user = current_user
    book = Book(book_id=bookid, user=user)
    db.session.add(book)
    db.session.commit()


@main.route('/img', methods=['GET'])
def img():
    url = request.args['url']
    img = requests.get(url, timeout=10)
    return Response(img.content, mimetype="image/jpeg")
