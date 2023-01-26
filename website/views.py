from django.shortcuts import render
from django.views import generic

from .models import Game
from .models import Post

# Create your views here.
class IndexView(generic.ListView):
    template_name = 'games/index.html'
    context_object_name = 'games_list'

    def get_queryset(self):
        return Game.objects.all()


class GameView(generic.ListView):
    model = Game
    template_name = 'games/game.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        return Post.objects.filter(game=self.kwargs['pk'])


class PostView(generic.DetailView):
    model = Post
    template_name = 'games/post.html'


class EntityView(generic.DetailView):
    pass