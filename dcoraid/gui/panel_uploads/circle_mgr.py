from functools import lru_cache

from PyQt6 import QtWidgets

from ..api import get_ckan_api


@lru_cache(maxsize=1)
def get_user_circle_dicts():
    """Conveniently cache the organization list for the user

    You must call `get_user_circle_dicts.cache_clear`
    if the circle list changes (e.g. because you added one).
    """
    api = get_ckan_api()
    circles = api.get("organization_list_for_user",
                      permission="create_dataset")
    return circles


def ask_for_new_circle(parent_widget):
    """Ask the user to create a new circle

    Returns
    -------
    circle_dict: dict or None
        The CKAN organization dictionary. None is returned if the
        user did not create a circle.
    """
    api = get_ckan_api()
    # Ask the user whether he would like to create a circle.
    ud = api.get_user_dict()
    name = ud["fullname"] if ud["fullname"] else ud["name"]
    text, ok_pressed = QtWidgets.QInputDialog.getText(
        parent_widget,
        "Circle required",
        f"You do not have access to any existing Circles. To upload\n"
        f"datasets, you need to be either Editor or Admin in\n"
        f"a Circle. You may create a Circle now or cancel and ask\n"
        f"a colleague to add you to a Circle (Your user name is "
        f"'{ud['name']}')."
        f"\n\nTo proceed with Circle creation, please choose a name:",
        QtWidgets.QLineEdit.EchoMode.Normal,
        f"{name}'s Circle")
    if ok_pressed and text != '':
        cdict = api.post("organization_create",
                         data={"name": f"user-circle-{ud['name']}",
                               "title": text.strip(),
                               })
        # invalidate cache, because now we have a new circle
        get_user_circle_dicts.cache_clear()
        return cdict


def request_circle(parent_widget):
    """Ask the user to select a circle

    If only a single circle is present in the list, than this circle
    is used without user interaction.

    Returns
    -------
    circle_dict: dict or None
        The CKAN organization dictionary. None is returned if the
        user aborted.
    """
    circs = get_user_circle_dicts()
    if len(circs) == 1:
        return circs[0]
    elif len(circs) == 0:
        return ask_for_new_circle(parent_widget)
    else:
        # Show a dialog with choices
        circle_texts = [c["title"] if c["title"] else c["name"] for c in circs]
        text, ok_pressed = QtWidgets.QInputDialog.getItem(
            parent_widget,
            "Please choose a circle",
            "You have upload-permissions to multiple circles. Please\n"
            "choose the one where you wish to upload your datasets to.",
            circle_texts,
            0,  # default index
            False,  # not editable
        )
        if ok_pressed:
            cid = circle_texts.index(text)
            return circs[cid]
