# urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('signin/', views.sign_in, name='signin'),
    path('signup/', views.sign_up, name='signup'),  
    path('reset/', views.reset, name='reset'),
    path('loadheartattack/', views.loadheartattack, name='loadheartattack'),
    path('heartattack/', views.heartattack, name='heartattack'),
    path('loadeyedisease/', views.loadeyedisease, name='loadeyedisease'),
    path('eyedisease/', views.eyedisease, name='eyedisease'),
   

]
