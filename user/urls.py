from django.urls import path
from .views import *

urlpatterns = [
    path("login", login_, name="login"),
    path("logout", logout_, name="logout"),
    path("block<int:id>", block, name="block"),
]