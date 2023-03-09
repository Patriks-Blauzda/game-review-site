from django import template

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
