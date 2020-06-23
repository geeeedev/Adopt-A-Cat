from django.urls import path
from . import views

# NO Leading Slashes!!
# DIRECT GET and POST routes - GET will show route as URL path
urlpatterns = [
    path('', views.index),
    path('register', views.register),
    path('login', views.login),
    path('success', views.success),
    path('logout', views.logout),
    path('cat/new', views.new),
    path('cat/create', views.create),
    path('cat/<id>', views.show),
    path('cat/<id>/toggle', views.toggle),
    path('cat/<id>/edit', views.edit),
    path('cat/<id>/update', views.update),
    path('cat/<id>/delete', views.destroy),
    path('traits', views.displayTraits),

]
