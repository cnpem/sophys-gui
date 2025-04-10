import copy
import re
from datetime import datetime
from qtpy.QtCore import Qt, QAbstractTableModel, QModelIndex, Slot, \
    Signal
from qtpy.QtGui import QBrush, QColor
from qtpy.QtWidgets import QMainWindow, QLabel, QScrollArea, QApplication, QWidget, \
    QVBoxLayout, QHBoxLayout
from sophys_gui.functions import getItemRecursively, addArgsToKwargs, addLineJumps
from .form import SophysForm

class ListModel(QAbstractTableModel):
    SelectedRole = Qt.UserRole + 1
    _roles = {Qt.DisplayRole: b"value", Qt.ToolTipRole: b"tooltip", SelectedRole: b"selected"}
    updateTable = Signal([int])

    def statusRender(self, item: dict, status: str):
        """Renders the 'Status' column items."""
        return str(status)

    def typeRender(self, item: dict, type: str):
        """Renders the 'Type' column items."""
        return type[0].upper()

    def nameRender(self, item: dict, name: str):
        """Renders the 'Name' column items."""
        return str(name)

    def userRender(self, item: dict, user: str):
        """Renders the 'User' column items."""
        return str(user[0])

    def argumentsRender(self, item: dict, argsList: dict):
        """Renders the 'Arguments' column items."""
        hasArgs = len(argsList[0]) != 0
        hasKwargs = len(argsList[1]) != 0
        if not (hasArgs or hasKwargs):
            return "None"
        desc = []
        if not hasKwargs or argsList[1] == '':
            argsList[1] = {}
        if hasArgs:
            addArgsToKwargs(argsList)
        if item["item_type"] == "plan":
            for key, val in argsList[1].items():
                desc.append("{} = {}".format(key, val))
            return "\n".join(desc)
        return str(desc)

    def uidRender(self, item: dict, uid: str):
        return ''

    def statusTooltipRender(self, item: dict, status: str):
        """Renders the 'Status' column item tooltips."""
        return addLineJumps("Exit status received after the item execution.")

    def editTooltipRender(self, item: dict, item_type: str):
        return addLineJumps("Copy the selected item data into a form that will update " \
            f"the {item_type} in this row.")

    def deleteTooltipRender(self, item: dict, item_type: str):
        return addLineJumps(f"Deletes the {item_type} in this row.")

    def typeTooltipRender(self, item: dict, type: str):
        """Renders the 'Type' column item tooltips."""
        return str(type)

    def nameTooltipRender(self, item: dict, name: str):
        """Renders the 'Name' column item tooltips."""
        if item["item_type"] == "plan":
            info = self._re_model.run_engine.get_allowed_plan_parameters(name=name)
            if "description" in info:
                description = info["description"]

                source = "From user-defined plan list"
                if "module" in info:
                    source = "From {}".format(info["module"])

                return "{}\n{}".format(description, source)
            return ""

    def userTooltipRender(self, item: dict, user: str):
        """Renders the 'User' column item tooltips."""
        return addLineJumps(f"Last user that modified the {user[1]} in this row.")

    def argumentsTooltipRender(self, item: dict, argsList: dict):
        """Renders the 'Arguments' column item tooltips."""
        hasArgs = len(argsList[0]) != 0
        hasKwargs = len(argsList[1]) != 0
        if not (hasArgs or hasKwargs):
            return "None"
        desc = []
        if hasArgs:
            addArgsToKwargs(argsList)
        if item["item_type"] == "plan":
            params = self._re_model.run_engine.get_allowed_plan_parameters(name=item["name"])["parameters"]
            for key in argsList[1]:
                matches = list(filter(lambda x: x["name"] == key, params))
                if len(matches) == 0:
                    continue

                param = matches[0]

                if "description" in param:
                    description = param["description"]
                    try:
                        extraIdx = description.index("-.-")
                        description = description[:extraIdx]
                    except Exception:
                        pass
                    description = re.sub("\n+", ". ", description)
                    tooltipRow = "{}: {}".format(key, description)
                else:
                    tooltipRow = ""
                desc.append(addLineJumps(tooltipRow))
            return "\n".join(desc)

    # (Column title, Attribute value, Display value, ToolTip value)
    # Display value: (self, item, value) => (display)
    # ToolTip value: (self, item, value) => (toolTip)
    columns = [
        ("Type", ["item_type"], typeRender, typeTooltipRender),
        ("Name", ["name"], nameRender, nameTooltipRender),
        ("User", [["user", "item_type"]], userRender, userTooltipRender),
        ("Arguments", [["args", "kwargs"]], argumentsRender, argumentsTooltipRender)
    ]

    columns_history = [
        ("Status", ["result", "exit_status"], statusRender, statusTooltipRender)
    ] + columns

    columns_queue = columns + [
        ("  Edit  ", ["item_type"], uidRender, editTooltipRender),
        (" Delete ", ["item_type"], uidRender, deleteTooltipRender)
    ]

    def __init__(self, re_model, plan_changed, plan_items, row_count, listId, parent=None):
        super().__init__(parent)

        self._re_model = re_model
        self.plan_items = plan_items
        self.row_count = row_count
        plan_changed.connect(self.onPlanListChanged)
        self.selected_rows = []
        isHistory = listId == "History"
        if isHistory:
            self.columns = self.columns_history
        else:
            self.columns = self.columns_queue

    def getColumns(self):
        return self.columns

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.plan_items)

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.columns)

    def getBackgroundColor(self, row):
        if row in self.selected_rows:
            return "gray"
        if row%2 == 0:
            return "#dfdfdf"
        return "#f7f7f7"

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return
        row = self.row_count(index.row()) - 1
        try:
            item = copy.deepcopy(self.plan_items[row])
        except IndexError:
            return

        column_spec = self.columns[index.column()]
        if role == Qt.BackgroundRole:
            return QBrush(QColor(self.getBackgroundColor(row)))
        if role == Qt.DisplayRole:
            return column_spec[2](self, item, getItemRecursively(item, column_spec[1]))
        if role == Qt.ToolTipRole:
            if column_spec[3] is None:
                return
            return column_spec[3](self, item, getItemRecursively(item, column_spec[1]))
        if role == self.SelectedRole:
            return index.row() in self.selected_rows

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                column_spec = self.columns[section]
                return str(column_spec[0])
            else:
                return self.row_count(section)

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def roleNames(self):
        return self._roles

    def getSelectedRows(self):
        return self.selected_rows

    @Slot(object)
    def onPlanListChanged(self, _):
        self.beginResetModel()
        self.endResetModel()
        self.updateTable.emit(self.rowCount())


