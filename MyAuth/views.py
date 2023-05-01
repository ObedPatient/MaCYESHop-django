from django.shortcuts import render, redirect
from django.contrib import messages, auth
from MyAuth.models import Account
from django.views.generic import View
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout
# getiing token from utils.py
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from .utils import TokenGenerator, generate_token

# to activate User Account 
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.urls import NoReverseMatch, reverse
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError

 # emails

from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.mail import BadHeaderError, send_mail
from django.core import mail
from django.conf import settings
from django.core.mail import EmailMessage
import threading


# Create your views here.
class EmailThread(threading.Thread):
    def __init__(self,email_message):
        self.email_message=email_message
        threading.Thread.__init__(self)
    def run(self):
        self.email_message.send()


def signup(request):
    if request.method == "POST":
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email=request.POST['email']
        phone_number = request.POST['phone_number']
        password=request.POST['pass1']
        confirm_password=request.POST['pass2']
        username = email.split('@')[0]

        if password!=confirm_password:
            messages.warning(request, "Password Is Not Matching")
            return render(request, 'auth/signup.html')
        
        try:
            if Account.objects.filter(email=email).exists():
                messages.warning(request, "Email is Taken")
                return render(request,'auth/signup.html')

        except Exception as identifier:
            pass


        user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, phone_number=phone_number,username=username, password=password)
        user.is_active=False
        user.save()
        current_site = get_current_site(request)
        email_subject = "Activate Your Account"
        message = render_to_string('auth/activate.html',{
            'user': user,
            'domain': '127.0.0.1:8000',
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': generate_token.make_token(user)
        })
        email_message = EmailMessage(email_subject,message,settings.EMAIL_HOST_USER,[email],)
        EmailThread(email_message).start()
        messages.success(request,"Activate Your Account By clicking link in your Email")
        return redirect('login')
    return render(request, 'auth/signup.html' )

class ActivateAccountView(View):
    def get(self,request,uidb64,token):
        try:
            uid= force_str(urlsafe_base64_decode(uidb64))
            user=Account.objects.get(pk=uid)
        except Exception as identifier:
            user=None

        if user is not None and generate_token.check_token(user,token):
            user.is_active=True
            user.save()
            messages.info(request,"Account Activated Successfully")
            return redirect('login')

        return render(request,'auth/activation_fail.html')


def login(request):
    if request.method =='POST':
        email=request.POST['email']
        password=request.POST['pass1']
        user=auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request,user)
            #messages.success(request, "Logged In Succesfully") 
            return redirect('index')
        
        else:
            messages.error(request, "Invalid Login Credentials")
            return redirect('login')
    return render(request, 'auth/login.html')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request,'log Out Success!')
    return redirect('login')


class RequestResetEmailView(View):
    def get(self,request):
        return render(request, 'auth/password_reset.html')
    
    def post(self,request):
        email=request.POST['email']
        user=Account.objects.filter(email=email)

        if user.exists():
            current_site=get_current_site(request)
            email_subject='[Reset Your Password]'
            message=render_to_string('auth/reset_user_password.html',{
                'domain':'127.0.0.1:8000',
                'uid':urlsafe_base64_encode(force_bytes(user[0].pk)),
                'token':PasswordResetTokenGenerator().make_token(user[0])
            })

            email_message=EmailMessage(email_subject,message,settings.EMAIL_HOST_USER,[email])
            EmailThread(email_message).start()


            messages.info(request,"WE HAVE SENT YOU AN EMAIL WITH INSTRUCTIONS ON HOW TO REST A PASSWORD ")
            return render(request,'auth/password_reset.html')
        


class SetNewPasswordView(View): 
    def get(self,request,uidb64,token):
        context = {
            'uidb64':uidb64,
            'token':token
        }
        try:
            user_id=force_str(urlsafe_base64_decode(uidb64))
            user=Account.objects.get(pk=user_id)

            if not PasswordResetTokenGenerator().check_token(user,token):
                messages.warning(request,"Password Reset Link is Invalid")
                return render(request,'auth/password_reset.html')

        except DjangoUnicodeDecodeError as identifier:
            pass

        return  render(request,'auth/set-new-password.html',context)
    
    def post(self,request,uidb64,token):
        context = {
            'uidb64':uidb64,
            'token':token
        }
        password = request.POST['pass1']
        confirm_password = request.POST['pass2']
        if password!=confirm_password:
            messages.warning(request, "Password Is Not Matching")
            return render(request, 'auth/set-new-password.html',context)

        try:
            user_id=force_str(urlsafe_base64_decode(uidb64))
            user=Account.objects.get(pk=user_id)
            user.set_password(password)
            user.save()
            messages.success(request,'Password Reset Success Please Login with New Password')
            return redirect('login')
        
        except DjangoUnicodeDecodeError as identifier:
            messages.error(request,'Somthing Went Wrong')
            return render(request, 'auth/set-new-password.html',context)
        return render(request, 'auth/set-new-password.html',context)