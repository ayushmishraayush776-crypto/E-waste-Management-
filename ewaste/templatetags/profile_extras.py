from django import template

register = template.Library()


@register.filter(name='is_company')
def is_company(user):
    """Return True if user has a profile and is a company member."""
    try:
        profile = getattr(user, 'profile', None)
        return bool(profile and getattr(profile, 'is_company', False))
    except Exception:
        return False
