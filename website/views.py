# File containing all database functionality and webpage displays

from datetime import datetime

import django.views.defaults
from django.db.models import Q
from django.db.models import Count
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
from django.utils.html import format_html
from django.urls import reverse

from .models import Game
from .models import Post
from .models import Image
from .models import Developer
from .models import Publisher
from .models import LikesUserMap
from .models import DislikesUserMap
from .models import UserData
from .models import Comment
from .models import Report

from django.urls import reverse_lazy


# Sorts users by amount of times they have been reported
def sort_reportcount(e):
    reports = Report.objects.filter(user=e)

    count = 0
    for report in reports:
        count += report.count

    return count


# Admin panel view sends list of all users, sorted by report count
# Optionally searches for specific users if query is not empty (search bar)
class AdminPanelView(generic.ListView):
    template_name = 'website/adminpanel.html'

    def get_queryset(self):
        return None

    def get_context_data(self):
        query = self.request.GET.get("user")
        users = User.objects.all()

        if query:
            users = User.objects.filter(Q(username__icontains=query))

        users = list(users)
        users.sort(key=sort_reportcount, reverse=True)

        return {"users": users}


# Displays the reports a specified user has
# Sends the user and reports associated with the user to the frontend
# Optionally able to search for specific reports
class AdminPanelReportsView(generic.ListView):
    template_name = 'website/adminpanelreports.html'

    def get_queryset(self):
        return None

    def get_context_data(self, **kwargs):
        query = self.request.GET.get("reason")

        user = User.objects.get(id=self.kwargs["pk"])
        reports = Report.objects.filter(user=user).order_by('-approved', '-count')

        if query:
            reports = Report.objects.filter(Q(reason__icontains=query, user=user))

        return {
            "user": user,
            "reports": reports
        }


# Sorts publishers/developers by amount of games associated with them
def sort_gamecount(e):
    match e.__class__.__name__:
        case "Developer":
            return len(Game.objects.filter(developer=e))
        case "Publisher":
            return len(Game.objects.filter(publisher=e))
    return -1


# Sorts games/posts by score (sum of likes and dislikes)
def sort_popularity(e):
    match e.__class__.__name__:
        case "Game":
            return len(LikesUserMap.objects.filter(game=e)) - len(DislikesUserMap.objects.filter(game=e))
        case "Post":
            return len(LikesUserMap.objects.filter(post=e)) - len(DislikesUserMap.objects.filter(post=e))
    return -9999999


# Ensures elemnets are all sorted in lowercase (ignores uppercase when sorting)
# Checks if the string to specify sort method has a '-' as the first character
# '-' in front of the specified sorting method reverses the sorting
def get_order(sort):
    if sort != "-id" and sort != "id":
        if sort[0] != '-':
            sort = Lower(sort)
        else:
            sort = Lower(sort[1:]).desc()

    return sort


# Home page, popular games and posts, as well as the 10 newest games and posts
class IndexView(generic.TemplateView):
    template_name = 'website/index.html'
    reverse_lazy('post')

    def get_context_data(self, **kwargs):
        games_list = list(Game.objects.all()[:10])
        games_list.sort(key=sort_popularity, reverse=True)

        post_list = list(Post.objects.all()[:10])
        post_list.sort(key=sort_popularity, reverse=True)


        return {
            'games_list': games_list,
            'post_list': post_list,
            'latest_reviews': Post.objects.order_by("-id")[:5],
            'latest_games': Game.objects.order_by("-id")[:5],
        }


# Displays all posts associated with current game
# Gets and sends the currently viewed game, is sortable
# Shows comments and allows writing comments
# Enables the writing of comments with CommentForm
class GameView(generic.ListView):
    model = Game
    template_name = 'website/game.html'
    context_object_name = 'post_list'

    def get_context_data(self, **kwargs):
        game = Game.objects.get(id=self.kwargs['pk'])
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
            'current_game': game,
            'sort': sort,
            'comments': Comment.objects.filter(game=game).order_by("-date"),
            'form': CommentForm,
        }

    # Saves comment to database, associated with specified game and user
    # Redirects to the registering page if user is not logged in
    def post(self, request, **kwargs):
        if request.user.is_authenticated:
            content = self.request.POST['content']
            game = Game.objects.get(id=self.kwargs['pk'])
            Comment.objects.create(user=self.request.user, content=content, game=game, date=datetime.now())

        else:
            return http.HttpResponseRedirect('account/user/register/')

        return http.HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# Simple class to handle the form input fields for comments
