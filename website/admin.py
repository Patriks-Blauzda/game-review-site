from django.contrib import admin

from .models import Game
from .models import Post
from .models import Image
from .models import LikesUserMap
from .models import DislikesUserMap
from .models import UserData

# Register your models here.
admin.site.register(Game)
admin.site.register(Post)
admin.site.register(Image)
admin.site.register(LikesUserMap)
admin.site.register(DislikesUserMap)
admin.site.register(UserData)
