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
from django.contrib.auth.hashers import check_password
from django.forms.widgets import DateInput
import base64
from itertools import chain
from django.db.models.functions import Lower

from .models import Game
from .models import Post
from .models import Image
from .models import Developer
from .models import Publisher
from .models import LikesUserMap
from .models import DislikesUserMap
from .models import UserData

from django.urls import reverse_lazy


def sort_postcount(e):
    if e.__class__.__name__ == "Game":
        return len(Post.objects.filter(game=e))
    return -1


def sort_popularity(e):
    match e.__class__.__name__:
        case "Game":
            return len(LikesUserMap.objects.filter(game=e)) - len(DislikesUserMap.objects.filter(game=e))
        case "Post":
            return len(LikesUserMap.objects.filter(post=e)) - len(DislikesUserMap.objects.filter(post=e))
    return -9999999


def get_order(sort):
    if sort != "-id" and sort != "id":
        if sort[0] != '-':
            sort = Lower(sort)
        else:
            sort = Lower(sort[1:]).desc()

    return sort


class IndexView(generic.TemplateView):
    template_name = 'website/index.html'
    reverse_lazy('post')

    def get_context_data(self, **kwargs):
        games_list = list(Game.objects.all())
        games_list.sort(key=sort_popularity, reverse=True)

        sort = self.request.GET.get("sort")
        if sort:
            if sort == "postcount":
                games_list = list(Game.objects.all())
                games_list.sort(key=sort_postcount, reverse=True)
            elif not "popularity":
                order = get_order(sort)
                games_list = Game.objects.order_by(order)
        else:
            sort = "popularity"

        return {
            'games_list': games_list,
            'latest_reviews': Post.objects.order_by("-id")[:5],
            'latest_games': Game.objects.order_by("-id")[:5],
            'sort': sort,
        }


class GameView(generic.ListView):
    model = Game
    template_name = 'website/game.html'
    context_object_name = 'post_list'

    def get_context_data(self, **kwargs):
        post_list = list(Post.objects.filter(game=self.kwargs['pk']))
        post_list.sort(key=sort_popularity, reverse=True)

        sort = self.request.GET.get("sort")
        if sort and sort != "popularity":
                order = get_order(sort)
                post_list = Post.objects.filter(game=self.kwargs['pk']).order_by(order)
        else:
            sort = "popularity"

        return {
            'post_list': post_list,
            'current_game': Game.objects.filter(id=self.kwargs['pk'])[0],
            'sort': sort,
        }


class PostView(generic.DetailView):
    model = Post
    template_name = 'website/post.html'


class DeveloperView(generic.DetailView):
    model = Developer
    template_name = 'website/entity.html'

    def get_context_data(self, **kwargs):
        return {
            'entity': Developer.objects.get(id=self.kwargs['pk']),
            'games': Game.objects.filter(developer=self.kwargs['pk'])
        }


class PublisherView(generic.DetailView):
    model = Publisher
    template_name = 'website/entity.html'

    def get_context_data(self, **kwargs):
        return {
            'entity': Publisher.objects.get(id=self.kwargs['pk']),
            'games': Game.objects.filter(publisher=self.kwargs['pk'])
        }


class PostForm(forms.ModelForm):
    name = "post"
    game_id = -1

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
    encoded_blob = base64.b64encode(image.read()).decode()
    row = Image.objects.create(binary_blob=encoded_blob)

    row.refresh_from_db()

    return row.id


def get_image(request, **kwargs):
    id = kwargs['pk']
    image_data = Image.objects.get(id=id).binary_blob
    image = base64.b64decode(image_data)
    return http.HttpResponse(image, content_type="image/png")



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
                    UserData.objects.create(user=User.objects.get(username=auth))

                    if auth:
                        login(request, auth)

                        messages.success(request, "Account successfully registered and logged in")
                        return http.HttpResponseRedirect("/")
                    else:
                        messages.error(request, "There was a problem registering, please try again")
                        return http.HttpResponseRedirect("/account/user/register/")

                else:
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
                        return http.HttpResponseRedirect("/account/user/login/")


def log_user_out(request):
    logout(request)
    messages.success(request, "User logged out")
    return http.HttpResponseRedirect("/")


class UserProfile(generic.DetailView):
    model = User
    template_name = "website/userprofile.html"

    def get_context_data(self, **kwargs):
        context = {
            'account': User.objects.get(id=self.kwargs['pk']),
            'userdata': UserData.objects.get(user=User.objects.get(id=self.kwargs['pk'])),
            'acc_posts': Post.objects.filter(author=self.kwargs['pk']),
        }
        return context


