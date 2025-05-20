from django.urls import path

from . import views

urlpatterns = [
    path('actors/', views.ActorListAPIView.as_view(), name='actor-list'),
    path('actors/<int:pk>/', views.ActorDetailAPIView.as_view(), name='actor-detail'),
    
    path('directors/', views.DirectorListAPIView.as_view(), name='director-list'),
    path('directors/<int:pk>/', views.DirectorDetailAPIView.as_view(), name='director-detail'), 
]