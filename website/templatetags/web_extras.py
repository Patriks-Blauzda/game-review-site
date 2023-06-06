from django import template
from django.contrib.auth.models import User
from website.models import LikesUserMap
from website.models import DislikesUserMap
from website.models import UserData
from website.models import Report

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
    value.refresh_from_db()
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


@register.filter
def get_image_from_user(value):
    if isinstance(value, User):
        return UserData.objects.get(user=value).image


@register.filter
def get_image_id_from_user(value):
    return UserData.objects.get(user=value).image.id


@register.filter
def count_reports(user):
    reports = Report.objects.filter(user=user)

    count = 0
    for report in reports:
        count += report.count

    return count

