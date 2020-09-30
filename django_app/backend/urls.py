from django.urls import path

from . import views

urlpatterns = [
    path('psks/', views.psks, name='psks'),
    path('psks/create/', views.createPsk, name='createPsks'),
    path('wlans/', views.wlans, name='wlans'),
    path('login/', views.login, name='login'),
    path('sites/', views.sites, name='sites')    
]

