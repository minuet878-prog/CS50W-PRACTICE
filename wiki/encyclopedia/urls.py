from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/random", views.randompage, name="random"),
    path("wiki/search", views.search, name="search"),
    path("wiki/create", views.create, name="create"),
    path("wiki/<str:title>", views.entry, name="entry")
]
