from flask import render_template
from flask_mail import Message
from application import application_instance, mail


def send_mail(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_mail(
        application_instance.config['APPLICATION_NAME'] + ' Reset Your Password Confirmation',
        sender=application_instance.config['MAIL_ADMINS'],
        recipients=[user.email],
        text_body=render_template(
            'email/reset_password.txt',
            user=user,
            token=token,
            app_name=application_instance.config['APPLICATION_NAME']),
        html_body=render_template(
            'email/reset_password.html',
            user=user,
            token=token,
            app_name=application_instance.config['APPLICATION_NAME'])
    )
