from . import views
from django.urls import path
from django.contrib.auth.decorators import login_required

login_path = "/account/user/login/"

# Handles all urls and associated views from views.py
# All urls have names, which can be used in place of urls with the Django Template Language

app_name = 'website'
urlpatterns = [
    # Home page
    path('', views.IndexView.as_view(), name='index'),

    # Admin panel
    path('panel/', login_required(views.AdminPanelView.as_view(), login_url=login_path), name='admin_panel'),
    path('panel/reports/<int:pk>/', login_required(views.AdminPanelReportsView.as_view(), login_url=login_path), name='admin_panel_reports'),
    path('panel/reports/approval/<int:report>/', login_required(views.toggle_report_approval, login_url=login_path), name='toggle_report'),

    # Game view
    path('game/<int:pk>/', views.GameView.as_view(), name='game'),

    # Post view
    path('post/<int:pk>/', views.PostView.as_view(), name='post'),

    # Object list views
    path('games/', views.GamesListView.as_view(), name='games_list'),
    path('posts/', views.PostsListView.as_view(), name='posts_list'),
    path('entities/<str:entity>/', views.EntityView.as_view(), name='entities'),

    # Developer and publisher views
    path('developer/<int:pk>', views.DeveloperView.as_view(), name='developer'),
    path('publisher/<int:pk>', views.PublisherView.as_view(), name='publisher'),

    # Object deletion
    path('delete/<str:object>/<int:obj_id>/', views.delete, name='delete'),

    # Account disabling and restoring
    path('disable/<int:user_id>/', views.disable_user, name='disable'),
    path('restore/<int:user_id>', views.restore_user, name='restore'),

    # New object creation views
    path('create/<str:object>/', login_required(views.CreateView.as_view(), login_url=login_path), name='create'),
    path('create/<str:object>/<int:game_id>/', login_required(views.CreateView.as_view(), login_url=login_path), name='create'),
    path('create/<str:object>/<str:entity>/', login_required(views.CreateView.as_view(), login_url=login_path), name='create'),
    path('addtempimage/', views.add_temp_image, name='addtempimage'),

    # Executed when leaving post creation without publishing post
    path('abortpostcreation/', views.delete_unused_images, name='abort_post_creation'),

    # User login, profile and settings views
    path('account/user/<str:action>/', views.AccountView.as_view(), name='account'),
    path('account/settings/', login_required(views.UserSettings.as_view(), login_url=login_path), name='account_settings'),
    path('account/profile/<int:pk>/', views.UserProfile.as_view(), name='profile'),

    # Logout function
    path('account/logout/', views.log_user_out, name='logout'),

    # Search view
    path('search/', views.SearchView.as_view(), name='search'),

    # Like and dislike functions
    path('like/game/<int:game>/', login_required(views.like_game, login_url=login_path), name='like_game'),
    path('like/post/<int:post>/', login_required(views.like_post, login_url=login_path), name='like_post'),

    path('dislike/game/<int:game>/', login_required(views.dislike_game, login_url=login_path), name='dislike_game'),
    path('dislike/post/<int:post>/', login_required(views.dislike_post, login_url=login_path), name='dislike_post'),

    # Image links
    path('image/<int:pk>', views.get_image, name='get_image'),
]
