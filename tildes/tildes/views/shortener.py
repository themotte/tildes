# Copyright (c) 2018 Tildes contributors <code@tildes.net>
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Views related to the link shortener."""
from typing import NoReturn

from pyramid.httpexceptions import HTTPMovedPermanently
from pyramid.request import Request
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.view import view_config


@view_config(route_name="shortener_group", permission=NO_PERMISSION_REQUIRED)
def get_shortener_group(request: Request) -> NoReturn:
    """Redirect to the base path of a group."""
    site_name = request.registry.settings["tildes.site_name"]
    destination = f"https://{site_name}/~{request.context.path}"
    raise HTTPMovedPermanently(location=destination)


@view_config(route_name="shortener_topic", permission=NO_PERMISSION_REQUIRED)
def get_shortener_topic(request: Request) -> NoReturn:
    """Redirect to the full permalink for a topic."""
    site_name = request.registry.settings["tildes.site_name"]
    destination = f"https://{site_name}{request.context.permalink}"
    raise HTTPMovedPermanently(location=destination)
