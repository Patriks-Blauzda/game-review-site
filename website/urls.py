from . import views
from django.urls import path

app_name = 'website'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),

    path('game/<int:pk>', views.GameView.as_view(), name='game'),

    path('post/<int:pk>', views.PostView.as_view(), name='post'),

    path('developer/<int:pk>', views.EntityView.as_view(), name='entity')
]