class CommentForm(forms.ModelForm):
    name = "comment"

    class Meta:
        model = Comment
        fields = ('content',)



# Shows a written post (review) and comments
class PostView(generic.DetailView):
    model = Post
    template_name = 'website/post.html'

    def get_context_data(self, **kwargs):
        post = Post.objects.get(id=self.kwargs['pk'])

        return {
            'post': post,
            'comments': Comment.objects.filter(post=post).order_by("-date"),
            'form': CommentForm,
        }

    # Same form data as line 181
    def post(self, request, **kwargs):
        if request.user.is_authenticated:
            content = self.request.POST['content']
            post = Post.objects.get(id=self.kwargs['pk'])
            Comment.objects.create(user=self.request.user, content=content, post=post, date=datetime.now())

        else:
            return http.HttpResponseRedirect('account/user/register/')

        return http.HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# Displays all games in the database, has sorting options
# Displays newest games and posts on the sidebar
class GamesListView(generic.TemplateView):
    template_name = 'website/gameslist.html'
    reverse_lazy('post')

    def get_context_data(self, **kwargs):
        games_list = list(Game.objects.all())
        games_list.sort(key=sort_popularity, reverse=True)

        sort = self.request.GET.get("sort")

        if sort:
            if sort == "postcount":
                games_list = list(Game.objects.all())
                games_list.sort(key=sort_postcount, reverse=True)
            elif sort != "popularity":
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


# Handles both developers and publishers, has sorting options
# Displays latest developers and publishers added to database on the sidebar
class EntityView(generic.ListView):
    template_name = 'website/entityview.html'
    model = Developer

    def get_context_data(self, **kwargs):
        # If 'developers' is found in the url in the specified location, displays all developers
        if self.kwargs['entity'] == "developers":
            dev_list = list(Developer.objects.all())
            dev_list.sort(key=sort_popularity, reverse=True)

            sort = self.request.GET.get("sort")

            if sort:
                if sort == "gamecount":
                    dev_list = list(Developer.objects.all())
                    dev_list.sort(key=sort_gamecount, reverse=True)
                else:
                    order = get_order(sort)
                    dev_list = Developer.objects.order_by(order)

            return {
                'content_list': dev_list,
                'latest_devs': Developer.objects.order_by("-id")[:5],
                'latest_pubs': Publisher.objects.order_by("-id")[:5],
                'sort': sort,
            }

        # If 'publishers' is found in the url in the specified location, displays all publishers
        elif self.kwargs['entity'] == "publishers":
            pub_list = list(Publisher.objects.all())
            pub_list.sort(key=sort_popularity, reverse=True)

            sort = self.request.GET.get("sort")

            if sort:
                if sort == "gamecount":
                    pub_list = list(Publisher.objects.all())
                    pub_list.sort(key=sort_gamecount, reverse=True)
                elif sort != "popularity":
                    order = get_order(sort)
                    pub_list = Publisher.objects.order_by(order)

            return {
                'content_list': pub_list,
                'latest_devs': Developer.objects.order_by("-id")[:5],
                'latest_pubs': Publisher.objects.order_by("-id")[:5],
                'sort': sort,
            }


# Shows a specified developer and all associated games
class DeveloperView(generic.DetailView):
    model = Developer
    template_name = 'website/developer.html'

    def get_context_data(self, **kwargs):
        return {
            'developer': Developer.objects.get(id=self.kwargs['pk']),
            'games_list': Game.objects.filter(publisher=self.kwargs['pk'])
        }


