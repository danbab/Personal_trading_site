from flask import Flask, request, flash, url_for, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.sqlite3'
app.config['SECRET_KEY'] = 'project'
app.config['UPLOAD_FOLDER'] = './static/uploads/'

db = SQLAlchemy(app)


class accounts(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    a_id = db.Column(db.String(30), nullable=False, unique=True)
    a_password = db.Column(db.String(30))
    a_nickname = db.Column(db.String(30), nullable=False, unique=True)

    def __init__(self, id, password, nickname):
        self.a_id = id
        self.a_password = password
        self.a_nickname = nickname


class posts(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    p_title = db.Column(db.String(30), nullable=False)
    p_keyword = db.Column(db.String(30), nullable=False)
    p_price = db.Column(db.String(30), nullable=False)
    p_seller = db.Column(db.String(30), nullable=False)
    p_description = db.Column(db.String(300))
    p_image1 = db.Column(db.String(30))
    p_soldOut = db.Column(db.Boolean, default=False)

    def __init__(self, title, price, keyword, description, seller, image1):
        self.p_title = title
        self.p_keyword = keyword
        self.p_price = price
        self.p_seller = seller
        self.p_description = description
        self.p_image1 = image1



class follows(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    f_follower = db.Column(db.String(30), nullable=False)
    f_followee = db.Column(db.String(30), nullable=False)

    def __init__(self, follower, followee):
        self.f_follower = follower
        self.f_followee = followee


@app.route('/')
def home():
    global signUpId
    global signUpPassword
    global signUpNickname
    global isIdDuplicate
    global isNicknameDuplicate

    global signInId
    global signInPassword

    global registerTitle
    global registerPrice
    global registerDescription
    global registerimage1


    global updateTitle
    global updatePrice
    global updateDescription
    global updateimage1


    signUpId = ''
    signUpPassword = ''
    signUpNickname = ''
    isIdDuplicate = True
    isNicknameDuplicate = True

    signInId = ''
    signInPassword = ''

    registerTitle = ''
    registerPrice = ''
    registerDescription = ''
    registerimage1 = ''


    updateTitle = ''
    updatePrice = ''
    updateDescription = ''
    updateimage1 = ''
    keyword='all'
    if keyword == 'all':
        list = posts.query.all()
        return render_template('search.html', list=list, keyword=keyword)
    elif keyword == 'keyword':
        temp = request.form['searchBar']
        return redirect(url_for('search', keyword=temp))
    else:
        if keyword == 'default':
            flash('키워드를 선택해주세요.')
            return redirect(url_for('search', keyword='all'))
        list = posts.query.filter_by(p_keyword=keyword)

    return render_template('home.html')


signUpId = ''
signUpPassword = ''
signUpNickname = ''
isIdDuplicate = True
isNicknameDuplicate = True


@app.route('/signUp/', methods=['GET', 'POST'])
def signUp():
    global signUpId
    global signUpPassword
    global signUpNickname
    global isIdDuplicate
    global isNicknameDuplicate

    if request.method == 'POST':
        if not request.form['a_id'] or not request.form['a_password'] or not request.form['a_nickname']:
            flash('아이디, 비밀번호, 닉네임 모두를 입력해주세요.', 'error')
            signUpId = request.form['a_id']
            signUpPassword = request.form['a_password']
            signUpNickname = request.form['a_nickname']

        else:
            account = accounts(request.form['a_id'], request.form['a_password'], request.form['a_nickname'])
            db.session.add(account)
            db.session.commit()
            flash('회원가입에 성공했습니다.')
            signUpId = ''
            signUpPassword = ''
            signUpNickname = ''
            isIdDuplicate = True
            isNicknameDuplicate = True
            return redirect(url_for('home'))
    return render_template('signUp.html', id=signUpId, password=signUpPassword, nickname=signUpNickname)


signInId = ''
signInPassword = ''


@app.route('/signIn/', methods=['GET', 'POST'])
def signIn():
    global signInId
    global signInPassword
    if request.method == 'POST':
        if not request.form['a_id'] or not request.form['a_password']:
            flash('아이디, 비밀번호 모두를 입력해주세요.', 'error')
            signInId = request.form['a_id']
            signInPassword = request.form['a_password']
            return redirect(url_for('signIn'))

        account = accounts.query.filter_by(a_id=request.form['a_id']).first()
        if not account:
            flash('존재하지 않는 아이디입니다.')
            signInId = ''
            signInPassword = ''
            return redirect(url_for('signIn'))
        elif account.a_password != request.form['a_password']:
            signInId = request.form['a_id']
            signInPassword = ''
            flash('비밀번호를 다시 확인해주세요.')
            return redirect(url_for('signIn'))
        else:
            signInId = ''
            signInPassword = ''
            flash('로그인을 성공했습니다.')
            session['nickname'] = account.a_nickname
            return redirect(url_for('home'))
    return render_template('signIn.html', id=signInId, password=signInPassword)


@app.route('/signOut/', methods=['GET', 'POST'])
def signOut():
    session.pop('nickname', None)
    flash('로그아웃을 성공했습니다.')
    return redirect(url_for('home'))

registerTitle = ''
registerPrice = ''
registerDescription = ''
registerimage1 = ''

@app.route('/register/', methods=['GET', 'POST'])
def register():
    global registerTitle
    global registerPrice
    global registerDescription
    global registerimage1

    if request.method == 'POST':
        if not request.form['p_title'] or not request.form['p_price'] or request.form['p_keyword'] == '키워드':
            flash('이름, 금액, 키워드를 작성해야합니다.')
            registerTitle = request.form['p_title']
            registerPrice = request.form['p_price']
            registerDescription = request.form['p_description']
        else:
            if request.files['p_image1']:
                f1 = request.files['p_image1']
                registerimage1 = secure_filename(f1.filename)
                f1.save(os.path.join(app.config['UPLOAD_FOLDER'], registerimage1))


            post = posts(request.form['p_title'], request.form['p_price'], request.form['p_keyword'],
                         request.form['p_description'], session['nickname'],
                         registerimage1)
            db.session.add(post)
            db.session.commit()

            registerTitle = ''
            registerPrice = ''
            registerDescription = ''
            registerimage1 = ''

            flash('게시물 등록을 성공했습니다.')
            return redirect(url_for('profile', nickname=session['nickname']))
    return render_template('register.html', title=registerTitle, price=registerPrice, description=registerDescription)


@app.route('/search/<keyword>', methods=['GET', 'POST'])
def search(keyword):
    if keyword == 'all':
        list = posts.query.all()
        return render_template('search.html', list=list, keyword=keyword)
    elif keyword == 'keyword':
        temp = request.form['searchBar']
        return redirect(url_for('search', keyword=temp))
    else:
        if keyword == 'default':
            flash('키워드를 선택해주세요.')
            return redirect(url_for('search', keyword='all'))
        list = posts.query.filter_by(p_keyword=keyword)
        return render_template('search.html', list=list, keyword=keyword)


@app.route('/detail/<id>', methods=['GET', 'POST'])
def detail(id):
    post = posts.query.filter_by(id=id).first()
    return render_template('detail.html', post=post)


@app.route('/image/<name>', methods=['GET', 'POST'])
def image(name):
    return render_template('image.html', image=name)


@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    post = posts.query.filter_by(id=id).first()
    return render_template('edit.html', title=post.p_title, price=post.p_price, description=post.p_description, id=id)


updateTitle = ''
updatePrice = ''
updateDescription = ''
updateimage1 = ''

@app.route('/update/<id>', methods=['GET', 'POST'])
def update(id):
    global updateTitle
    global updatePrice
    global updateDescription
    global updateimage1

    if not request.form['p_title'] or not request.form['p_price'] or request.form['p_keyword'] == '키워드':
        flash('이름, 금액, 키워드를 작성해야합니다.')
        updateTitle = request.form['p_title']
        updatePrice = request.form['p_price']
        updateDescription = request.form['p_description']
        return render_template('edit.html', title=updateTitle, price=updatePrice, description=updateDescription, id=id)
    else:
        if request.files['p_image1']:
            f1 = request.files['p_image1']
            updateimage1 = f1.filename
            f1.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f1.filename)))


        post = posts.query.filter_by(id=id).first()
        post.id = id
        post.p_title = request.form['p_title']
        post.p_keyword = request.form['p_keyword']
        post.p_price = request.form['p_price']
        post.p_seller = session['nickname']
        post.p_description = request.form['p_description']
        post.p_image1 = updateimage1
        post.p_soldOut = False
        db.session.commit()

        updateTitle = ''
        updatePrice = ''
        updateDescription = ''
        updateimage1 = ''
        flash('게시글수정 성공했습니다.')
        return redirect(url_for('detail', id=id))


