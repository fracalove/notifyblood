from flask import Flask, render_template, redirect, request, flash
import smtplib
import email.message
from twilio.rest import Client
import mysql.connector

#Twilio - SMS/Whatsapp
sid = ""
token = ""
client = Client(sid, token)

#Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'NOTIFYBLOOD'

#conecta os arquivos css e imagens
app.static_url_path = '/static'
app.static_folder = 'static'

#----- VARIÁVEIS E FUNÇÕES GLOBAIS -----
logado = False

#Conexão banco de dados
connectBD = mysql.connector.connect(host='localhost', database='usuarios', user='root', password='')

#info email
msg = email.message.Message()
s = smtplib.SMTP('smtp.gmail.com: 587')
password = 'xlhqeykiahfjwzxn'
msg['From'] = 'notifyblood@gmail.com'

#notificacao pelo tipo sanguineo
def notificacao(tipo_sanguineo, usuarios, local):
    if tipo_sanguineo < "35":
            cont = 0
            for user in usuarios:
                cont += 1
                if str(user[5]) == "B-":

                    #envio de Whatsapp
                    client.messages.create(from_='whatsapp:+14155238886', body=f"NotifyBlood: {str(user[1])}, estamos precisando da sua doação! Por favor, quando for possível se direcionar ao endereço: {local}", to="whatsapp:+55"+str(user[3]))

                    #envio de email
                    corpo_email = f"""
                    <p>Olá, {str(user[1])}!</p>
                    <p>Estamos precisando da sua doação!</p>
                    <p>Por favor, quando for possível se direcionar ao endereço: {local}</p>
                    <br>
                    <p>Qualquer dúvida entre em contato!</p>
                    <p>Telefone: (27) 9 9905-5593</p>
                    <p>Email: notifyblood@gmail.com</p>
                    """

                    msg['Subject'] = f"Precisamos da sua doação, {str(user[1])}!"
                    msg['To'] = str(user[2])
                    msg.add_header('Content-Type', 'text/html')
                    msg.set_payload(corpo_email)

                    s.starttls()
                    s.login(msg['From'], password)
                    s.sendmail(msg['From'], [msg['To']], msg.as_string().encode('utf-8'))
                    
                if cont >= len(usuarios):
                    break
                
#----- HOME -----
@app.route('/')
def home():
    global logado
    logado = False
    return render_template('FrontEnd.html')

#----- CONTATOS -----
@app.route('/contatos', methods=['GET', 'POST'])
def contatos():
    if request.method == 'POST':
        nome_contato = request.form.get('name_contato')
        email_contato = request.form.get('email_contato')
        mensagem_contato = request.form.get('mensagem_contato')
        telefone_contato = request.form.get('telefone_contato')

#envio das informações de contato para email
        corpo_email = f"""
        <p>Nome: {nome_contato}</p>
        <p>Email: {email_contato}</p>
        <p>Telefone: {telefone_contato}</p>
        <p>Mensagem: {mensagem_contato}</p>
        """

        msg['Subject'] = f"Contato/dúvida de {nome_contato}"
        msg['To'] = 'notifyblood@gmail.com'
        msg.add_header('Content-Type', 'text/html')
        msg.set_payload(corpo_email)

        s.starttls()
        s.login(msg['From'], password)
        s.sendmail(msg['From'], [msg['To']], msg.as_string().encode('utf-8'))

#envio de informações para o banco de dados
        if connectBD.is_connected():
            cursor = connectBD.cursor()
            cursor.execute(f"insert into contato values (default, '{nome_contato}', '{email_contato}', '{mensagem_contato}', '{telefone_contato}');")
            
        if connectBD.is_connected():
            cursor.close()
            connectBD.close()
            
        flash('Mensagem enviada com sucesso!')
        return redirect('/')

#----- CADASTRO -----
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    global logado
    if request.method == 'POST':
        email_cadastro = request.form.get('email')
        nome = request.form.get('name')
        idade = request.form.get('idade')
        sangue = request.form.get('sangue')
        telefone = request.form.get('telefone')
        sexo = request.form.get('sexo')

#login de administrador
        if email_cadastro == 'admin@admin' and nome == 'admin' and telefone == '99999999999':
            logado = True
            return render_template('admin.html')

#verifica se email ou telefone ja estao cadastrados
        if connectBD.is_connected():
            cursor = connectBD.cursor()
            cursor.execute('select * from usuario;')
            usuarios = cursor.fetchall()
            cont = 0
            for user in usuarios:
                cont += 1
                if str(user[2]) == email_cadastro:
                    flash("Email ja cadastrado")
                    return redirect('/')
                
                if str(user[3]) == telefone:
                    flash("Telefone ja cadastrado")
                    return redirect('/')

#cadastro do usuario no banco de dados
        if connectBD.is_connected():
            cursor = connectBD.cursor()
            cursor.execute(f"insert into usuario values (default, '{nome}', '{email_cadastro}', '{telefone}', '{idade}', '{sangue}', '{sexo}');")

#envio das informações de contato para email
            corpo_email = f"""
            <p>Olá, {nome}!</p>
            <p>Estamos muito felizes que você resolveu participar do nosso projeto!</p>
            <p>Fique atento às notificações que enviamos, através dela você saberá quando estivermos precisando de doação.</p>
            <br>
            <p>Qualquer dúvida entre em contato!</p>
            <p>Telefone: (27) 9 9905-5593</p>
            <p>Email: notifyblood@gmail.com</p>
            """

            msg['Subject'] = f"Bem-vindo ao NotifyBlood, {nome}!"
            msg['To'] = email_cadastro
            msg.add_header('Content-Type', 'text/html')
            msg.set_payload(corpo_email)

            s.starttls()
            s.login(msg['From'], password)
            s.sendmail(msg['From'], [msg['To']], msg.as_string().encode('utf-8'))

        if connectBD.is_connected():
            cursor.close()
            connectBD.close()
            
        flash(f"Cadastro realizado com sucesso! Seja bem-vindo(a), {nome}")    
        return redirect('/')

#----- ADMIN -----
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    Ap = request.form.get('A+')
    An = request.form.get('A-')
    Bp = request.form.get('B+')
    Bn = request.form.get('B-')
    ABp = request.form.get('AB+')
    ABn = request.form.get('AB-')
    Op = request.form.get('O+')
    On = request.form.get('O-')
    local = request.form.get('local')

#recolhe informações do banco de dados
    if connectBD.is_connected():
        cursor = connectBD.cursor()
        cursor.execute('select * from usuario;')
        usuarios = cursor.fetchall()

#envio de notificação
        #A+
        notificacao(Ap, usuarios, local)

        #A-
        notificacao(An, usuarios, local)

        #B+
        notificacao(Bp, usuarios, local)
    
        #B-
        notificacao(Bn, usuarios, local)

        #AB+
        notificacao(ABp, usuarios, local)

        #AB-
        notificacao(ABn, usuarios, local)

        #O+
        notificacao(Op, usuarios, local)

        #O-
        notificacao(On, usuarios, local)

    flash("ATUALIZADO COM SUCESSO")
    return redirect('/')

#----- HOST DO SITE -----    
if __name__ == '__main__':
    app.run(debug=True)
