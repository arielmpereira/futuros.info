from flask import render_template, redirect, url_for, flash, request
from app import app
from flask_login import login_user, logout_user, login_required, current_user
from app.models import Paginas, Users
from .forms import SignupForm, LoginForm, ContactoForm
from urllib.parse import urlparse


@app.route('/')
def home():
    return render_template('index.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = Users.get_by_email(form.email.data)
        if user is not None and user.check_password(form.password.data):
            login_user(user)
            flash('Ingreso exitoso', 'success')
            return redirect(url_for('home'))
        else:
            flash('Email o contraseña incorrectos', 'danger')
    return render_template('login_form.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Cierre de sesión exitoso', category='success')
    return redirect(url_for('home'))


@app.route('/signup', methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = SignupForm()
    error = None
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        # Comprobamos que no hay ya un usuario con ese email
        user = Users.get_by_email(email)
        if user is not None:
            flash(f'El email {email} ya está siendo utilizado por otro usuario', category='danger')

        else:
            # Creamos el usuario y lo guardamos
            user = Users(name=name, email=email)
            user.set_password(password)
            user.save()
            # Dejamos al usuario logueado
            login_user(user, remember=True)
            next_page = request.args.get('next', None)
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('home')
            return redirect(next_page)

    return render_template("signup_form.html", form=form, error=error)

