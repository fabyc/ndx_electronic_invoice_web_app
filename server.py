#corregir que cuando se busque las facturas se comprube tb el numero de cedula si no se estan obteniendo todas las facturas
# -*- coding: utf-8 -*-
import psycopg2
import psycopg2.extras
import os
from flask import Flask, render_template, request, flash, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask.ext.login import (LoginManager, login_user, logout_user, current_user, \
                            login_required, logout_user, UserMixin, \
                            confirm_login, fresh_login_required)
from __init__ import app, db
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email.mime.application import MIMEApplication
from email import encoders
from email.Utils import COMMASPACE, formatdate
from email import Encoders
import smtplib, os
import datetime
import base64

database = 'database_name'
user = 'database_user'
password = 'database_user_password'
host = 'database_host'

conn = psycopg2.connect(database=database,user= user, password=password, host=host)

cur = conn.cursor()
@app.route('/')
def mainIndex():
    return render_template('index.html')
    
@app.route("/secret")
@fresh_login_required
def secret():
    return render_template("secret.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    cont = 0
    if request.method == "POST" and "user" and 'password' in request.form:
        cur.execute("SELECT * FROM information_schema.sequences")
        sequences = cur.fetchall()
        s_true_u = 0
        s_true_f = 0
        for s in sequences:
            print "s2", s[2]
            if s[2] == 'user_id_seq':
                s_true_u = 1
            elif s[2] == 'factura_id_seq':
                s_true_f = 1
            else:
                pass
        if s_true_u == 0:      
            cur.execute("CREATE SEQUENCE user_id_seq;")
        if s_true_f == 0:
            cur.execute("CREATE SEQUENCE factura_id_seq;") 
        
        cur.execute("CREATE TABLE IF NOT EXISTS usuario_web (id integer DEFAULT  NEXTVAL('user_id_seq') NOT  NULL, username varchar, password varchar, cedula varchar, correo varchar, nombre varchar, token varchar, fecha varchar, primary key (id))")
        cur.execute("CREATE TABLE IF NOT EXISTS factura_web (id integer DEFAULT  NEXTVAL('factura_id_seq') NOT  NULL, cedula varchar, ruc varchar, tipo varchar, fecha varchar, empresa varchar, numero_comprobante varchar, numero_autorizacion varchar, total varchar, path_xml varchar, path_pdf varchar, primary key (numero_autorizacion))")
        conn.commit()
    
        session['user'] = request.form['user']
        user = request.form["user"]
        password = request.form["password"]
        
        cur.execute("SELECT cedula FROM usuario_web WHERE username = %s AND password =%s", (user,password))
        result = cur.fetchone()
        cur.execute("SELECT empresa FROM factura_web")
        empresas = cur.fetchall()
        empresa = []
        cont = 0
        for e in empresas:
            if e in empresa:
                pass
            else:
                empresa.append(e) 
        if result:
            remember = request.form.get("remember", "no") == "yes"
            cur.execute("SELECT * FROM factura_web WHERE cedula=%s",(result))
            invoices = cur.fetchall()
            cur.execute("SELECT nombre FROM usuario_web WHERE cedula=%s",(result))
            name = cur.fetchall()
            return render_template('comprobantes.html', invoices=invoices, name=name, empresa=empresa)
        else:
            flash(u"Datos ingresados son incorrectos.")
            return render_template("index.html", cont = cont)
    else:
        return render_template("index.html", cont = cont)
        
@app.route('/search', methods=["GET", "POST"])
def search():
    auth = request.form["auth"]
    tipo = request.form["tipo_cbt"]
    id_empresa = request.form["id_empresa"]
    forma = request.form["forma"]
    cur.execute("SELECT empresa FROM factura_web")
    empresas = cur.fetchall()
    empresa = []
    cont = 0
    for e in empresas:
        if e in empresa:
            pass
        else:
            empresa.append(e) 
    invoice = []
    if tipo or id_empresa or auth or forma: 
        cur.execute("SELECT cedula FROM usuario_web WHERE username = %s", [session['user']])
        ced = cur.fetchone()
        cur.execute("SELECT nombre FROM usuario_web WHERE username = %s", [session['user']])
        name = cur.fetchone()
        if tipo:
            if tipo == 'retencion':
                tipo_c = 'in_withholding'
                cur.execute("SELECT * FROM factura_web WHERE tipo=%s AND cedula=%s",[tipo_c, ced])
                invoice_r = cur.fetchall()
                cur.execute("SELECT * FROM factura_web WHERE tipo=%s AND ruc=%s",[tipo_c, ced])
                invoice_e = cur.fetchall()
                if invoice_r:
                    invoice = invoice_r
                if invoice_e:
                    invoice = invoice_e
                return render_template('busqueda.html', invoices=invoice,  empresa=empresa, name=name)
            elif tipo == 'factura':
                tipo_c = 'out_invoice'
                cur.execute("SELECT * FROM factura_web WHERE tipo=%s AND cedula=%s",[tipo_c, ced])
                invoice_r = cur.fetchall()
                
                cur.execute("SELECT * FROM factura_web WHERE tipo=%s AND ruc=%s",[tipo_c, ced])
                invoice_e = cur.fetchall()
                if invoice_r:
                    invoice = invoice_r
                if invoice_e:
                    invoice = invoice_e
                return render_template('busqueda.html', invoices=invoice, empresa=empresa, name=name)
            elif tipo == 'guia':
                tipo_c = 'out_shipment'
                cur.execute("SELECT * FROM factura_web WHERE tipo=%s AND cedula=%s",[tipo_c, ced])
                invoice_r = cur.fetchall()
                cur.execute("SELECT * FROM factura_web WHERE tipo=%s AND ruc=%s",[tipo_c, ced])
                invoice_e = cur.fetchall()
                if invoice_r:
                    invoice = invoice_r
                if invoice_e:
                    invoice = invoice_e
                return render_template('busqueda.html', invoices=invoice, empresa=empresa, name=name)
            elif tipo == 'credito':
                tipo_c = 'out_credit_note'
                cur.execute("SELECT * FROM factura_web WHERE tipo=%s AND cedula=%s",[tipo_c, ced])
                invoice_r = cur.fetchall()
                cur.execute("SELECT * FROM factura_web WHERE tipo=%s AND ruc=%s",[tipo_c, ced])
                invoice_e = cur.fetchall()
                if invoice_r:
                    invoice = invoice_r
                if invoice_e:
                    invoice = invoice_e
                return render_template('busqueda.html', invoices=invoice, empresa=empresa, name=name)
            elif tipo == 'debito':
                tipo_c = 'out_debit_note'
                cur.execute("SELECT * FROM factura_web WHERE tipo=%s AND cedula=%s",[tipo_c, ced])
                invoice_r = cur.fetchall()
                cur.execute("SELECT * FROM factura_web WHERE tipo=%s AND ruc=%s",[tipo_c, ced])
                invoice_e = cur.fetchall()
                if invoice_r:
                    invoice = invoice_r
                if invoice_e:
                    invoice = invoice_e
                return render_template('busqueda.html', invoices=invoice, empresa=empresa, name=name)
        if auth:
            cur.execute("SELECT * FROM factura_web WHERE numero_autorizacion=%s",[auth])
            invoice = cur.fetchall()
            return render_template('busqueda.html', invoices=invoice, empresa=empresa, name=name)
            
        if id_empresa:
            cur.execute("SELECT * FROM factura_web WHERE empresa=%s AND cedula=%s",[id_empresa, ced])
            invoice = cur.fetchall()
            return render_template('busqueda.html', invoices=invoice, empresa=empresa, name=name)
            
        if forma == 'emitidos':
            cur.execute("SELECT * FROM factura_web WHERE ruc=%s", [ced])
            invoice = cur.fetchall()
            return render_template('busqueda.html', invoices=invoice, empresa=empresa, name=name)
        if forma == 'recibidos':
            cur.execute("SELECT * FROM factura_web WHERE cedula=%s", [ced])
            invoice = cur.fetchall()
            return render_template('busqueda.html', invoices=invoice, empresa=empresa, name=name)
    else:
        return render_template('comprobantes.html', invoices=invoice, empresa=empresa, name=name)



@app.route('/search_admin', methods=["GET", "POST"])
def search_admin():
    auth = request.form["auth"]
    tipo = request.form["tipo_cbt"]
    invoice = []
    if tipo or auth: 
        if tipo:
            if tipo == 'retencion':
                tipo_c = 'in_withholding'
                cur.execute("SELECT * FROM factura_web WHERE tipo=%s AND cedula=%s",[tipo_c, ced])
                invoice = cur.fetchall()
                return render_template('busqueda_admin.html', invoices=invoice)
            elif tipo == 'factura':
                tipo_c = 'out_invoice'
                cur.execute("SELECT * FROM factura_web WHERE tipo=%s AND cedula=%s",[tipo_c, ced])
                invoice = cur.fetchall()
                return render_template('busqueda_admin.html', invoices=invoice)
            elif tipo == 'guia':
                tipo_c = 'out_shipment'
                cur.execute("SELECT * FROM factura_web WHERE tipo=%s AND cedula=%s",[tipo_c, ced])
                invoice = cur.fetchall()
                return render_template('busqueda_admin.html', invoices=invoice)
            elif tipo == 'credito':
                tipo_c = 'out_credit note'
                cur.execute("SELECT * FROM factura_web WHERE tipo=%s AND cedula=%s",[tipo_c, ced])
                invoice = cur.fetchall()
                return render_template('busqueda_admin.html', invoices=invoice)
            elif tipo == 'debito':
                tipo_c = 'out_debit note'
                cur.execute("SELECT * FROM factura_web WHERE tipo=%s",[tipo_c])
                invoice = cur.fetchall()
                return render_template('busqueda_admin.html', invoices=invoice)
            
        if auth:
            cur.execute("SELECT * FROM factura_web WHERE numero_autorizacion=%s",[auth])
            invoice = cur.fetchall()
            return render_template('busqueda_admin.html', invoices=invoice)
    else:
        return render_template('comprobantes_admin.html', invoices=invoice)

   
@app.route('/redirigir')
def redirigir():
    return render_template('restablecer.html')
    
@app.route("/enviar", methods=["GET", "POST"])
def enviar():
    name = request.form["name"]
    email = request.form["email"]
    comments = request.form["comments"]
    fromaddr= "nodux.ec@gmail.com"
    toaddr = "etqm25@gmail.com"
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = (toaddr)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = "Contacto desde el Sitio Web de Nodux Comprobantes Electronicos"
    html = """\
                    <html>
                     <head>
                      <title>INFORMACION DE CONTACTO
                      </title> 
                      </head> 
                      <body> 
                        <table width="700" bgcolor=#ec3539 align=center> 
                        <tr> 
                       	<td> 
                       	Nombre: {name}
                       	<p>
                       	Email: {email}
                       	<p>
                       	Comentario: {comments}
                       	<p>
                       	</td> 
                    </tr> 
                    </table> 
                    </body> 
                    
                    """.format(name=name, email=email, comments=comments)
                    
    msg.attach(MIMEText(html, 'html'))
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(fromaddr, "arlrfc&&&78")
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()
    flash(u"Mensaje envíado exitósamente.")
    return render_template("index.html")     
    
            
@app.route('/restablecer',methods=["GET", "POST"])
def restablecer():
    correo = request.form["email"]
    if correo:
        cur.execute("SELECT correo FROM usuario_web WHERE correo=%s",[correo])
        mail = cur.fetchone()
        cur.execute("SELECT username, password, cedula FROM usuario_web WHERE correo=%s",[correo])
        usuario = cur.fetchone()
        ahora = datetime.datetime.now()
        month = str(ahora.month)
        year = str(ahora.year)
        day = str(ahora.day)
        fecha = day+'/'+month+'/'+year
        token = base64.b64encode(usuario[0]+'_'+usuario[1]+'_'+day+'/'+month+'/'+year)
        cur.execute("UPDATE usuario_web SET token= %s, fecha=%s WHERE cedula=%s",[token, fecha, usuario[2]])
        conn.commit()
        if mail:
            fromaddr= "nodux.ec@gmail.com"
            toaddr= mail[0]
            msg = MIMEMultipart()
            msg['From'] = fromaddr
            msg['To'] = (toaddr)
            msg['Date'] = formatdate(localtime=True)
            msg['Subject'] = "ENLACE PARA RESTABLECER SU CONTRASEÑA"
            link="http://0.0.0.0:8080/redirigir?"+token
            html = """\
                    <html>
                     <head>
                      <title>RESTABLEZCA SU CONTRASEÑA
                      </title> 
                      </head> 
                      <body> 
                        <table width="700" bgcolor=#ec3539 align=center> 
                        <tr> 
                       	<td> 
                       	<h2>Hemos recibido una petición para restablecer la contraseña de su cuenta.</h2>
                       	<h3 style="color:000000">Si realizo la petición haga clic en el siguiente enlace, caso contrario puede ignorar este correo.</h3> 
                       	<br> 
                       	<h3><center><a href= {link}> Restablezca su contraseña aqui </a> </center></h3> 
                       	<br> 
                       	</td> 
                    </tr> 
                    </table> 
                    </body> 
                    
                    """.format(link=link)
                    
            msg.attach(MIMEText(html, 'html'))
            server = smtplib.SMTP('smtp.gmail.com:587')
            server.starttls()
            server.login(fromaddr, "arlrfc&&&78")
            text = msg.as_string()
            server.sendmail(fromaddr, toaddr, text)
            server.quit()
            flash(u"Revise su correo para restablecer su contraseña.")
            return render_template("index.html")
                
        else:
            flash(u"El correo ingresado no coincide, inténtelo de nuevo.")
            return render_template("index.html")     
            
@app.route('/restableciendo', methods=["GET", "POST"])
def restableciendo():
    pass1 = request.form["password"]
    pass2 = request.form["password_c"]
    s= request.referrer
    t = s.split("?") 
    token = t[1]
    if pass1 == pass2: 
        cur.execute("SELECT cedula FROM usuario_web WHERE token=%s",[token])
        cedula = cur.fetchone()
        nuevo = ''
        if cedula:
            cur.execute("UPDATE usuario_web SET password = %s, token = %s WHERE cedula=%s", [pass1, nuevo, cedula])
            conn.commit()
            flash(u"Contraseña cambiada exitósamente.")
            return render_template('index.html')
        else:
            flash(u"El token asignado no coincide, diríjase a OLVIDÓ SU CONTRASEÑA \n para continuar el proceso.")
            return render_template('index.html')
    else:
        flash(u"Contraseñas no coinciden.")
        return render_template('restablecer.html')
        
@app.route('/logout', methods=["GET", "POST"])
def logout():
    # remove the username from the session if it's there
    session.pop('user.id', None)
    return redirect(url_for('mainIndex'))
        
if __name__ == '__main__':
    app.debug=True
    app.run(host='0.0.0.0', port=8080)
