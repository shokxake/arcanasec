from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # --- ASOSIY SAHIFA VA PROFIL ---
    path('', views.asosiy_sahifa, name='asosiy_sahifa'),
    path('profil/', views.profil, name='profil'),
    path('profil/ozgartirish/', views.profil_ozgartirish, name='profil_ozgartirish'),
    path('users/', views.users_list, name='users_list'),

    # --- ODDIY CHALLENGES (PRACTICE MODE) ---
    path('challenges/', views.challenge_list, name='challenge_list'),
    path('challenges/<int:challenge_id>/', views.challenge_detail, name='challenge_detail'),
    path('yechish/<int:challenge_id>/', views.yechish, name='yechish'),
    path('scoreboard/', views.scoreboard, name='scoreboard'),

    # --- CONTEST REJIMI (CONTEST MODE) ---
    path('contests/', views.contest_list, name='contest_list'),
    path('contest/<int:contest_id>/', views.contest_detail, name='contest_detail'),
    path('contest/<int:contest_id>/join/', views.join_contest, name='join_contest'),
    path('contest/<int:contest_id>/challenges/', views.contest_challenges, name='contest_challenges'),

    # YANGI: contest ichidagi challenge detail sahifasi
    path(
        'contest/<int:contest_id>/challenges/<int:challenge_id>/',
        views.contest_challenge_detail,
        name='contest_challenge_detail'
    ),

    path('contest/<int:contest_id>/participants/', views.contest_participants, name='contest_participants'),
    path('contest/<int:contest_id>/scoreboard/', views.contest_scoreboard, name='contest_scoreboard'),

    # --- AUTHENTICATION (LOGIN/LOGOUT/REGISTER) ---
    path('register/', views.register, name='register'),
    path(
        'login/',
        auth_views.LoginView.as_view(template_name='registration/login.html'),
        name='login'
    ),
    path(
        'logout/',
        auth_views.LogoutView.as_view(next_page='asosiy_sahifa'),
        name='logout'
    ),

    # --- PASSWORD RESET ---
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]