# Shows a publisher and all associated games
class PublisherView(generic.DetailView):
    model = Publisher
    template_name = 'website/publisher.html'

    def get_context_data(self, **kwargs):
        return {
            'publisher': Publisher.objects.get(id=self.kwargs['pk']),
            'games_list': Game.objects.filter(publisher=Publisher.objects.get(id=self.kwargs['pk']))
        }


# Form containing post creation input fields
class PostForm(forms.ModelForm):
    name = "post"
    game_id = -1

    class Meta:
        model = Post
        fields = ('title', 'content')


# Form containing game creation fields, includes datetime field to specify release date
class GameForm(forms.ModelForm):
    name = "game"

    class Meta:
        model = Game
        fields = ('developer', 'publisher', 'title', 'description', 'releasedate')

        widgets = {'releasedate': DateInput(attrs={'type': 'date'})}


# Form containing developer creation fields, includes datetime field to specify founding date
class DeveloperForm(forms.ModelForm):
    name = "entity"

    class Meta:
        model = Developer
        fields = ('title', 'description', 'foundingdate')

        widgets = {'foundingdate': DateInput(attrs={'type': 'date'})}


# Form containing publisher creation fields, includes datetime field to specify founding date
class PublisherForm(forms.ModelForm):
    name = "entity"

    class Meta:
        model = Publisher
        fields = ('title', 'description', 'foundingdate')

        widgets = {'foundingdate': DateInput(attrs={'type': 'date'})}


# Handles all pages for creating objects (games, posts, publishers, developers) and saving the posted form data
class CreateView(generic.ListView):
    # Saves object to database if form data is valid
    # If an image was uploaded, saves image and keeps the ID returned by the function add_image_to_db()
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

    # Sends the specified form template to the frontend, and displays sidebar data
    def get_context_data(self, **kwargs):
        sidebar_list = {}

        # Sends specified form templates and sidebar information to the frontend dependant on the current url
        if self.kwargs:
            if self.kwargs['object'] == "game":
                self.template_name = 'website/creategame.html'
                self.form_class = GameForm

                sidebar_list = {
                    'latest_games': Game.objects.all().order_by("-id")[:10]
                }

            elif self.kwargs['object'] == "post":
                self.template_name = 'website/createpost.html'
                self.form_class = PostForm

                sidebar_list = {
                    'latest_reviews': Post.objects.filter(game=self.kwargs['game_id']).order_by("-id")[:5],
                    'own_reviews': Post.objects.filter(game=self.kwargs['game_id'], author=self.request.user).order_by("-id")[:5],
                    'game_id': self.kwargs['game_id']
                }

            if self.kwargs['object'] == "entity":
                self.template_name = 'website/createdevpub.html'

                if self.kwargs['entity'] == "developer":
                    self.form_class = DeveloperForm
                    self.form_class.Meta.model = Developer

                if self.kwargs['entity'] == "publisher":
                    self.form_class = PublisherForm
                    self.form_class.Meta.model = Publisher

                sidebar_list = {
                    'latest_devs': Developer.objects.all().order_by("-id")[:5],
                    'latest_pubs': Publisher.objects.all().order_by("-id")[:5]
                }

            # Creates a temporary object of the current function to get specific data and combine it with
            # sidebar data, sending a combined dict to the frontend
            context = super().get_context_data(**kwargs)

            form = self.form_class

            context["form"] = form
            context = context | sidebar_list

            return context


# Encodes an image in base64 and adds it to the database
# Refreshes the database so the image is visible immediately
# Returns the ID of the image on the database
def add_image_to_db(image):
    encoded_blob = base64.b64encode(image.read()).decode()
    row = Image.objects.create(binary_blob=encoded_blob)

    row.refresh_from_db()

    return row.id


# Used in post creation (createpost.html, textformatting.js)
# Calls add_image_to_db() and returns json data for use in JavaScript
def add_temp_image(request):
    if request.FILES:
        image = request.FILES['image']

        image_id = add_image_to_db(image)

        return http.JsonResponse({'status': 'success', 'image_id': image_id}, status=200)

    return http.HttpResponseForbidden()


