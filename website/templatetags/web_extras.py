from django import template
from website.models import LikesUserMap

register = template.Library()


@register.filter
def get_model_name(value):
    return value.__class__.__name__


@register.filter
def get_url(value):
    match value.__class__.__name__:
        case "Game":
            return 'website:game'

        case "Post":
            return 'website:post'

        case "User":
            return 'website:profile'

        case "Developer":
            return 'website:developer'

        case "Publisher":
            return 'website:publisher'

    return None


@register.filter
def count_likes(value):
    match value.__class__.__name__:
        case "Game":
            return len(LikesUserMap.objects.filter(game=value))
        case "Post":
            return len(LikesUserMap.objects.filter(post=value))
