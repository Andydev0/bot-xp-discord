import smtplib
from smtplib import SMTPException
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.mime.base import MIMEBase
import dotenv
import os

dotenv.load_dotenv(dotenv.find_dotenv())

SENDER = os.getenv("SENDER")
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
PASS = os.getenv("PASS")
 
def envia_email(destinatarios, titulo='', texto='', caminho=None, arquivos=None):

    sender = SENDER
    session = smtplib.SMTP(HOST, PORT)
    session.starttls()
    session.login(sender, PASS)

    message = MIMEMultipart("alternative")
    message["Subject"] = titulo
    message["From"] = sender
    message["To"] = ','.join(destinatarios)
    texto = MIMEText(texto, "plain")

    message.attach(texto)
    if arquivos is not None:
        for arquivo in arquivos:
            part = MIMEBase('application', "octet-stream")
            part.set_payload(open(caminho + '\\' + arquivo, "rb").read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{arquivo}"')
            message.attach(part)
    
    session.sendmail(sender, destinatarios, message.as_string())

    return 'Email enviado com sucesso'
