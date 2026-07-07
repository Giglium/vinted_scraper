"""Enum representing extractable OpenGraph fields from a Vinted item page."""

from enum import Enum


class OgField(str, Enum):
    """Available OpenGraph fields that can be extracted from an item page.

    Members:
        TITLE: The item title (derived from og:description).
        DESCRIPTION: The full item description (og:description).
        URL: The canonical item URL (og:url).
        IMAGE: The item image URL (og:image).
    """

    TITLE = "title"
    DESCRIPTION = "description"
    URL = "url"
    IMAGE = "image"
