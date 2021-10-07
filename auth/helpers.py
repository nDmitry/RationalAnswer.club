import logging
from datetime import datetime, timedelta

import jwt
from django.shortcuts import redirect, render, get_object_or_404

from auth.models import Session, Apps
from club import settings, features
from club.exceptions import AccessDenied, ApiAuthRequired, ApiAccessDenied
from users.models.user import User
from posts.models.post import Post

log = logging.getLogger(__name__)


def authorized_user(request):
    user, _ = authorized_user_with_session(request)
    return user


def authorized_user_with_session(request):
    auth_token = request.COOKIES.get("token") or request.GET.get("token")
    if auth_token:
        return user_by_token(auth_token)

    jwt_token = request.COOKIES.get("jwt") or request.GET.get("jwt")
    if jwt_token:
        return user_by_jwt(jwt_token)

    return None, None


def user_by_token(token):
    session = Session.objects\
        .filter(token=token)\
        .order_by()\
        .select_related("user")\
        .first()

    if not session or session.expires_at <= datetime.utcnow():
        return None, None  # session is expired

    return session.user, session


def user_by_jwt(jwt_token):
    try:
        payload = jwt.decode(jwt_token, settings.JWT_PUBLIC_KEY, algorithms=[settings.JWT_ALGORITHM])
    except (jwt.DecodeError, jwt.ExpiredSignatureError):
        return None, None  # bad jwt token

    user = get_object_or_404(User, slug=payload["user_slug"])

    return user, None


def auth_required(view):
    def wrapper(request, *args, **kwargs):
        access_denied = check_user_permissions(request)
        if access_denied:
            return access_denied

        return view(request, *args, **kwargs)

    return wrapper


def check_user_permissions(request, **context):
    public_pages = [] # for exact matching
    public_paths = [] # for partial matching

    if request.me:
        public_paths.extend(["/profile/", "/auth/", "/intro/", "/network/", "/messages/"])

    if features.PUBLIC_CONTENT:
        public_pages.append("/")
        public_paths.extend(["/network/", "/search/", "/room/", "/telegram/", "/all/", "/user/"])
        public_paths.extend(["/{}/".format(t) for t in dict(Post.TYPES).keys()]) # including intros
        public_paths.append("/label/")

    is_public = "/edit" not in request.path and (
        request.path in public_pages or \
        len([p for p in public_paths if request.path.startswith(p)]) > 0
    )

    if is_public:
        return None

    if not request.me:
        return render(request, "auth/access_denied.html", context, status=403)

    if request.me.membership_expires_at < datetime.utcnow():
        log.info("User membership expired. Redirecting to payments page...")
        return redirect("membership_expired")

    if request.me.is_banned:
        log.info("User was banned. Redirecting to 'banned' page...")
        return redirect("banned")

    if request.me.moderation_status == User.MODERATION_STATUS_INTRO:
        log.info("New user. Redirecting to intro...")
        return redirect("intro")

    if request.me.moderation_status == User.MODERATION_STATUS_REJECTED:
        log.info("Rejected user. Redirecting to 'rejected' page...")
        return redirect("rejected")

    if request.me.moderation_status == User.MODERATION_STATUS_ON_REVIEW:
        log.info("User on review. Redirecting to 'on_review' page...")
        return redirect("on_review")

    return None


def moderator_role_required(view):
    def wrapper(request, *args, **kwargs):
        if not request.me:
            return redirect("login")

        if not request.me.is_moderator:
            raise AccessDenied()

        return view(request, *args, **kwargs)

    return wrapper


def curator_role_required(view):
    def wrapper(request, *args, **kwargs):
        if not request.me:
            return redirect("login")

        if not request.me.is_curator:
            raise AccessDenied()

        return view(request, *args, **kwargs)

    return wrapper


def api_required(view):
    def wrapper(request, *args, **kwargs):
        if not request.me:
            raise ApiAuthRequired()

        return view(request, *args, **kwargs)

    return wrapper


def auth_switch(no, yes):
    def result(request, *args, **kwargs):
        is_authorized = request.me is not None
        if is_authorized:
            return yes(request, *args, **kwargs)
        else:
            return no(request, *args, **kwargs)

    return result


def set_session_cookie(response, user, session):
    response.set_cookie(
        key="token",
        value=session.token,
        expires=max(user.membership_expires_at, datetime.utcnow() + timedelta(days=30)),
        httponly=True,
        secure=not settings.DEBUG,
    )
    return response
