from datetime import datetime

import django.views.defaults
from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone
import django.http as http
from django.views import generic
from django import forms
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms.widgets import DateInput
import base64
from itertools import chain
from django.db.models.functions import Lower

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
        order = "title"
        if self.request.GET.get("sort"):
            order = self.request.GET.get("sort")
            if order[0] != '-':
                order = Lower(order)
            else:
                order = Lower(order[1:]).desc()

        result = {
            'games_list': Game.objects.order_by(order)
        }

        return result


class GameView(generic.ListView):
    model = Game
    template_name = 'website/game.html'
    context_object_name = 'post_list'

    def get_context_data(self, **kwargs):
        order = "title"
        if self.request.GET.get("sort"):
            order = self.request.GET.get("sort")
            if order[0] != '-':
                order = Lower(order)
            else:
                order = Lower(order[1:]).desc()

        context = {
            'post_list': Post.objects.filter(game=self.kwargs['pk']).order_by(order),
            'current_game': Game.objects.filter(id=self.kwargs['pk'])[0],
        }

        return context


class PostView(generic.DetailView):
    model = Post
    template_name = 'website/post.html'


class DeveloperView(generic.DetailView):
    model = Developer
    template_name = 'website/entity.html'

    def get_context_data(self, **kwargs):
        return {
            'entity': Developer.objects.filter(id=self.kwargs['pk'])[0],
            'games': Game.objects.filter(developer=self.kwargs['pk'])
        }


class PublisherView(generic.DetailView):
    model = Publisher
    template_name = 'website/entity.html'

    def get_context_data(self, **kwargs):
        return {
            'entity': Publisher.objects.filter(id=self.kwargs['pk'])[0],
            'games': Game.objects.filter(publisher=self.kwargs['pk'])
        }


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

    class Meta:
        model = Game
        fields = ('developer', 'publisher', 'title', 'description', 'releasedate')

        widgets = {'releasedate': DateInput(attrs={'type': 'date'})}


class DeveloperForm(forms.ModelForm):
    name = "entity"

    class Meta:
        model = Developer
        fields = ('title', 'description', 'foundingdate')

        widgets = {'foundingdate': DateInput(attrs={'type': 'date'})}


class PublisherForm(forms.ModelForm):
    name = "entity"

    class Meta:
        model = Publisher
        fields = ('title', 'description', 'foundingdate')

        widgets = {'foundingdate': DateInput(attrs={'type': 'date'})}


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
                post = Post.objects.create(
                    title=form.cleaned_data['title'], content=form.cleaned_data['content'], image_id=image_id,
                    pubdate=timezone.now(), game_id=int(self.kwargs['game_id']), author=request.user,
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
                            title=form.cleaned_data['title'], description=form.cleaned_data['description'],
                            image_id=image_id,
                        )
                case 'publisher':
                    form = PublisherForm(request.POST)

                    if form.is_valid():
                        entity = Publisher(
                            title=form.cleaned_data['title'], description=form.cleaned_data['description'],
                            image_id=image_id,
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


def delete(request, **kwargs):
    match kwargs['object']:
        case "game":
            Game.objects.filter(id=kwargs['obj_id']).delete()
            return http.HttpResponseRedirect("/")

        case "post":
            game_id = Post.objects.filter(id=kwargs['obj_id'])[0].game.id
            Post.objects.filter(id=kwargs['obj_id']).delete()
            return http.HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        case "developer":
            Developer.objects.filter(id=kwargs['obj_id']).delete()
            return http.HttpResponseRedirect("/")

        case "publisher":
            Publisher.objects.filter(id=kwargs['obj_id']).delete()
            return http.HttpResponseRedirect("/")


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'email']


class LoginForm(forms.Form):
    username = forms.CharField(max_length=40)
    password = forms.CharField(max_length=40, widget=forms.PasswordInput)


