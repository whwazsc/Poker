"""Poker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from . import view

urlpatterns = [
    path('', view.login),
    path("home/", view.home),
    path("illegal/", view.illegal),
    path("createroom/", view.createroom),
    re_path("^room/([0-9a-f]{32})/$", view.room),
    path("gotoroom/", view.gotoroom),
    re_path("^room/([0-9a-f]{32})/sit/$", view.sit),
    re_path("^room/([0-9a-f]{32})/getsit/$", view.getsit),
    re_path("^room/([0-9a-f]{32})/getstatus/$", view.getstatus),
    re_path("^room/([0-9a-f]{32})/begingame/$", view.begingame),
    re_path("^room/([0-9a-f]{32})/bet/$", view.userbet),
    re_path("^room/([0-9a-f]{32})/call/$", view.call),
    re_path("^room/([0-9a-f]{32})/check/$", view.check),
    re_path("^room/([0-9a-f]{32})/exit/$", view.delete),
    path("returnhome/", view.returnhome),
]
