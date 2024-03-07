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


QUEUE_BTNS = [
    {
        "title": "Top",
        "icon": "ri.align-top",
        "cmd": lambda re: re.move_top(),
        "enabled": False,
        "permission": 3,
        "tooltip": "Move the selected item to the first position of the queue."
    },
    {
        "title": "Up",
        "icon": "fa5s.arrow-up",
        "cmd": lambda re: re.move_up(),
        "enabled": False,
        "permission": 3,
        "tooltip": "Move the selected item to one position ahead in the queue."
    },
    {
        "title": "Down",
        "icon": "fa5s.arrow-down",
        "cmd": lambda re: re.move_down(),
        "enabled": False,
        "permission": 2,
        "tooltip": "Move the selected item to one position back in the queue."
    },
    {
        "title": "Bottom",
        "icon": "ri.align-bottom",
        "cmd": lambda re: re.move_bottom(),
        "enabled": False,
        "permission": 2,
        "tooltip": "Move the selected item to the last position of the queue."
    },
    {
        "title": "Delete",
        "icon": "fa5s.trash-alt",
        "cmd": lambda re: re.delete_item(),
        "enabled": False,
        "confirm": True,
        "permission": 1,
        "tooltip": "Delete the selected item from the queue."
    },
    {
        "title": "Duplicate",
        "icon": "fa5s.clone",
        "cmd": lambda re: re.duplicate_item(),
        "enabled": False,
        "permission": 1,
        "tooltip": "Duplicate the selected item data into a new queue "\
            "item that will be placed after the selected item."
    },
    {
        "title": "Copy",
        "icon": "fa5s.copy",
        "cmd": lambda re: re.copy_queue_item(),
        "enabled": False,
        "permission": 1,
        "tooltip": "Copy the selected item data into a form for creating a " \
            "new queue item that will be placed after the selected item."
    },
    {
        "title": "Edit",
        "icon": "fa5s.pencil-alt",
        "cmd": lambda re: re.edit_queue_item(),
        "enabled": False,
        "permission": 1,
        "tooltip": "Copy the selected item data into a form that will " \
            "update selected item."
    },
    {
        "title": "Clear All",
        "icon": "mdi.sort-variant-remove",
        "cmd": lambda re: re.clear_all(),
        "enabled": True,
        "confirm": True,
        "permission": 0,
        "tooltip": "Delete all the queue items."
    },
    {
        "title": "Add Plan",
        "icon": "fa5s.plus",
        "cmd": lambda re: re.add_plan_item(),
        "enabled": True,
        "permission": 0,
        "tooltip": "Open a form that will create a new queue item " \
            "and placed it in the last position of the queue."
    },
    {
        "title": "Add Instruction",
        "icon": "mdi6.block-helper",
        "cmd": lambda re: re.add_instruction_item(),
        "enabled": True,
        "permission": 0,
        "tooltip": "Add a customized instruction " \
            "and placed it in the last position of the queue."
    },
    {
        "title": "Add Stop Item",
        "icon": "mdi6.block-helper",
        "cmd": lambda re: re.add_stop_queue(),
        "enabled": True,
        "permission": 0,
        "tooltip": "Add an instruction for stopping the queue " \
            "and placed it in the last position of the queue."
    }
]

QUEUE_TABLE_BTNS = [
    {
        "icon": "fa5s.pencil-alt",
        "cmd": lambda re: re.edit_queue_item(),
        "enabled": True,
        "tooltip": "",
        "permission": 0
    },
    {
        "icon": "fa5s.trash-alt",
        "cmd": lambda re: re.delete_item(),
        "enabled": True,
        "confirm": True,
        "tooltip": "",
        "permission": 0
    }
]
