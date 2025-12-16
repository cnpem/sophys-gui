SOPHYS-GUI
----------

The SOPHYS (Sirius Ophyd and Bluesky utilities) GUI is responsible for controlling and monitoring a Bluesky instance through HTTP Server and a Kafka broker. 

![Screenshot from 2024-11-25 09-27-27](https://github.com/user-attachments/assets/e47dfc2f-f0d7-4edb-95c9-e9a60294c62c)
![image](https://github.com/user-attachments/assets/bb3c5521-b55f-4969-93ef-ebde742b4d76)
![image](https://github.com/user-attachments/assets/e23fcdf6-9ba5-414b-9a57-a919e8f1028f)

Some of its features are:
  * Control of permissions via a login widget, only monitoring is enabled for unauthenticated users.
  * Ordering the items of the Queue 
  * Editting or deleting items of the Queue
  * Duplicating the items of the Queue
  * Addition of a plan to the Queue or immediate execution of it, using a dynamic form that adapts itself using the types provided by the queue server, as shown below.
  * Addition of instructions in the Queue
  * Shortcut for the addition of stop items in the Queue
  * Monitoring the current running item
  * Control of the Queue status, like connection, environment, stop pending and running status.
  * Dynamic buttons for controlling the queue:
    - Starting the queue if in the idle state.
    - Immediate and deffered pausing and stopping if in the running state.
    - Aborting, halting and resuming if in the paused state.
  * Monitoring the exit status, user, plan and parameters present in the History.
  * Live plotting using the Kafka Bluesky Live GUI.
  * Monitoring of the http server communication via a console.
  * Rescaling of the widgets.
  * Tooltips for the plans and parameters.
  * Loading bar for current running plan. If the "total_seq_num" metadata key is set, this will be the total number of events set in the progress ration.

![Screenshot from 2024-11-25 09-28-15](https://github.com/user-attachments/assets/0bc4c227-e8e7-4b3c-830b-6d768e7154ab)
![Screenshot from 2024-11-25 09-28-00](https://github.com/user-attachments/assets/5f537bc6-37ad-4869-a97a-aae751c689b6)

### How to Configure the YAML File

The `.yml` file is structured into multiple dictionaries, each identified by the plan name in snake case, as defined in the main function responsible for executing it.

Each top-level dictionary must contain:
  * `name:` an alternative display name for the plan, if a custom label is required.
  * `param_names:` a mapping between the plan parameters (in snake case) and their modified values.

The `param_names:` key may include nested dictionaries, where each key represents a group name and its value defines a specific set of parameters associated with the main plan.

```yaml
example_plan:
    name: "Example Plan"
    param_names:
            "Plan Arguments":
                "proposal": "Proposal"
                "experiment_tag": "File Name"
                "trajectory_file": "Trajectory File"
                
            "Detectors Config.":
                "use_det1": "Use Detector 1"
                "use_det2": "Use Detector 2"
```

![image](https://raw.githubusercontent.com/Murilo-cnpem/my-repo/main/Captura%20de%20tela%20de%202025-12-16%2011-20-21.png)
![image](https://raw.githubusercontent.com/Murilo-cnpem/my-repo/main/PlanNewNames.png)
![image](https://raw.githubusercontent.com/Murilo-cnpem/my-repo/main/RunningItemName.png)
![image](https://raw.githubusercontent.com/Murilo-cnpem/my-repo/main/HistoryNewName.png)



