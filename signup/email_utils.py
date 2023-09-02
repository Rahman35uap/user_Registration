from django.core.mail import send_mail
from django.conf import settings

def sendCustomEmail(subject,message,receiverList):
    send_mail(subject,message,settings.EMAIL_HOST_USER,receiverList)