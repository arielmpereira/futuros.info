from flask import render_template, redirect, url_for, flash, request
from app import app
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, Paginas, Users, Tickets, ForexDaily, IndicesDaily, CommoditiesDaily
from app.forms import SignupForm, LoginForm, ContactoForm
from urllib.parse import urlparse

from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd

import plotly.express as px
import plotly.io as pio

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


@app.route('/mercado-<string:mercado>')
def listar_tickets(mercado):
    tickets = Tickets.query.filter_by(mercado=mercado).all()
    return render_template('listar_tickets.html', tickets=tickets, mercado=mercado)

@app.route('/activo-<int:ticket_id>')
def mostrar_ticket(ticket_id):
    ticket = Tickets.query.get_or_404(ticket_id)

    # Crear un gráfico de línea utilizando Plotly Express
    fig = px.line(x=ticket. .fecha, y=activo.precio, labels={'x': 'Fecha', 'y': 'Precio'},
                  title=f'Gráfico de Línea para {activo.nombre}')

@app.route('/actualizar_datos')
def actualizar_datos():
    # Obtener la lista de todos los tickets
    tickets = Tickets.query.filter_by(habilitado=True).all()
    mensaje = '<pre>'

    # Iterar sobre cada ticket
    for ticket in tickets:
        mensaje += f"Procesando el ticket {ticket.ticket} de {ticket.mercado}:\n"
        mensaje += f"Fecha de ultima actualizacion: {ticket.ultima_actualizacion}\n"

        # Obtenemos los datos de Yahoo Finance desde la última fecha hasta hoy
        df = obtener_datos_yahoo(ticket.ticket, ticket.ultima_actualizacion)
        mensaje += 'Cantidad de registros: ' + str(len(df)) + '\n'

        if not df.empty:
            # Actualizar la tabla correspondiente
            actualizar_tabla(ticket.ticket_id, df, ticket.mercado)

            # Actualizar la fecha de ultima_actualizacion en Tickets
            ticket.ultima_actualizacion = df.index[-1].strftime('%Y-%m-%d')
            db.session.commit()
            mensaje += f"Fecha de ultima actualización actualizada: {ticket.ultima_actualizacion}\n"

    return mensaje + '</pre>'


def obtener_datos_yahoo(ticket, ultima_actualizacion):

    # Convertir la cadena a un objeto datetime
    start_date = datetime.strptime(ultima_actualizacion, '%Y-%m-%d')

    # Incrementar en un día
    start_date = start_date + timedelta(days=1)

    # Convertir la nueva fecha a formato 'yyyy-mm-dd' para usar con yfinance
    start_date_str = start_date.strftime('%Y-%m-%d')

    # Obtener los datos de Yahoo Finance
    data = yf.download(ticket, start=start_date_str, end=datetime.now(), interval='1d')
    return data


def actualizar_tabla(ticket_id, df, mercado):
    # Determinar la tabla según el mercado
    if mercado == 'forex':
        tabla = ForexDaily
    elif mercado == 'indices':
        tabla = IndicesDaily
    else:
        tabla = ComoditiesDaily

    # Insertar nuevos registros
    for index, row in df.iterrows():
        # Convertir la fecha a texto en formato 'yyyy-mm-dd'
        fecha_str = row.name.strftime('%Y-%m-%d')

        nuevo_registro = tabla(ticket_id=ticket_id, fecha=fecha_str, apertura=row['Open'], maximo=row['High'], minimo=row['Low'], cierre=row['Close'])
        db.session.add(nuevo_registro)

    # Realizar una inserción por lotes (bulk insert)
    db.session.commit()



