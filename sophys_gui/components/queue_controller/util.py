CONFIG = {
    "start": [
        {
            'icon': 'fa5s.play',
            'title': 'Start',
            'cmd': lambda re: re.queue_start(),
            "tooltip": "Start running the first queue item."
        },
        {
            'icon': 'fa5s.pause',
            'title': 'Pause',
            'cmd': lambda re: re.re_pause(option='deferred'),
            "tooltip": "Pause the running item."
        },
        {
            'icon': 'fa5s.play',
            'title': 'Resume',
            'cmd': lambda re: re.re_resume(),
            "tooltip": "Resume running the paused queue item."
        }
    ],
    "start_monitor": [
        {
            'icon': 'fa5s.play',
            'title': 'Start',
            'cmd': lambda _: print(""),
            'enabled': False,
            "tooltip": "Start running the first queue item."
        },
        {
            'icon': 'fa5s.pause',
            'title': 'Pause',
            'cmd': lambda re: re.re_pause(option='deferred'),
            "tooltip": "Pause the running item."
        },
        {
            'icon': 'fa5s.play',
            'title': 'Resume',
            'cmd': lambda re: re.re_resume(),
            "tooltip": "Resume running the paused queue item."
        }
    ],
    "stop": [
        {
            'icon': 'fa5s.stop',
            'title': 'Stop',
            'cmd': lambda re: re.re_pause(option="deferred"),
            'enabled': False,
            "tooltip": "Stop running the queue list."
        },
        {
            'icon': 'fa5s.stop',
            'title': 'Stop',
            'cmd': lambda re: re.queue_stop(),
            "tooltip": "Stop running the queue list."
        },
        {
            'icon': 'fa5s.stop',
            'title': 'Abort',
            'cmd': lambda re: re.re_abort(),
            "tooltip": "Cancel running the paused item. This will item will " \
                "show in the history with the aborted status."
        }
    ],
    "help": [
        {
            'icon': 'fa5s.pause-circle',
            'title': 'Pause Now',
            'cmd': lambda re: re.re_pause(option="deferred"),
            'enabled': False,
            "tooltip": "Pause the execution now. This may cause the plan to fail later."
        },
        {
            'icon': 'fa5s.pause-circle',
            'title': 'Pause Now',
            'cmd': lambda re: re.re_pause(option="immediate"),
            "tooltip": "Pause the execution now. This may cause the plan to fail later."
        },
        {
            'icon': 'mdi6.restore',
            'title': 'Halt',
            'cmd': lambda re: re.re_halt(),
            "tooltip": "Halt the running plan."
        }
    ],
    "env": [
        {
            'icon': 'mdi6.progress-check',
            'title': 'Open',
            'cmd': lambda re: re.environment_open(),
            "tooltip": "Open the Bluesky Environment."
        },
        {
            'icon': 'mdi6.progress-close',
            'title': 'Close',
            'cmd': lambda re: re.environment_close(),
            "tooltip": "Close the Bluesky Environment."
        }
    ],
    "leds": {
        'Connected': {
            'key': 'worker_environment_exists',
            'comp': True,
            'conn': True
        },
        'Environment': {
            'key': 'worker_environment_exists',
            'comp': lambda boolVar: boolVar,
            'control': "env",
            'loading': {
                'key': 'manager_state',
                'comp': lambda stateVar:
                    stateVar=="creating_environment" or stateVar=="closing_environment"
            }
        },
        'Running': {
            'key': 'manager_state',
            'comp': lambda stateVar: stateVar == "executing_queue"
        },
        'Stop Pending': {
            'key': 'queue_stop_pending',
            'comp': lambda boolVar: boolVar
        }
    }
}
