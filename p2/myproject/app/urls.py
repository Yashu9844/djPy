

from django.urls import path
from . import views
urlpatterns = [
   
    path('',views.chaihome,name='chaihome'),
   
    path('alliswell/',views.alliswell,name='alliswell'),
]