# Deletes all temporarily added images after user leaves post creation page without publishing
# Receives the array containing IDs of images, iterates through them to delete them
# If not receiving a post request, access is forbidden
def delete_unused_images(request):
    if request.POST['images']:

        data = request.POST['images']
        newdata = []

        for id in data.split(","):
            newdata.append(int(id))

        for image_id in newdata:
            Image.objects.get(id=image_id).delete()

        return http.HttpResponse()

    return http.HttpResponseForbidden()


# Image is tied to specified url containing the image ID
# The image is decoded and displayed on the url, as a result, these images can be displayed on other pages
def get_image(request, **kwargs):
    id = kwargs['pk']

    if Image.objects.filter(id=id).exists():

        image_data = Image.objects.get(id=id).binary_blob
        image = base64.b64decode(image_data)
        return http.HttpResponse(image, content_type="image/png")

    return http.HttpResponse()


# Disables the specified user's account if the logged in user is an administrator (staff)
def disable_user(request, **kwargs):
    if request.user.is_staff:
        user = User.objects.get(id=kwargs['user_id'])

        if user.is_active:
            user.is_active = False
            user.save()
            messages.success(request, "User account deactivated")

        else:
            messages.error(request, "User account is already deactivated")

    else:
        messages.error(request, "User is not a staff member")

    return http.HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# Reactivates specified user account if the logged in uesr is an administrator
def restore_user(request, **kwargs):
    if request.user.is_staff:
        user = User.objects.get(id=kwargs['user_id'])

        if not user.is_active:
            user.is_active = True
            user.save()
            messages.success(request, "User account reactivated")

        else:
            messages.error(request, "User account is already active")

    else:
        messages.error(request, "User is not a staff member")

    return http.HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# Handles all deletion of database entries
def delete(request, **kwargs):
    obj = kwargs['object']

    # Deletes posts if logged in user is author of the post or an administrator
    if obj == "post":
        post = Post.objects.get(id=kwargs['obj_id'])
        if request.user.is_staff or post.author == request.user:
            messages.success(request, "Successfully deleted post")
            post.delete()
            return http.HttpResponseRedirect("/game/" + str(post.game.id))
        else:
            messages.error(request, "User is not author or staff member")

    # Deletes user account if logged in user is an administrator
    # Accessible through the admin panel
    elif obj == "user":
        account = User.objects.get(id=kwargs['obj_id'])
        if request.user.is_staff and not account.is_active:
            messages.success(request, "Successfully deleted user account")
            account.delete()
            return http.HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            messages.error(request, "User is not a staff member")

    # Deletes comments if logged in user is author of the post or an administrator
    elif obj == "comment":
        comment = Comment.objects.get(id=kwargs['obj_id'])
        if request.user.is_staff or comment.user == request.user:
            messages.success(request, "Successfully deleted comment")
            comment.delete()

            if comment.post:
                return http.HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            messages.error(request, "User is not author or staff member")

    # Delete operations meant exclusively for administrators
    elif request.user.is_staff and obj != "post":
        match obj.lower():
            case "game":
                Game.objects.get(id=kwargs['obj_id']).delete()
                messages.success(request, "Successfully deleted game")
                return http.HttpResponseRedirect("/")

            case "developer":
                Developer.objects.get(id=kwargs['obj_id']).delete()
                messages.success(request, "Successfully deleted developer")

            case "publisher":
                Publisher.objects.get(id=kwargs['obj_id']).delete()
                messages.success(request, "Successfully deleted publisher")

            case "report":
                Report.objects.get(id=kwargs['obj_id']).delete()
                messages.success(request, "Successfully deleted report")

        return http.HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    elif obj != "post":
        messages.error(request, "User is not staff")


    return http.HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# Registration form template
# Password security checking is done by Django
class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'email']


# Login form template
# Password field input is hidden
class LoginForm(forms.Form):
    username = forms.CharField(max_length=40)
    password = forms.CharField(max_length=40, widget=forms.PasswordInput)