class HistoryModel(ListModel):

    def __init__(self, re_model, parent=None):
        history_changed = re_model.run_engine.events.plan_history_changed
        history_items = re_model.run_engine._plan_history_items
        row_count = lambda section: self.rowCount()-section
        super().__init__(re_model, history_changed, history_items, row_count, "History", parent)

    @Slot(int)
    def select(self, row):
        changed_rows = [*self.selected_rows, row]
        self.selected_rows = [self.rowCount() - row - 1]
        for changed_row in changed_rows:
            self.dataChanged.emit(
                self.index(changed_row, 0),
                self.index(changed_row, self.columnCount() - 1))

    def setSelectedItems(self):
        self._re_model.run_engine.selected_history_item_pos = self.selected_rows

    @Slot()
    def clear_all(self):
        self._re_model.run_engine.history_clear()

    @Slot()
    def copy_to_queue(self):
        self.setSelectedItems()
        self._re_model.run_engine.history_item_add_to_queue()

    def create_traceback_widget(self, result):
        widget = QWidget()
        vlay = QVBoxLayout(widget)
        for scan_times in ["time_start", "time_stop"]:
            hlay = QHBoxLayout()
            title = QLabel(f"<strong>{scan_times[5:].capitalize()}</strong>")
            hlay.addWidget(title)

            utc_s = result[scan_times] - 3 * 60**2
            date = datetime.utcfromtimestamp(utc_s)
            lbl = QLabel(date.strftime("%X %x"))
            hlay.addWidget(lbl)
            vlay.addLayout(hlay)

        title = QLabel("<strong>Traceback</strong>", alignment=Qt.AlignCenter)
        vlay.addWidget(title)

        scroll = QScrollArea()
        log = QLabel(result["traceback"])
        scroll.setWidget(log)
        scroll.setWidgetResizable(True)
        vlay.addWidget(scroll)

        return widget

    @Slot()
    def error_log(self):
        selected_row = self.getSelectedRows()
        if len(selected_row) > 0:
            selected_item = self._re_model.run_engine._plan_history_items[selected_row[0]]
            if selected_item["result"]["exit_status"] == "failed":
                self.window = QMainWindow()
                self.window.setCentralWidget(
                    self.create_traceback_widget(selected_item["result"]))
                self.window.show()
            else:
                app = QApplication.instance()
                app.popup[0].set_text("No error log!")
                app.popup[0].show_popup()