class UserSettings(generic.FormView):
    model = User
    template_name = "website/usersettings.html"

    def post(self, request, *args, **kwargs):
        form = self.request.POST
        files = self.request.FILES

        userdata = UserData.objects.get(user=request.user)

        new_username = form['new_username']
        if new_username != '':
            if check_password(form['username_password_auth'], request.user.password):
                if not User.objects.filter(username=new_username).exists():
                    user = request.user
                    user.username = new_username
                    user.save()

                    messages.success(request, "Username updated")
                else:
                    messages.error(request, "Username already exists")
            else:
                messages.error(request, "Incorrect password")

        old_password = form['old_password']
        if old_password != '':
            if check_password(old_password, request.user.password):
                if form['new_password1'] == form['new_password2']:
                    if form['new_password1'] != '':
                        if not check_password(form['new_password1'], request.user.password):
                            user = request.user
                            user.set_password(form['new_password1'])
                            user.save()

                            authenticate(request, user=user.username, password=form['new_password1'])
                            login(request, user)

                            messages.success(request, "Password updated")
                        else:
                            messages.error(request, "New password cannot be the same")
                    else:
                        messages.error(request, "New password cannot be blank")
                else:
                    messages.error(request, "New password does not match")
            else:
                messages.error(request, "Incorrect password")

        if files:
            profile_picture = files['picture']

            if profile_picture:
                if userdata.image:
                    encoded_blob = base64.b64encode(profile_picture.read()).decode()
                    userdata.image.binary_blob = encoded_blob

                    userdata.image.save()
                    userdata.save()

                    userdata.image.refresh_from_db()

                else:
                    userdata.image = Image.objects.get(id=add_image_to_db(profile_picture))
                    userdata.save()

                messages.success(request, "Profile picture updated")


        description = form['description']
        if description != userdata.description:
            userdata.description = description
            userdata.save()

            messages.success(request, "Profile description updated")


        return http.HttpResponseRedirect("/account/settings/")

    def get_context_data(self, **kwargs):
        return {
            'userdata': UserData.objects.get(user=self.request.user),
        }



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

    if not sortmethod:
        sortmethod = "title"

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
        case "-type":
            query_list.sort(key=sort_type, reverse=True)
        case "popularity":
            query_list.sort(key=sort_popularity, reverse=True)
        case "postcount":
            query_list.sort(key=sort_postcount, reverse=True)

    return query_list


class SearchView(generic.ListView):
    template_name = "website/search.html"

    def get_queryset(self):
        return None

    def get_context_data(self, **kwargs):
        query = self.request.GET.get("q")

        return {
            'object_list': get_search_results(query, self.request.GET.get("sort")),
            'sort': self.request.GET.get("sort")
        }


# add a way to display likes to debug this
def like_game(request, game):
    if LikesUserMap.objects.filter(user=request.user, game=Game.objects.get(id=game)).exists():
        obj = LikesUserMap.objects.get(user=request.user, game=Game.objects.get(id=game))
        obj.delete()

    else:
        if DislikesUserMap.objects.filter(user=request.user, game=Game.objects.get(id=game)).exists():
            DislikesUserMap.objects.get(user=request.user, game=Game.objects.get(id=game)).delete()

        like = LikesUserMap(user=request.user, game=Game.objects.get(id=game))
        like.save()

    return http.HttpResponseRedirect(request.META['HTTP_REFERER'])


def like_post(request, post):
    if LikesUserMap.objects.filter(user=request.user, post=Post.objects.get(id=post)).exists():
        obj = LikesUserMap.objects.get(user=request.user, post=Post.objects.get(id=post))
        obj.delete()

    else:
        if DislikesUserMap.objects.filter(user=request.user, post=Post.objects.get(id=post)).exists():
            DislikesUserMap.objects.get(user=request.user, post=Post.objects.get(id=post)).delete()

        like = LikesUserMap(user=request.user, post=Post.objects.get(id=post))
        like.save()

    return http.HttpResponseRedirect(request.META['HTTP_REFERER'])


def dislike_game(request, game):
    if DislikesUserMap.objects.filter(user=request.user, game=Game.objects.get(id=game)).exists():
        obj = DislikesUserMap.objects.get(user=request.user, game=Game.objects.get(id=game))
        obj.delete()

    else:
        if LikesUserMap.objects.filter(user=request.user, game=Game.objects.get(id=game)).exists():
            LikesUserMap.objects.get(user=request.user, game=Game.objects.get(id=game)).delete()

        dislike = DislikesUserMap(user=request.user, game=Game.objects.get(id=game))
        dislike.save()

    return http.HttpResponseRedirect(request.META['HTTP_REFERER'])

def dislike_post(request, post):
    if DislikesUserMap.objects.filter(user=request.user, post=Post.objects.get(id=post)).exists():
        obj = DislikesUserMap.objects.get(user=request.user, post=Post.objects.get(id=post))
        obj.delete()

    else:
        if LikesUserMap.objects.filter(user=request.user, post=Post.objects.get(id=post)).exists():
            LikesUserMap.objects.get(user=request.user, post=Post.objects.get(id=post)).delete()

        dislike = DislikesUserMap(user=request.user, post=Post.objects.get(id=post))
        dislike.save()

    return http.HttpResponseRedirect(request.META['HTTP_REFERER'])