from django.urls import path
from . import views


urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout,name='logout'),
    path('activate/<uidb64>/<token>', views.ActivateAccountView.as_view(),name='activate'),
    path('password_reset/', views.RequestResetEmailView.as_view(),name='password_reset'),
    path('set-new-password/<uidb64>/<token>', views.SetNewPasswordView.as_view(),name='set-new-password'),
]