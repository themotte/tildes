# Copyright (c) 2018 Tildes contributors <code@tildes.net>
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Views related to logging in/out."""

from datetime import timedelta
from typing import NoReturn
from urllib.parse import unquote_plus

from marshmallow.fields import String
from pyramid.httpexceptions import HTTPFound, HTTPUnauthorized, HTTPUnprocessableEntity
from pyramid.renderers import render_to_response
from pyramid.request import Request
from pyramid.response import Response
from pyramid.security import NO_PERMISSION_REQUIRED, remember
from pyramid.view import view_config

from tildes.enums import LogEventType
from tildes.metrics import incr_counter
from tildes.models.log import Log
from tildes.models.user import User
from tildes.schemas.user import UserSchema
from tildes.views.decorators import not_logged_in, rate_limit_view, use_kwargs


@view_config(
    route_name="login", renderer="login.jinja2", permission=NO_PERMISSION_REQUIRED
)
@use_kwargs({"from_url": String(missing="")})
@not_logged_in
def get_login(request: Request, from_url: str) -> dict:
    """Display the login form."""
    # pylint: disable=unused-argument
    return {"from_url": unquote_plus(from_url)}


def finish_login(request: Request, user: User, redirect_url: str) -> HTTPFound:
    """Save the user ID into session and return a redirect to appropriate page."""
    # Username/password were correct - attach the user_id to the session
    remember(request, user.user_id)

    # Depending on "keep me logged in", set session timeout to 1 year or 1 day
    if request.params.get("keep"):
        request.session.adjust_timeout_for_session(31_536_000)
    else:
        request.session.adjust_timeout_for_session(86400)

    # set request.user before logging so the user is associated with the event
    request.user = user
    request.db_session.add(Log(LogEventType.USER_LOG_IN, request))

    # only use redirect_url if it's a relative url, so we can't redirect to other sites
    if redirect_url.startswith("/"):
        return HTTPFound(location=redirect_url)

    return HTTPFound(location="/")


@view_config(
    route_name="login", request_method="POST", permission=NO_PERMISSION_REQUIRED
)
@use_kwargs(
    UserSchema(
        only=("username", "password"), context={"username_trim_whitespace": True}
    ),
    location="form",
)
@use_kwargs({"from_url": String(missing="")}, location="form")
@not_logged_in
@rate_limit_view("login")
def post_login(
    request: Request, username: str, password: str, from_url: str
) -> Response:
    """Process a log in request."""
    incr_counter("logins")

    # Look up the user for the supplied username
    user = (
        request.query(User)
        .undefer_all_columns()
        .filter(User.username == username)
        .one_or_none()
    )

    # If the username doesn't exist, tell them so - usually this isn't considered a good
    # practice, but it's completely trivial to check if a username exists on Tildes
    # anyway (by visiting /user/<username>), so it's better to just let people know if
    # they're trying to log in with the wrong username
    if not user:
        incr_counter("login_failures")

        # log the failure - need to manually commit because of the exception
        log_entry = Log(
            LogEventType.USER_LOG_IN_FAIL,
            request,
            {"username": username, "reason": "Nonexistent username"},
        )
        request.db_session.add(log_entry)
        request.tm.commit()

        raise HTTPUnprocessableEntity("That username does not exist")

    if not user.is_correct_password(password):
        incr_counter("login_failures")

        # log the failure - need to manually commit because of the exception
        log_entry = Log(
            LogEventType.USER_LOG_IN_FAIL,
            request,
            {"username": username, "reason": "Incorrect password"},
        )
        request.db_session.add(log_entry)
        request.tm.commit()

        raise HTTPUnprocessableEntity("Incorrect password")

    # Don't allow banned users to log in
    if user.is_banned:
        if user.ban_expiry_time:
            # add an hour to the ban's expiry time since the cronjob runs hourly
            unban_time = user.ban_expiry_time + timedelta(hours=1)
            unban_time = unban_time.strftime("%Y-%m-%d %H:%M (UTC)")

            raise HTTPUnprocessableEntity(
                "That account is temporarily banned. "
                f"The ban will be lifted at {unban_time}"
            )

        raise HTTPUnprocessableEntity("That account has been banned")

    # If 2FA is enabled, save username to session and make user enter code
    if user.two_factor_enabled:
        request.session["two_factor_username"] = username
        return render_to_response(
            "tildes:templates/intercooler/login_two_factor.jinja2",
            {"keep": request.params.get("keep"), "from_url": from_url},
            request=request,
        )

    raise finish_login(request, user, from_url)


@view_config(
    route_name="login_two_factor",
    request_method="POST",
    permission=NO_PERMISSION_REQUIRED,
)
@not_logged_in
@rate_limit_view("login_two_factor")
@use_kwargs(
    {"code": String(missing=""), "from_url": String(missing="")}, location="form"
)
def post_login_two_factor(request: Request, code: str, from_url: str) -> NoReturn:
    """Process a log in request with 2FA."""
    # Look up the user for the supplied username
    user = (
        request.query(User)
        .undefer_all_columns()
        .filter(User.username == request.session["two_factor_username"])
        .one_or_none()
    )

    if not user.is_correct_two_factor_code(code):
        raise HTTPUnauthorized(body="Invalid code, please try again.")

    del request.session["two_factor_username"]
    raise finish_login(request, user, from_url)


@view_config(route_name="logout", request_method="POST")
def post_logout(request: Request) -> HTTPFound:
    """Process a log out request."""
    request.session.invalidate()
    request.db_session.add(Log(LogEventType.USER_LOG_OUT, request))

    raise HTTPFound(location="/")
