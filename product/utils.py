import random
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from .models import Verify,CustomUser

def generate_otp():
    return str(random.randint(1000, 9999))  # رمز من 6 أرقام



def send_otp(user):
    otp = generate_otp()
    # user = get_object_or_404(CustomUser, email=user_email)
    otp_instance = Verify.objects.create(
    user=user,
    token=otp
)
    
    subject = 'رمز التحقق الخاص بك'
    message = f'رمز التحقق الخاص بك هو: {otp}'
    from_email = 'algarbealaa@gmail.com'
    recipient_list = [user.email]
    try:
        send_mail(subject, message, from_email, recipient_list)
        return True
    except Exception as e:
        print(e)
        return False
    
    
def verify_otp(email, otp_code):
    user = get_object_or_404(CustomUser, email=email)
    stored_otp = Verify.objects.filter(user=user).order_by('-id').first()
    if stored_otp and stored_otp.token == otp_code:
        stored_otp.delete()
        return True
    return False