@app.route('/soldOut/<id>', methods=['GET', 'POST'])
def soldOut(id):
    post = posts.query.filter_by(id=id).first()
    post.p_soldOut = True
    post.p_image1 = ''
    db.session.commit()
    flash('판매 완료')
    return redirect(url_for('detail', id=id))


@app.route('/profile/<nickname>', methods=['GET', 'POST'])
def profile(nickname):
    list = posts.query.filter_by(p_seller=nickname)
    follow = follows.query.filter_by(f_follower=session['nickname'], f_followee=nickname)
    return render_template('profile.html', list=list, nickname=nickname, follow=follow)


@app.route('/follow/<nickname>', methods=['GET', 'POST'])
def follow(nickname):
    follow = follows.query.filter_by(f_follower=nickname)
    return render_template('follow.html', follow=follow)


@app.route('/following/<nickname>', methods=['GET', 'POST'])
def following(nickname):
    follow = follows(session['nickname'], nickname)
    db.session.add(follow)
    db.session.commit()
    flash('팔로우 성공했습니다.')
    return redirect(url_for('follow', nickname=session['nickname']))


@app.route('/warning/<type>')
def warning(type):
    if type == 'register':
        flash('게시물을 등록하려면 로그인이 필요합니다.')
    elif type == 'profile':
        flash('게시물을 관리하려면 로그인이 필요합니다.')
    elif type == 'follow':
        flash('팔로우를 보려면 로그인이 필요합니다.')
    return redirect(url_for('signIn'))


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)