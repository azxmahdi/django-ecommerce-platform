from urllib.parse import urlparse
from django.conf import settings


def is_safe_url(url, allowed_hosts=None):

    if not url:
        return False

    if allowed_hosts is None:
        allowed_hosts = set(settings.ALLOWED_HOSTS)
        if settings.DEBUG:
            allowed_hosts.add("localhost:8000")
            allowed_hosts.add("127.0.0.1:8000")
            allowed_hosts.add("[::1]")

    try:
        parsed = urlparse(url)
    except Exception:
        return False

    if parsed.scheme and parsed.scheme not in ("http", "https"):
        return False

    if parsed.netloc and parsed.netloc not in allowed_hosts:
        return False

    return True


def get_redirect_url(request, default_url=None):

    if default_url is None:
        default_url = settings.LOGIN_REDIRECT_URL

    next_url = request.GET.get("next") or request.POST.get("next")

    if next_url and is_safe_url(next_url):
        return next_url

    next_url = request.session.get("next_url")

    if next_url and is_safe_url(next_url):
        if "next_url" in request.session:
            del request.session["next_url"]
        return next_url

    return default_url


def set_next_url_logout(request):

    url = request.META.get("HTTP_REFERER")
    if url and is_safe_url(url):
        request.session["next_url"] = url
        return True
    return False


def set_next_url(request, url=None):

    if url and is_safe_url(url):
        request.session["next_url"] = url
        return True
    return False