# Handles user login and register pages
class AccountView(generic.FormView):
    # Uses the relevant html file according to the current url
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

                # Checks if the email inputted already exists in another account
                if form.is_valid():
                    if not User.objects.filter(email=form.cleaned_data['email']).exists():
                        form.save()

                        # Used to limit usernames to 20 characters
                        un = form.cleaned_data['username'][:20]
                        pw = form.cleaned_data['password1']

                        # Authenticates the form data to make sure the forms are filled out correctly
                        # Creates a new UserData row associated with the newly created account
                        auth = authenticate(request, username=un, password=pw)
                        UserData.objects.create(user=User.objects.get(username=auth))

                        # Logs in the just registered user and redirects to home page
                        if auth:
                            login(request, auth)

                            messages.success(request, "Account successfully registered and logged in")
                            return http.HttpResponseRedirect("/")
                        else:
                            messages.error(request, "There was a problem registering, please try again")
                            return http.HttpResponseRedirect("/account/user/register/")

                    else:
                        messages.error(request, "Email is already in use")
                        return render(request, 'website/register.html', {'form': form})

                else:
                    # Displays all issues present in the registration form fields (username, password security)
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

                    # is_active controls whether a user's account is enabled or disabled
                    # Owners of disabled accounts are unable to log in
                    elif User.objects.filter(username=un).exists():
                        if not User.objects.get(username=un).is_active:
                            messages.error(request, "This account has been deactivated")
                            messages.error(request, "Please contact the administrator: admin@email.com")
                        else:
                            messages.error(request, "Incorrect password")

                    else:
                        messages.error(request, "This account does not exist")

                        msg_link = format_html(
                            "<a href={}>Click here to register</a>",
                            reverse("website:account", kwargs={"action": 'register'})
                        )
                        messages.error(request, msg_link)

                    return http.HttpResponseRedirect("/account/user/login/")


def log_user_out(request):
    logout(request)
    messages.success(request, "User logged out")
    return http.HttpResponseRedirect("/")


# Handles user profiles and displays user data
class UserProfile(generic.DetailView):
    model = User
    template_name = "website/userprofile.html"

    def get_context_data(self, **kwargs):
        user = User.objects.get(id=self.kwargs['pk'])
        userdata = UserData.objects.get(user=user)

        context = {
            'account': User.objects.get(id=self.kwargs['pk']),
            'userdata': userdata,
            'acc_posts': Post.objects.filter(author=self.kwargs['pk']),
            'form': CommentForm,
            'comments': Comment.objects.filter(profileuserdata=userdata).order_by("-date"),
            'sidebar_latest_comments': Comment.objects.filter(user=user).order_by("-date")[:6],
        }
        return context

    def post(self, request, **kwargs):
        if request.user.is_authenticated:
            user = User.objects.get(id=self.kwargs['pk'])

            if 'comment' in request.POST:
                content = self.request.POST['content']
                userdata = UserData.objects.get(user=user)
                Comment.objects.create(user=self.request.user, content=content, profileuserdata=userdata, date=datetime.now())

            # Submits a report to the administrators
            # If a report already exists, increase that report's count by 1
            elif 'report' in request.POST:
                form = self.request.POST
                content = form['reason']

                if content == "other":
                    content = form['reason-other']

                if Report.objects.filter(reason=content, user=user).exists():
                    current_report = Report.objects.get(reason=content, user=user)
                    current_report.count += 1
                    current_report.save()

                else:
                    Report.objects.create(reason=content, user=user)

                messages.success(request, "User has been reported")

        else:
            return http.HttpResponseRedirect('account/user/register/')


        return http.HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# Changes if a report is approved or unapproved
# Approved reports are shown higher up than unapproved reports and they cannot be deleted until unapproved
def toggle_report_approval(request, **kwargs):
    if request.user.is_staff:
        report = Report.objects.get(id=kwargs['report'])
        report.approved = not report.approved
        report.save()

        if report.approved:
            messages.success(request, "Report approved")
        else:
            messages.success(request, "Report unapproved")
    else:
        messages.error(request, "User is not staff member")

    return http.HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# Sorts games by amount of posts created for this game
