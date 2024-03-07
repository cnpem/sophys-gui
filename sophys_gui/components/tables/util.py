HISTORY_BTNS = [
    {
        "title": "Clear All",
        "icon": "mdi.sort-variant-remove",
        "cmd": lambda re: re.clear_all(),
        "enabled": True,
        "confirm": True,
        "permission": 0,
        "tooltip": "Delete all the history items."
    },
    {
        "title": "Copy to Queue",
        "icon": "mdi6.content-copy",
        "cmd": lambda re: re.copy_to_queue(),
        "enabled": False,
        "permission": 1,
        "tooltip": "Duplicate the selected item to the end of the queue list."
    }
]
