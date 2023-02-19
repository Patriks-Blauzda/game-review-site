from . import views
from django.urls import path

app_name = 'website'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),

    path('game/<int:pk>/', views.GameView.as_view(), name='game'),

    path('post/<int:pk>/', views.PostView.as_view(), name='post'),

    path('developer/<int:pk>/', views.EntityView.as_view(), name='entity'),

    path('create/', views.CreateView.as_view(), name='create'),
    path('create/<str:object>/', views.CreateView.as_view(), name='create'),
    path('create/<str:object>/<int:game_id>/', views.CreateView.as_view(), name='create'),
    path('create/<str:object>/<str:entity>/', views.CreateView.as_view(), name='create'),

    # 'delete/'
]
