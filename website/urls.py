from . import views
from django.urls import path
from django.contrib.auth.decorators import login_required

login_path = "/account/user/login/"

app_name = 'website'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),

    path('game/<int:pk>/', views.GameView.as_view(), name='game'),

    path('post/<int:pk>/', views.PostView.as_view(), name='post'),

    path('entity/developer/<int:pk>/', views.DeveloperView.as_view(), name='developer'),
    path('entity/publisher/<int:pk>/', views.PublisherView.as_view(), name='publisher'),

    path('delete/<str:object>/<int:obj_id>/', views.delete, name='delete'),

    path('create/<str:object>/', login_required(views.CreateView.as_view(), login_url=login_path), name='create'),
    path('create/<str:object>/<int:game_id>/', login_required(views.CreateView.as_view(), login_url=login_path), name='create'),
    path('create/<str:object>/<str:entity>/', login_required(views.CreateView.as_view(), login_url=login_path), name='create'),

    path('account/user/<str:action>/', views.AccountView.as_view(), name='account'),
    path('account/settings/', login_required(views.UserSettings.as_view(), login_url=login_path), name='account_settings'),
    path('account/profile/<int:pk>/', views.UserProfile.as_view(), name='profile'),

    path('account/logout/', views.log_user_out, name='logout'),

    path('search/', views.SearchView.as_view(), name='search'),

    path('like/game/<int:game>/', login_required(views.like_game, login_url=login_path), name='like_game'),
    path('like/post/<int:post>/', login_required(views.like_post, login_url=login_path), name='like_post'),

    path('dislike/game/<int:game>/', login_required(views.dislike_game, login_url=login_path), name='dislike_game'),
    path('dislike/post/<int:post>/', login_required(views.dislike_post, login_url=login_path), name='dislike_post'),

    path('image/<int:pk>', views.get_image, name='get_image'),
]
