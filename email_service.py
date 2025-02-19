import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_smtp_email(subject, body, to_email, cat):
    settings = cat.mad_hatter.get_plugin().load_settings()

    smtp_server = settings["smtp_server"]
    smtp_port = settings["smtp_port"]
    sender_email = settings["sender_email"]
    sender_password = settings["sender_password"]
    use_tls = settings["smtp_tls"]

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = to_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "html"))

    result_message = ''
    try:
        # Abilita il debug SMTP
        if use_tls:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()  # Attiva TLS
        else:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)  # Se non si usa TLS
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, message.as_string())
        server.quit()
        result_message = "Favola inviata!"
    except Exception as e:
        print(f"Errore durante l'invio dell'email: {e}")
        cat.llm('non inviare email')
        result_message = "Non sono riuscito ad inviare la storia."
    finally:
        return result_message

