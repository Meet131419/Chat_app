from django.urls import path
from user import views

urlpatterns = [
   path('',views.home,name='home'),
   path("login/",views.login,name='login'),
   path("register/",views.register,name='register'),
   path('logout_user/', views.logout_user, name='logout_user'),
   path('forgot_password/', views.forgot_password, name='forgot_password'),
   path('verify_otp/', views.verify_otp, name='verify_otp'),
   path('reset_password/', views.reset_password, name='reset_password'),
   path('chat_view/', views.chat_view, name='chat_view'),
   path('chat_view/<str:group_name>/', views.chat_view, name='chat_view'),  # URL for group chat
   path('create_group/', views.create_group, name='create_group'),
    path("upload/", views.upload_file, name="upload_file"),
   
   
   
   
]
