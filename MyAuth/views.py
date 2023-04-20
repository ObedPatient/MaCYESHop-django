from django.shortcuts import render
from django.contrib import messages, auth
from MyAuth.models import Account

# Create your views here.


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


        user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
        user.is_active=False
        user.save()
    return render(request, 'auth/signup.html' )



def login(request):
    return render(request, 'auth/login.html')