def sort_postcount(e):
    if e.__class__.__name__ == "Game":
        return len(Post.objects.filter(game=e))
    return -1


# Handles account settings where users can change account information
class UserSettings(generic.FormView):
    model = User
    template_name = "website/usersettings.html"

    def post(self, request, *args, **kwargs):
        form = self.request.POST
        files = self.request.FILES

        userdata = UserData.objects.get(user=request.user)

        # The tabs of settings have separate form submit buttons,
        # which will be the tab that appears when the page refreshes
        # Checks all form input fields and makes changes regarding those which are not empty
        if form['tab'] == "account":

            # Changes username if the chosen username does not already exist
            # Must input password to make this change
            new_username = form['new_username']
            if new_username != '':
                if check_password(form['username_password_auth'], request.user.password):
                    if not User.objects.filter(username=new_username).exists():
                        user = request.user
                        user.username = new_username[:20]
                        user.save()

                        messages.success(request, "Username updated")
                    else:
                        messages.error(request, "Username already exists")
                else:
                    messages.error(request, "Incorrect password")

            return http.HttpResponseRedirect("?tab=account")

            # Changes the user's password
            # Must input password to make this change
            # New password must be entered in two fields
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

        if form['tab'] == "profile":
            if files:
                profile_picture = files['picture']

                # Saves new profile picture and adds it to UserData
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

            # Updates the profile description
            description = form['description']
            if description != userdata.description:
                userdata.description = description
                userdata.save()

                messages.success(request, "Profile description updated")

            return http.HttpResponseRedirect("?tab=profile")


        return http.HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    # Sends UserData and the default tab to the frontend
    def get_context_data(self, **kwargs):
        tab = self.request.GET.get("tab")

        if not tab:
            tab = "profile"

        return {
            'userdata': UserData.objects.get(user=self.request.user),
            'tab': tab,
        }


# Sorts objects alphabetically
def sort_title(e):
    name = e.__class__.__name__
    if name == "User":
        return e.username.lower()
    else:
        return e.title.lower()


# Sorts objects by date, excluding time
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


# Sorts objects by ID
def sort_id(e):
    return e.id


# Sorts objects alphabetically by the name of the object's class (User, Post, Game, etc.)
def sort_type(e):
    return e.__class__.__name__


# Returns search query from the search box on the navbar
def get_search_results(query, sortmethod):
    # All ojects are filtered by title and description, or users by their usernames
    post = Post.objects.filter(Q(title__icontains=query) | Q(content__icontains=query))
    game = Game.objects.filter(Q(title__icontains=query) | Q(description__icontains=query))
    developer = Developer.objects.filter(Q(title__icontains=query) | Q(description__icontains=query))
    publisher = Publisher.objects.filter(Q(title__icontains=query) | Q(description__icontains=query))
    user = User.objects.filter(Q(username__icontains=query))

    # Combines all objects into one list
    query_list = list(chain(post, game, developer, publisher, user))

    # Default sorting method
    if not sortmethod:
        sortmethod = "title"

    # Sorts all combined objects by specified sorting method
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


# Handles the search page
# Search results are handled by the function get_search_results()
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


# Adds or removes instances of users liking an object
# If a user has disliked the object, the dislike will be removed before the like is added
def like_game(request, game):
    if LikesUserMap.objects.filter(user=request.user, game=Game.objects.get(id=game)).exists():
        obj = LikesUserMap.objects.get(user=request.user, game=Game.objects.get(id=game))
        obj.delete()

    else:
        if DislikesUserMap.objects.filter(user=request.user, game=Game.objects.get(id=game)).exists():
            DislikesUserMap.objects.get(user=request.user, game=Game.objects.get(id=game)).delete()

        like = LikesUserMap(user=request.user, game=Game.objects.get(id=game))
        like.save()

    likes = len(LikesUserMap.objects.filter(game=Game.objects.get(id=game))) - len(
        DislikesUserMap.objects.filter(game=Game.objects.get(id=game)))

    has_liked = LikesUserMap.objects.filter(user=request.user, game=game).exists()

    return http.JsonResponse({"like": likes, "has_liked": has_liked}, status=201)


