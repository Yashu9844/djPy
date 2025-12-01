

from django.urls import path
from . import views
urlpatterns = [
   
    path('',views.chaihome,name='chaihome'),
   
    path('alliswell/',views.alliswell,name='alliswell'),
    path('<int:chai_id>/', views.chai_detail, name='chai_detail'),
]
