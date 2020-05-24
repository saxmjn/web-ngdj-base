from django.core.mail import send_mail

def send_email():
    send_mail(
    'Subject here',
    'Here is the message.',
    'gomama.india@gmail.com',
    ['cedaus97@gmail.com'],
    fail_silently=False,
    )