# Adds or removes instances of users disliking an object
# If a user has liked the object, the like will be removed before the dislike is added
def dislike_game(request, game):
    if DislikesUserMap.objects.filter(user=request.user, game=Game.objects.get(id=game)).exists():
        obj = DislikesUserMap.objects.get(user=request.user, game=Game.objects.get(id=game))
        obj.delete()

    else:
        if LikesUserMap.objects.filter(user=request.user, game=Game.objects.get(id=game)).exists():
            LikesUserMap.objects.get(user=request.user, game=Game.objects.get(id=game)).delete()

        dislike = DislikesUserMap(user=request.user, game=Game.objects.get(id=game))
        dislike.save()

    likes = len(LikesUserMap.objects.filter(game=Game.objects.get(id=game))) - len(
        DislikesUserMap.objects.filter(game=Game.objects.get(id=game)))

    has_disliked = DislikesUserMap.objects.filter(user=request.user, game=game).exists()

    return http.JsonResponse({"like": likes, "has_disliked": has_disliked}, status=201)


# Functions the same way as like_game() on line 1064, but is used for posts instead
def like_post(request, post):
    if LikesUserMap.objects.filter(user=request.user, post=Post.objects.get(id=post)).exists():
        obj = LikesUserMap.objects.get(user=request.user, post=Post.objects.get(id=post))
        obj.delete()

    else:
        if DislikesUserMap.objects.filter(user=request.user, post=Post.objects.get(id=post)).exists():
            DislikesUserMap.objects.get(user=request.user, post=Post.objects.get(id=post)).delete()

        like = LikesUserMap(user=request.user, post=Post.objects.get(id=post))
        like.save()

    likes = len(LikesUserMap.objects.filter(post=Post.objects.get(id=post))) - len(
        DislikesUserMap.objects.filter(post=Post.objects.get(id=post)))
    has_liked = LikesUserMap.objects.filter(user=request.user, post=post).exists()

    return http.JsonResponse({"like": likes, "has_liked": has_liked}, status=201)


# Functions the same way as dislike_game on line 1086, but is used for posts instead
def dislike_post(request, post):
    if DislikesUserMap.objects.filter(user=request.user, post=Post.objects.get(id=post)).exists():
        obj = DislikesUserMap.objects.get(user=request.user, post=Post.objects.get(id=post))
        obj.delete()

    else:
        if LikesUserMap.objects.filter(user=request.user, post=Post.objects.get(id=post)).exists():
            LikesUserMap.objects.get(user=request.user, post=Post.objects.get(id=post)).delete()

        dislike = DislikesUserMap(user=request.user, post=Post.objects.get(id=post))
        dislike.save()

    likes = len(LikesUserMap.objects.filter(post=Post.objects.get(id=post))) - len(
        DislikesUserMap.objects.filter(post=Post.objects.get(id=post)))
    has_disliked = DislikesUserMap.objects.filter(user=request.user, post=post).exists()

    return http.JsonResponse({"like": likes, "has_disliked": has_disliked}, status=201)


# Handles the posts list page, where all posts are visible, has sorting options
# Shows latest posts and games on the sidebar
class PostsListView(generic.ListView):
    template_name = "website/postslist.html"
    model = Post

    def get_context_data(self, **kwargs):
        post_list = list(Post.objects.all())
        post_list.sort(key=sort_popularity, reverse=True)

        sort = self.request.GET.get("sort")
        if sort and sort != "popularity":
            order = get_order(sort)
            post_list = Post.objects.all().order_by(order)
        else:
            sort = "popularity"

        return {
            'post_list': post_list,
            'latest_reviews': Post.objects.order_by("-id")[:5],
            'latest_games': Game.objects.order_by("-id")[:5],
            'sort': sort,
        }
