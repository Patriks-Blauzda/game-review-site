from django import template
from website.models import LikesUserMap
from website.models import DislikesUserMap

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
            return len(LikesUserMap.objects.filter(game=value)) - len(DislikesUserMap.objects.filter(game=value))
        case "Post":
            return len(LikesUserMap.objects.filter(post=value)) - len(DislikesUserMap.objects.filter(post=value))
    return 0


@register.filter
def is_liked(value, user):
    match value.__class__.__name__:
        case "Game":
            return LikesUserMap.objects.filter(user=user, game=value).exists()
        case "Post":
            return LikesUserMap.objects.filter(user=user, post=value).exists()
    return False


@register.filter
def is_disliked(value, user):
    match value.__class__.__name__:
        case "Game":
            return DislikesUserMap.objects.filter(user=user, game=value).exists()
        case "Post":
            return DislikesUserMap.objects.filter(user=user, post=value).exists()
    return False


@register.filter
def count_user_score(value):
    return len(LikesUserMap.objects.filter(user=value)) - len(DislikesUserMap.objects.filter(user=value))