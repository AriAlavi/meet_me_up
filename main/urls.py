from django.urls import path
from django.contrib.auth import views as auth_views
import main.views as main_views

urlpatterns = [
    path("", main_views.home, name="home"),
    path("login/", auth_views.LoginView.as_view(template_name="main/login.html"), name="login"),
    path('logout/', auth_views.LogoutView.as_view(template_name="main/logout.html"), name="logout"),
    path('register/', main_views.register, name="register"),
    path('accounts/profile/', main_views.profile, name="profile_redirect"),
    path('index/', main_views.index, name = "index"),
    path('event/<str:code_name>/', main_views.event, name = "event"),
    path('free/', main_views.busy, name = "busy"),
    path('freeInterface/', main_views.freeInterface, name="freeInterface"),
    path('craete/', main_views.create, name="create")
]