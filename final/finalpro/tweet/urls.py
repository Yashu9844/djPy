
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("tweets/", views.tweet_list, name="tweet_list"),
    path("tweets/create/", views.create_tweet, name="create_tweet"),
    path("tweets/<int:pk>/edit/", views.tweet_edit, name="tweet_edit"),
    path("tweets/<int:pk>/delete/", views.tweet_delete, name="tweet_delete"),
    path("register/", views.register, name="register"),
    # API-powered pages
    path("api-feed/", views.tweet_list_api, name="tweet_list_api"),
    path("api-login/", views.login_api, name="login_api"),
    path("api-register/", views.register_api, name="register_api"),
]
