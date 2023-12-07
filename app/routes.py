from flask import render_template, redirect, url_for, flash, request
from app import app
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, Paginas, Users, Tickets, ForexDaily, IndicesDaily, ComoditiesDaily
from .forms import SignupForm, LoginForm, ContactoForm
from urllib.parse import urlparse

from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd

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


@app.route('/actualizar_datos')
def actualizar_datos():
    # Obtener la lista de todos los tickets
    tickets = Tickets.query.all()

    # Iterar sobre cada ticket
    for ticket in tickets:
        mercado = ticket.mercado

        # Obtenemos la ultima fecha actualizacion del ticket
        ultima_fecha = obtener_ultima_fecha(mercado, ticket.ticket_id)

        # Obtenemos los datos de Yahoo Finance desde la última fecha hasta hoy
        df = obtener_datos_yahoo(ticket.ticket, ultima_fecha)

        if not df.empty:
            # Actualizar la tabla correspondiente
            actualizar_tabla(ticket.ticket_id, df, mercado)


def obtener_ultima_fecha(mercado, ticket_id):
    # Seleccionar la tabla correspondiente según el mercado
    if mercado == 'forex':
        tabla = ForexDaily
    elif mercado == 'indices':
        tabla = IndicesDaily
    else:
        tabla = ComoditiesDaily

    # Consultar la última fecha para el ticket_id en la tabla correspondiente
    ultima_fecha = tabla.query.filter_by(ticket_id=ticket_id).order_by(tabla.fecha.desc()).first()

    if ultima_fecha:
        return ultima_fecha.fecha
    else:
        return None


def obtener_datos_yahoo(symbol, start_date):
    # Definir la fecha de inicio como la última fecha registrada o una fecha inicial si es None
    start_date = start_date or datetime.now() - timedelta(days=365 * 15)  # 15 años atrás

    # Convertir la fecha de inicio a formato de cadena si es un objeto datetime
    if isinstance(start_date, datetime):
        start_date = start_date.strftime('%Y-%m-%d')

    # Obtener los datos de Yahoo Finance
    data = yf.download(symbol, start=start_date, end=datetime.now(), interval='1d')

    return data

def actualizar_tabla(ticket_id, df, mercado):
    # Determinar la tabla según el mercado
    if mercado == 'forex':
        tabla = ForexDaily
    elif mercado == 'indices':
        tabla = IndicesDaily
    else:
        tabla = ComoditiesDaily

    # Iterar sobre los datos del DataFrame y actualizar la base de datos
    for index, row in df.iterrows():
        registro = tabla.query.filter_by(ticket_id=ticket_id, fecha=row.name).first()

        # Comprobar si ya existe un registro para esa fecha y ticket_id
        if registro:
            pass
        else:
            # Crear un nuevo registro si no existe
            nuevo_registro = tabla(ticket_id=ticket_id, fecha=row.name, apertura=row['Open'], maximo=row['High'], minimo=row['Low'], cierre=row['Close'])
            db.session.add(nuevo_registro)

    # Commit para guardar los cambios en la base de datos
    db.session.commit()