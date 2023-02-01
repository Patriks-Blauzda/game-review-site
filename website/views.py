from django.shortcuts import render
from django.views import generic

from .models import Game
from .models import Post

# Create your views here.
class IndexView(generic.ListView):
    template_name = 'website/index.html'
    context_object_name = 'games_list'

    def get_queryset(self):
        return Game.objects.all()


class GameView(generic.ListView):
    model = Game
    template_name = 'website/game.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        return Post.objects.filter(game=self.kwargs['pk'])


class PostView(generic.DetailView):
    model = Post
    template_name = 'website/post.html'


class EntityView(generic.DetailView):
    pass