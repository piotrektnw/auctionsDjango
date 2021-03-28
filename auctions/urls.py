from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("additem", views.additem, name="additem"),
    path("listing/", views.listing, name="listing"),
    path("listing/<str:item>", views.listing, name="listing"),
    path("addtowatch", views.addtowatch, name="addtowatch"),
    path("addtowatch/<str:itemId>", views.addtowatch, name="addtowatch"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("bid", views.bid, name="bid"),
    path("bid/<str:itemId>", views.bid, name="bid"),
    path("close",  views.close, name="close"),
    path("close/<str:itemId>", views.close, name="close"),
    path("closed", views.closed, name="closed"),
    path("comments", views.comments, name="comments"),
    path("comments/<str:itemId>", views.comments, name="comments"),
    path("categories", views.categories, name="categories"),
    path("categories/<str:itemId>", views.categories, name="categories")
]
