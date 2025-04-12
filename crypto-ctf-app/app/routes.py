from flask import Blueprint, render_template, redirect, request, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .models import User, Challenge, Submission
from flask import session, redirect, url_for, flash
bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    if 'user_id' in session:
        user = db.session.get(User, session['user_id'])
        if user:
            challenges = Challenge.query.all()
            solved_ids = [s.challenge_id for s in Submission.query.filter_by(user_id=user.id).all()]
            return render_template('dashboard.html', user=user, challenges=challenges, solved=solved_ids)
        else:
            # User not found in DB, clear session
            session.pop('user_id')

    return render_template('index.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        if User.query.filter_by(username=username).first():
            return 'Username already exists!'
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('main.login'))
    return render_template('register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, request.form['password']):
            session['user_id'] = user.id
            return redirect(url_for('main.index'))
        return 'Invalid credentials'
    return render_template('login.html')

@bp.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('main.index'))

@bp.route('/challenge/<int:id>', methods=['GET', 'POST'])
def challenge(id):
    challenge = Challenge.query.get_or_404(id)
    user = db.session.get(User, session['user_id'])

    if request.method == 'POST':
        flag = request.form['answer'].strip()
        already_solved = Submission.query.filter_by(user_id=user.id, challenge_id=challenge.id).first()

        if already_solved:
            return render_template('challenge.html', challenge=challenge, message='Already solved.')

        if flag == challenge.flag:
            user.score += challenge.points
            db.session.add(user)
            db.session.add(Submission(user_id=user.id, challenge_id=challenge.id))
            db.session.commit()
            return render_template('challenge.html', challenge=challenge, message='Correct!')

        return render_template('challenge.html', challenge=challenge, message='Incorrect flag.')

    return render_template('challenge.html', challenge=challenge)

@bp.route('/scoreboard')
def scoreboard():
    users = User.query.order_by(User.score.desc()).all()
    return render_template('scoreboard.html', users=users)

@bp.route('/leaderboard')
def leaderboard():
    users = User.query.all()
    leaderboard = sorted(users, key=lambda u: len(u.solved_challenges), reverse=True)
    return render_template('leaderboard.html', leaderboard=leaderboard)


@bp.route('/add-challenge', methods=['GET', 'POST'])
def add_challenge():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        flag = request.form['flag']
        points = request.form['points']

        new_challenge = Challenge(
            title=title,
            description=description,
            flag=flag,
            points=int(points)
        )
        db.session.add(new_challenge)
        db.session.commit()
        return redirect(url_for('main.index'))

    return render_template('add_challenge.html')
