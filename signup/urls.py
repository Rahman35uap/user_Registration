from django.contrib import admin
from django.urls import path,include
from . import views as v

urlpatterns = [  
    path('',v.index),
    path('user_register/',v.userRegister, name = "user_register"),
    path('verify_register/<int:id>',v.verifyRegister, name  = "verify_register"),
    path('register_success/',v.registerSuccess, name  = "register_completed")
]