class AccountView(generic.FormView):
    def get_context_data(self, **kwargs):
        match self.kwargs['action']:
            case 'register':
                self.template_name = "website/register.html"
                self.form_class = RegisterForm

            case 'login':
                self.template_name = "website/login.html"
                self.form_class = LoginForm

        context = super().get_context_data(**kwargs)

        context["form"] = self.form_class

        return context

    def get_queryset(self):
        return http.HttpResponseRedirect("/")

    def post(self, request, **kwargs):
        match self.kwargs['action']:
            case 'register':
                form = RegisterForm(request.POST)

                if form.is_valid():
                    form.save()

                    un = form.cleaned_data['username']
                    pw = form.cleaned_data['password1']

                    auth = authenticate(request, username=un, password=pw)

                    if auth:
                        login(request, auth)

                        messages.success(request, "Account successfully registered and logged in")
                        return http.HttpResponseRedirect("/")
                    else:
                        messages.error(request, "There was a problem registering, please try again")
                        return http.HttpResponseRedirect("/account/register/")

                else:
                    print(form.errors)
                    messages.error(request, form.errors)
                    return render(request, 'website/register.html', {'form': form})

            case 'login':
                form = LoginForm(request.POST)

                if form.is_valid():
                    un = form.cleaned_data['username']
                    pw = form.cleaned_data['password']

                    user = authenticate(request, username=un, password=pw)

                    if user:
                        login(request, user)
                        messages.success(request, "Successfully logged in")
                        next = self.request.GET.get("next")
                        if next:
                            return http.HttpResponseRedirect(next)
                        else:
                            return http.HttpResponseRedirect("/")
                    else:
                        messages.error(request, "Login failed")
                        return http.HttpResponseRedirect("/account/login/")


def log_user_out(request):
    logout(request)
    messages.success(request, "User logged out")
    return http.HttpResponseRedirect("/")


class UserProfile(generic.DetailView):
    model = User
    template_name = "website/userprofile.html"

    def get_context_data(self, **kwargs):
        context = {
            'account': User.objects.filter(id=self.kwargs['pk'])[0],
            'acc_posts': Post.objects.filter(author=self.kwargs['pk']),
        }
        return context


def sort_title(e):
    name = e.__class__.__name__
    if name == "User":
        return e.username.lower()
    else:
        return e.title.lower()


def sort_date(e):
    name = e.__class__.__name__

    if name == "User" and e.date_joined:
        return e.date_joined
    elif name == "Post" and e.pubdate:
        return e.pubdate
    elif name == "Game" and e.releasedate:
        return timezone.make_aware(datetime.combine(e.releasedate, datetime.min.time()))
    elif (name == "Publisher" or name == "Developer") and e.foundingdate:
        return timezone.make_aware(datetime.combine(e.foundingdate, datetime.min.time()))
    else:
        return timezone.make_aware(datetime(1970, 1, 1))


def sort_id(e):
    return e.id


def sort_type(e):
    return e.__class__.__name__


def get_search_results(query, sortmethod):
    post = Post.objects.filter(Q(title__icontains=query) | Q(content__icontains=query))
    game = Game.objects.filter(Q(title__icontains=query) | Q(description__icontains=query))
    developer = Developer.objects.filter(Q(title__icontains=query) | Q(description__icontains=query))
    publisher = Publisher.objects.filter(Q(title__icontains=query) | Q(description__icontains=query))
    user = User.objects.filter(Q(username__icontains=query))

    query_list = list(chain(post, game, developer, publisher, user))

    match sortmethod:
        case "title":
            query_list.sort(key=sort_title)
        case "-title":
            query_list.sort(key=sort_title, reverse=True)
        case "date":
            query_list.sort(key=sort_date)
        case "-date":
            query_list.sort(key=sort_date, reverse=True)
        case "id":
            query_list.sort(key=sort_id)
        case "-id":
            query_list.sort(key=sort_id, reverse=True)
        case "type":
            query_list.sort(key=sort_type)
        case "-type":
            query_list.sort(key=sort_type, reverse=True)

    return query_list


class SearchView(generic.ListView):
    template_name = "website/search.html"

    def get_queryset(self):
        query = self.request.GET.get("q")

        return get_search_results(query, self.request.GET.get("sort"))
