from django.contrib import admin

from .models import Game
from .models import Post
from .models import Image

# Register your models here.
admin.site.register(Game)
admin.site.register(Post)
admin.site.register(Image)
