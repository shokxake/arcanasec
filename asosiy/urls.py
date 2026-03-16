from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.asosiy_sahifa, name='asosiy_sahifa'),
    path('profil/', views.profil, name='profil'),
    path('profil/ozgartirish/', views.profil_ozgartirish, name='profil_ozgartirish'),
    path('challenges/', views.challenge_list, name='challenge_list'),
    path('challenges/<int:challenge_id>/', views.challenge_detail, name='challenge_detail'),
    path('scoreboard/', views.scoreboard, name='scoreboard'),
    path('yechish/<int:challenge_id>/', views.yechish, name='yechish'),
    path('register/', views.register, name='register'), # Ro'yxatdan o'tish uchun URL
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='asosiy_sahifa'), name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('logout/', auth_views.LogoutView.as_view(next_page='asosiy_sahifa'), name='logout'),
    path('users/', views.users_list, name='users_list'),  # Bu qatorni o'zgartiring
]