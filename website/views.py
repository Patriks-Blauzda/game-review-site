import django.views.defaults
from django.shortcuts import render
from django.utils import timezone
import django.http as http
from django.views import generic
from django import forms
import base64


from .models import Game
from .models import Post
from .models import Image
from .models import Developer
from .models import Publisher

from django.urls import reverse_lazy


# Create your views here.
class IndexView(generic.TemplateView):
    template_name = 'website/index.html'
    reverse_lazy('post')

    def get_context_data(self, **kwargs):
        result = {
            'games_list': Game.objects.all(),
        }

        return result



class GameView(generic.ListView):
    model = Game
    template_name = 'website/game.html'
    context_object_name = 'post_list'


    def get_context_data(self, **kwargs):
        context = {
            'post_list': Post.objects.filter(game=self.kwargs['pk']),
            'current_game': Game.objects.filter(id=self.kwargs['pk'])[0],
        }
        return context



class PostView(generic.DetailView):
    model = Post
    template_name = 'website/post.html'


class EntityView(generic.DetailView):
    pass



class PostForm(forms.ModelForm):
    name = "post"
    game_id = -1
    title = forms.CharField(label="Title")
    content = forms.CharField(label="Contents", widget=forms.Textarea)

    class Meta:
        model = Post
        fields = ('title', 'content')


class GameForm(forms.ModelForm):
    name = "game"
    title = forms.CharField()
    description = forms.CharField(label="Game Description", widget=forms.Textarea)
    releasedate = forms.DateField(label="Release Date", required=False)

    class Meta:
        model = Game
        fields = ('developer', 'publisher', 'title', 'description', 'releasedate')


class DeveloperForm(forms.ModelForm):
    name = "entity"
    title = forms.CharField(label="Developer Title")
    description = forms.CharField(label="Developer Description", widget=forms.Textarea)

    class Meta:
        model = Developer
        fields = ('title', 'description', 'foundingdate')


class PublisherForm(forms.ModelForm):
    name = "entity"
    title = forms.CharField(label="Publisher Title")
    description = forms.CharField(label="Publisher Description", widget=forms.Textarea)

    class Meta:
        model = Publisher
        fields = ('title', 'description', 'foundingdate')



class CreateView(generic.ListView):
    template_name = 'website/createredirect.html'


    def post(self, request, **kwargs):
        form = None
        image_id = None

        if request.FILES:
            image_id = add_image_to_db(request.FILES["file"])


        if self.kwargs['object'] == "post":
            form = PostForm(request.POST)

            if form.is_valid():
                post = Post(
                    title=form.cleaned_data['title'], content=form.cleaned_data['content'], image_id=image_id,
                    pubdate=timezone.now(), game_id=int(self.kwargs['game_id']),
                )

                post.save()

                return http.HttpResponseRedirect("http://127.0.0.1:8000/post/%s/" % post.id)


        if self.kwargs['object'] == "game":
            form = GameForm(request.POST)

            if form.is_valid():
                game = Game(
                    title=form.cleaned_data['title'], description=form.cleaned_data['description'], image_id=image_id,
                    releasedate=form.cleaned_data['releasedate'], developer=form.cleaned_data['developer'],
                    publisher=form.cleaned_data['publisher'],

                )

                game.save()

                game.refresh_from_db()


        if self.kwargs['object'] == "entity":
            entity = None

            match self.kwargs['entity']:
                case 'developer':
                    form = DeveloperForm(request.POST)

                    if form.is_valid():
                        entity = Developer(
                            title=form.cleaned_data['title'], description=form.cleaned_data['description'], image_id=image_id,
                        )
                case 'publisher':
                    form = PublisherForm(request.POST)

                    if form.is_valid():
                        entity = Publisher(
                            title=form.cleaned_data['title'], description=form.cleaned_data['description'], image_id=image_id,
                        )

            entity.save()

        return http.HttpResponseRedirect("http://127.0.0.1:8000/")


    def get_queryset(self):
        return http.HttpResponseRedirect("http://127.0.0.1:8000/")



    def get_context_data(self, **kwargs):
        if self.kwargs:
            if self.kwargs['object'] == "game":
                self.template_name = 'website/creategame.html'
                self.form_class = GameForm

            elif self.kwargs['object'] == "post":
                self.template_name = 'website/createpost.html'
                self.form_class = PostForm

            if self.kwargs['object'] == "entity":
                self.template_name = 'website/createdevpub.html'

                if self.kwargs['entity'] == "developer":
                    self.form_class = DeveloperForm
                    self.form_class.Meta.model = Developer

                if self.kwargs['entity'] == "publisher":
                    self.form_class = PublisherForm
                    self.form_class.Meta.model = Publisher


            context = super().get_context_data(**kwargs)

            form = self.form_class

            context["form"] = form

            return context



def add_image_to_db(image):
    encoded_blob = "data:image/jpeg;base64," + base64.b64encode(image.read()).decode()
    row = Image.objects.create(binary_blob=encoded_blob)

    row.refresh_from_db()

    return row.id


def Delete(request, **kwargs):
    match kwargs['object']:
        case "game":
            Game.objects.filter(id=kwargs['obj_id']).delete()
            return http.HttpResponseRedirect("/")

        case "post":
            game_id = Post.objects.filter(id=kwargs['obj_id'])[0].game.id
            Post.objects.filter(id=kwargs['obj_id']).delete()
            return http.HttpResponseRedirect("/game/%s" % str(game_id))

        case "developer":
            Developer.objects.filter(id=kwargs['obj_id']).delete()
            return http.HttpResponseRedirect("/")

        case "publisher":
            Publisher.objects.filter(id=kwargs['obj_id']).delete()
            return http.HttpResponseRedirect("/")

