from django.urls import path

from . import views

urlpatterns = [
    path('psks/', views.psks, name='psks'),
    path('psks/create/', views.createPsk, name='createPsks'),
    path('psks/delete/', views.deletePsk, name='deletePsks'),
    path('psks/email/', views.emailPsk, name='emailPsk'),
    path('wlans/', views.wlans, name='wlans'),
    path('login/', views.login, name='login'),
    path('sites/', views.sites, name='sites'),    
    path('vlans/', views.vlans, name='vlans'),    
]

