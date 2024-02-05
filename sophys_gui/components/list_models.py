import re
from qtpy.QtCore import Qt, QAbstractTableModel, QModelIndex, Slot
from qtpy.QtGui import QBrush
from sophys_gui.functions import getItemRecursively


class ListModel(QAbstractTableModel):
    SelectedRole = Qt.UserRole + 1
    _roles = {Qt.DisplayRole: b"value", Qt.ToolTipRole: b"tooltip", SelectedRole: b"selected"}

    def typeRender(self, item: dict, type: str):
        """Renders the 'Type' column items."""
        return type[0].upper()

    def nameRender(self, item: dict, name: str):
        """Renders the 'Name' column items."""
        return str(name)

    def argumentsRender(self, item: dict, args: list):
        """Renders the 'Arguments' column items."""
        if len(args) == 0:
            return "None"

        desc = []

        if item["item_type"] == "plan":
            params = self._re_model.run_engine.get_allowed_plan_parameters(name=item["name"])["parameters"]
            for i, arg in enumerate(args):
                desc.append("{} = {}".format(params[i]["name"], arg))
            return " | ".join(desc)
        return str(args)

    def kwRender(self, item: dict, kwargs: dict):
        """Renders the 'Keyword Arguments' column items."""
        if len(kwargs) == 0:
            return "None"

        desc = []

        if item["item_type"] == "plan":
            for key, val in kwargs.items():
                desc.append("{} = {}".format(key, val))
            return "\n".join(desc)
        return str(kwargs)

    def typeTooltipRender(self, item: dict, type: str):
        """Renders the 'Type' column item tooltips."""
        return str(type)

    def nameTooltipRender(self, item: dict, name: str):
        """Renders the 'Name' column item tooltips."""
        if item["item_type"] == "plan":
            info = self._re_model.run_engine.get_allowed_plan_parameters(name=name)
            description = info["description"]

            source = "From user-defined plan list"
            if "module" in info:
                source = "From {}".format(info["module"])

            return "{}\n{}".format(description, source)

    def argumentsTooltipRender(self, item: dict, args: list):
        """Renders the 'Arguments' column item tooltips."""
        if len(args) == 0:
            return

        desc = []

        if item["item_type"] == "plan":
            params = self._re_model.run_engine.get_allowed_plan_parameters(name=item["name"])["parameters"]
            for i in range(len(args)):
                desc.append("{}: {}".format(params[i]["name"], params[i]["description"]))
            return "\n".join(desc)

    def kwTooltipRender(self, item: dict, kwargs: dict):
        """Renders the 'Keyword Arguments' column item tooltips."""
        if len(kwargs) == 0:
            return

        desc = []

        if item["item_type"] == "plan":
            params = self._re_model.run_engine.get_allowed_plan_parameters(name=item["name"])["parameters"]
            for key in kwargs:
                param = next(filter(lambda x: x["name"] == key, params))
                description = re.sub("\n+", ". ", param["description"])

                desc.append("{}: {}".format(key, description))
            return "\n".join(desc)

    # (Column title, Attribute value, Display value, ToolTip value)
    # Display value: (self, item, value) => (display)
    # ToolTip value: (self, item, value) => (toolTip)
    _columns = [
        ("Type", ["item_type"], typeRender, typeTooltipRender),
        ("Name", ["name"], nameRender, nameTooltipRender),
        ("Arguments", ["args"], argumentsRender, argumentsTooltipRender),
        ("Keyword Arguments", ["kwargs"], kwRender, kwTooltipRender),
    ]

    def __init__(self, re_model, plan_changed, plan_items, row_count, parent=None):
        super().__init__(parent)

        self._re_model = re_model
        self.plan_items = plan_items
        self.row_count = row_count
        plan_changed.connect(self.onPlanListChanged)
        self.selected_rows = []

    def getColumns(self):
        return self._columns

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.plan_items)

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._columns)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return
        row = index.row()
        try:
            item = self.plan_items[row]
        except IndexError:
            return

        column_spec = self._columns[index.column()]

        if row in self.selected_rows and role == Qt.BackgroundRole:
            return QBrush(Qt.lightGray)
        if role == Qt.DisplayRole:
            return column_spec[2](self, item, getItemRecursively(item, column_spec[1]))
        if role == Qt.ToolTipRole:
            if column_spec[3] is None:
                return
            return column_spec[3](self, item, getItemRecursively(item, column_spec[1]))
        if role == self.SelectedRole:
            return index.row() in self.selected_rows

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal:
            column_spec = self._columns[section]
            if role == Qt.DisplayRole:
                return str(column_spec[0])
        else:
            if role == Qt.DisplayRole:
                return str(self.row_count(section))

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

    @Slot(int)
    def select(self, row):
        changed_rows = [*self.selected_rows, row]
        self.selected_rows = [row]
        for changed_row in changed_rows:
            self.dataChanged.emit(
                self.index(changed_row, 0),
                self.index(changed_row, self.columnCount() - 1))


class HistoryModel(ListModel):

    def __init__(self, re_model, parent=None):
        history_changed = re_model.run_engine.events.plan_history_changed
        history_items = re_model.run_engine._plan_history_items
        row_count = lambda section: self.rowCount()-section
        super().__init__(re_model, history_changed, history_items, row_count, parent)


class QueueModel(ListModel):
    def __init__(self, re_model, parent=None):
        queue_changed = re_model.run_engine.events.plan_queue_changed
        queue_items = re_model.run_engine._plan_queue_items
        row_count = lambda section: section+1
        super().__init__(re_model, queue_changed, queue_items, row_count, parent)

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
        self._re_model.run_engine.clear()

    @Slot()
    def delete_item(self):
        self.setSelectedItems()
        self._re_model.run_engine.queue_items_remove()