class QueueModel(ListModel):

    def __init__(self, re_model, parent=None):
        queue_changed = re_model.run_engine.events.plan_queue_changed
        queue_items = re_model.run_engine._plan_queue_items
        row_count = lambda section: section + 1
        self.global_metadata = ""
        super().__init__(re_model, queue_changed, queue_items, row_count, "Queue", parent)

    @Slot(int)
    def select(self, row):
        changed_rows = [*self.selected_rows, row]
        self.selected_rows = [row]
        for changed_row in changed_rows:
            self.dataChanged.emit(
                self.index(changed_row, 0),
                self.index(changed_row, self.columnCount() - 1))

    def setSelectedItems(self):
        self._re_model.run_engine.selected_queue_item_uids = [
            self._re_model.run_engine.queue_item_pos_to_uid(i) for i in self.selected_rows]

    @Slot()
    def move_up(self):
        self.setSelectedItems()
        self._re_model.run_engine.queue_items_move_up()
        self.selected_rows = [i - 1 for i in self.selected_rows]
        for changed_row in self.selected_rows:
            self.dataChanged.emit(
                self.index(changed_row, 0),
                self.index(changed_row + 1, self.columnCount() - 1))

    @Slot()
    def move_down(self):
        self.setSelectedItems()
        self._re_model.run_engine.queue_items_move_down()
        self.selected_rows = [i + 1 for i in self.selected_rows]
        for changed_row in self.selected_rows:
            self.dataChanged.emit(
                self.index(changed_row - 1, 0),
                self.index(changed_row, self.columnCount() - 1))

    @Slot()
    def move_top(self):
        self.setSelectedItems()
        self._re_model.run_engine.queue_items_move_to_top()
        __last_modified_row = max(self.selected_rows)
        self.selected_rows = [i for i in range(len(self.selected_rows))]
        self.dataChanged.emit(
            self.index(0, 0),
            self.index(__last_modified_row, self.columnCount() - 1))

    @Slot()
    def move_bottom(self):
        self.setSelectedItems()
        self._re_model.run_engine.queue_items_move_to_bottom()
        __last_modified_row = min(self.selected_rows)
        self.selected_rows = [self.rowCount() - i - 1 for i in range(len(self.selected_rows))]
        self.dataChanged.emit(
            self.index(__last_modified_row, 0),
            self.index(self.rowCount() - 1, self.columnCount() - 1))

    @Slot()
    def clear_all(self):
        self._re_model.run_engine.queue_clear()

    @Slot()
    def delete_item(self):
        self.setSelectedItems()
        self._re_model.run_engine.queue_items_remove()

    @Slot()
    def duplicate_item(self):
        self.setSelectedItems()
        self._re_model.run_engine.queue_item_copy_to_queue()

    def get_item_type(self):
        re = self._re_model.run_engine
        sel_item = re._selected_queue_item_uids
        pos = re.queue_item_uid_to_pos(sel_item[0])
        return re._plan_queue_items[pos]['item_type']

    def get_name_param_variables(self, item_type):
        re = self._re_model.run_engine
        if item_type == 'plan':
            allowed_parameters = re.get_allowed_plan_parameters
            allowed_names = re.get_allowed_plan_names
        else:
            allowed_parameters = re.get_allowed_instruction_parameters
            allowed_names = re.get_allowed_instruction_names
        return allowed_parameters, allowed_names

    def has_open_environment(self):
        status = self._re_model.run_engine.re_manager_status
        return status.get("worker_environment_exists", None)

    def global_metadata_updater(self, new_value = None):
        if new_value != None:
            self.global_metadata = new_value
        return self.global_metadata

    @Slot()
    def add_plan_item(self):
        allowed_parameters, allowed_names = self.get_name_param_variables("plan")
        SophysForm(self._re_model.run_engine, "add_plan",
            allowed_parameters, allowed_names, hasEnv=self.has_open_environment(), metadata_file_path=self.global_metadata_updater).exec()

    @Slot()
    def add_instruction_item(self):
        allowed_parameters, allowed_names = self.get_name_param_variables("instruction")
        SophysForm(self._re_model.run_engine, "add_instruction",
            allowed_parameters, allowed_names, hasEnv=self.has_open_environment()).exec()

    @Slot()
    def add_stop_queue(self):
        allowed_parameters, allowed_names = self.get_name_param_variables('instruction')
        form = SophysForm(self._re_model.run_engine, "add_instruction", allowed_parameters, allowed_names)
        form.addItemToQueue()

    @Slot()
    def copy_queue_item(self):
        self.setSelectedItems()
        item_type = self.get_item_type()
        allowed_parameters, allowed_names = self.get_name_param_variables(item_type)
        SophysForm(self._re_model.run_engine, "copy",
            allowed_parameters, allowed_names).exec()

    @Slot()
    def edit_queue_item(self):
        self.setSelectedItems()
        item_type = self.get_item_type()
        allowed_parameters, allowed_names = self.get_name_param_variables(item_type)
        SophysForm(self._re_model.run_engine, "edit_"+item_type,
            allowed_parameters, allowed_names).exec()
