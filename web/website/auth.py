from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from .models import User
from . import db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Đăng nhập thành công!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Mật khẩu không đúng, thử lại lần nữa', category='error')
        else:
            flash('Tài khoản hiện chưa được đăng ký', category='error')

    data = request.form
    print(data)
    return render_template('login.html', user=current_user)

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(username=username).first()

        if user:
            flash('Tài khoản đã tồn tại', category='error')
        elif len(password1) < 5:
            flash('Mật khẩu phải có tối thiểu 5 ký tự', category='error')
        elif password1 != password2:
            flash('Mật khẩu không đồng nhất', category='error')
        else:
            new_user = User(username=username, email=email, password=generate_password_hash(password1, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash('Tạo tài khoản thành công!', category='success')
            login_user(new_user)
            return redirect(url_for('views.home'))

    return render_template('sign_up.html', user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.home'))

@auth.route('technical-analysis', methods=['GET', 'POST'])
@login_required
def technical_analysis():
    urls = {
        'Mô hình dự đoán': 'static/AAPL.jpg',
        'Giá đóng cửa': 'static/AAPL_Close.jpg',
        'Khối lượng giao dịch': 'static/AAPL_Volume.jpg',
        'Trung bình di động': 'static/AAPL_MA.jpg'
    }
    technical = 'Mô hình dự đoán'

    if request.method == 'POST':
        technical = request.form.get('technical-list')

    return render_template('technical_analysis.html', 
                           user=current_user, 
                           chart_name=technical, 
                           url=urls[technical])