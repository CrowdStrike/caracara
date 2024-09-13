"""Caracara: CrowdStrike Style Radio Dialog for Prompt Toolkit."""

from __future__ import annotations

from typing import Any, Sequence, TypeVar

from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app
from prompt_toolkit.formatted_text import AnyFormattedText
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.key_binding.defaults import load_key_bindings
from prompt_toolkit.key_binding.key_bindings import KeyBindings, merge_key_bindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import AnyContainer, HSplit
from prompt_toolkit.styles import BaseStyle, Style, merge_styles
from prompt_toolkit.widgets import Button, Dialog, Label, RadioList

# Prompt Toolkit uses _T for the generic type
_T = TypeVar("_T")


def _create_app(dialog: AnyContainer, style: BaseStyle | None) -> Application[Any]:
    """Turn a container into a Prompt Toolkit Application."""
    bindings = KeyBindings()
    bindings.add("tab")(focus_next)
    bindings.add("s-tab")(focus_previous)

    return Application(
        layout=Layout(dialog),
        key_bindings=merge_key_bindings([load_key_bindings(), bindings]),
        mouse_support=True,
        style=style,
        full_screen=True,
    )


def _return_none() -> None:
    """Button handler that returns None.

    This is used by cancel buttons.
    """
    get_app().exit()


CS_STYLE = Style.from_dict(
    {
        "button": "fg:#1A1A1A bold",
        "button.arrow": "fg:#FC0000 bold",
        "button.focused": "fg:#FFFFFF bg:#2F8BAA",
        "button.text": "fg:#1A1A1A bold",
        "dialog": "bg:#58595B",
        "dialog.body": "bg:#F3F3F4",
        "dialog.body label": "fg:#FC0000",
        "dialog frame.label": "bg:#F3F4F4 #1A1A1A",
        "dialog shadow": "bg:#68696B",
        "frame.label": "fg:#FC0000",
        "label": "#FC0000",
        "radio-list": "#1A1A1A",
        "radio-checked": "fg:#2F8BAA",
    }
)


def csradiolist_dialog(  # pylint: disable=too-many-arguments
    title: AnyFormattedText = "",
    text: AnyFormattedText = "",
    ok_text: str = "Ok",
    cancel_text: str = "Cancel",
    values: Sequence[tuple[_T, AnyFormattedText]] | None = None,
    default: _T | None = None,
    style: BaseStyle | None = None,
) -> Application[_T]:
    """Display a CrowdStrike styled simple list of elements that the user can choose from.

    This function is heavily based on the radiolist_dialog function provided by Prompt Toolkit,
    with some tweaks in place to handle a lack of cancel button (where desired) and a default
    set of styles.

    Only one element can be selected at a time using Arrow keys and Enter.
    The focus can be moved between the list and the Ok/Cancel button with tab.
    """
    if values is None:
        values = []

    def ok_handler() -> None:
        get_app().exit(result=radio_list.current_value)

    radio_list = RadioList(values=values, default=default)

    buttons = [Button(text=ok_text, handler=ok_handler)]

    if cancel_text is not None:
        buttons.append(Button(text=cancel_text, handler=_return_none))

    dialog = Dialog(
        title=title,
        body=HSplit(
            [Label(text=text, dont_extend_height=True), radio_list],
            padding=1,
        ),
        buttons=buttons,
        with_background=True,
    )

    if style is None:
        style = CS_STYLE
    else:
        style = merge_styles([CS_STYLE, style])

    app = _create_app(dialog, style)

    return app
