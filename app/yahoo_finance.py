import yfinance as yf
from datetime import datetime
from models import ForexDaily, IndicesDaily, ComoditiesDaily, Tickets

def descargar_datos_yfinance(symbol, start_date, end_date):
    data = yf.download(symbol, start=start_date, end=end_date)
    return data

def insertar_datos(ticket_id, fecha, apertura, maximo, minimo, cierre, tabla):
    if tabla == 'forex_daily':
        registro = ForexDaily(ticket_id=ticket_id, fecha=fecha, apertura=apertura, maximo=maximo, minimo=minimo, cierre=cierre)
    elif tabla == 'indices_daily':
        registro = IndicesDaily(ticket_id=ticket_id, fecha=fecha, apertura=apertura, maximo=maximo, minimo=minimo, cierre=cierre)
    elif tabla == 'comodities_daily':
        registro = ComoditiesDaily(ticket_id=ticket_id, fecha=fecha, apertura=apertura, maximo=maximo, minimo=minimo, cierre=cierre)


    db.session.add(registro)
    db.session.commit()
