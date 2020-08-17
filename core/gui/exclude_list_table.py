# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from .base import DupeGuruGUIObject
from hscommon.gui.table import GUITable, Row
from hscommon.gui.column import Column, Columns
from hscommon.trans import trget
tr = trget("ui")


class ExcludeListTable(GUITable, DupeGuruGUIObject):
    COLUMNS = [
        Column("marked", ""),
        Column("regex", tr("Regular Expressions"))
    ]

    def __init__(self, exclude_list_dialog, app):
        GUITable.__init__(self)
        DupeGuruGUIObject.__init__(self, app)
        self.columns = Columns(self)
        self.dialog = exclude_list_dialog

    def rename_selected(self, newname):
        row = self.selected_row
        if row is None:
            return False
        row._data = None
        return self.dialog.rename_selected(newname)

    # --- Virtual
    def _do_add(self, regex):
        """(Virtual) Creates a new row, adds it in the table.
        Returns ``(row, insert_index)``.
        """
        # Return index 0 to insert at the top
        return ExcludeListRow(self, self.dialog.exclude_list.is_marked(regex), regex), 0

    def _do_delete(self):
        self.dalog.exclude_list.remove(self.selected_row.regex)

    # --- Override
    def add(self, regex):
        row, insert_index = self._do_add(regex)
        self.insert(insert_index, row)
        # self.select([insert_index])
        self.view.refresh()

    def _fill(self):
        for enabled, regex in self.dialog.exclude_list:
            self.append(ExcludeListRow(self, enabled, regex))

    # def remove(self):
    #     super().remove(super().selected_rows)

    # def _update_selection(self):
    #     # rows = self.selected_rows
    #     # self.dialog._select_rows(list(map(attrgetter("_dupe"), rows)))
    #     self.dialog.remove_selected()

    def refresh(self, refresh_view=True):
        """Override to avoid keeping previous selection in case of multiple rows
        selected previously."""
        self.cancel_edits()
        del self[:]
        self._fill()
        # sd = self._sort_descriptor
        # if sd is not None:
        #     super().sort_by(self, column_name=sd.column, desc=sd.desc)
        if refresh_view:
            self.view.refresh()


class ExcludeListRow(Row):
    def __init__(self, table, enabled, regex):
        Row.__init__(self, table)
        self._app = table.app
        self._data = None
        self.enabled_original = enabled
        self.regex_original = regex
        self.enabled = str(enabled)
        self.regex = str(regex)

    @property
    def data(self):
        def get_display_info(row):
            return {"marked": row.enabled, "regex": row.regex}

        if self._data is None:
            self._data = get_display_info(self)
        return self._data

    @property
    def markable(self):
        return self._app.exclude_list.is_markable(self.regex)

    @property
    def marked(self):
        return self._app.exclude_list.is_marked(self.regex)

    @marked.setter
    def marked(self, value):
        if value:
            self._app.exclude_list.mark(self.regex)
        else:
            self._app.exclude_list.unmark(self.regex)

    @property
    def error(self):
        # This assumes error() returns an Exception()
        message = self._app.exclude_list.error(self.regex)
        if hasattr(message, "msg"):
            return self._app.exclude_list.error(self.regex).msg
        else:
            return message  # Exception object
    # @property
    # def regex(self):
    #     return self.regex

    # @regex.setter
    # def regex(self, value):
    #     self._app.exclude_list.add(self._regex, value)
