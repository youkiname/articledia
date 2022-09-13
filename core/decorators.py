from django.core.exceptions import PermissionDenied
from .services import check_ban, get_client_ip


def login_required(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def superuser_required(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_superuser:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def has_access(access_types: list[str]):
    def wrapper(view_func):
        def wrapped(request, *args, **kwargs):
            if check_ban(get_client_ip(request), access_types):
                raise PermissionDenied
            else:
                return view_func(request, *args, **kwargs)
        return wrapped
    return wrapper
