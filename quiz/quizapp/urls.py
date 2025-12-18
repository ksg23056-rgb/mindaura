from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("signup/", views.signup, name="signup"),
    path("signin/", views.signin, name="signin"),
    path("logout/", views.signout, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("quiz/", views.quiz, name="quiz"),
    path("history/", views.history, name="history"),
    path("leaderboard/", views.leaderboard, name="leaderboard"),


]
