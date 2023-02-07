import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class ComboBoxWindow(Gtk.Window):
    COLUMN_MANUFACTURER = 0
    COLUMN_SELLER = 3

    def __init__(self, componentList):
        super().__init__(title="Select component")

        self.set_border_width(10)
        # Setting up the self.grid in which the elements are to be positioned
        self.grid = Gtk.Grid()
        self.grid.set_column_homogeneous(True)
        self.grid.set_row_homogeneous(True)
        self.add(self.grid)

        self.name_store = Gtk.ListStore(str, str, float, str, str, str)
        for el in componentList:
            self.name_store.append(el)
        self.current_filter_manufacturer = None

        # Creating the filter, feeding it with the liststore model
        self.manufacturer_filter = self.name_store.filter_new()
        # setting the filter function, note that we're not using the
        self.manufacturer_filter.set_visible_func(self.manufacturer_filter_func)
        liststore_sellers = Gtk.ListStore(str)
        # FIXME: hier müssten eigentlich die dinger aus dem result stehen
        sellers = set([el[self.COLUMN_SELLER] for el in componentList])
        for item in sellers:
            liststore_sellers.append([item])

        # creating the treeview, making it use the filter as a model, and adding the columns
        self.treeview = Gtk.TreeView(model=self.manufacturer_filter)
        for i, column_title in enumerate(
            ["Manufacturer", "Part Number", "Median Price", "Seller", "Seller URL", "Offer URL"]
        ):
            if i == self.COLUMN_SELLER:
                renderer_combo = Gtk.CellRendererCombo()
                renderer_combo.set_property("editable", True)
                renderer_combo.set_property("model", liststore_sellers)
                renderer_combo.set_property("text-column", 0)
                renderer_combo.set_property("has-entry", False)
                renderer_combo.connect("edited", self.on_combo_changed)

                column = Gtk.TreeViewColumn(column_title, renderer_combo, text=i)
            else:
                renderer = Gtk.CellRendererText()
                column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            self.treeview.append_column(column)

        # creating buttons to filter by manufacturer, and setting up their events
        self.buttons = list()
        for manufacturer in set([el[self.COLUMN_MANUFACTURER] for el in componentList]):
            button = Gtk.Button(label=manufacturer)
            self.buttons.append(button)
            button.connect("clicked", self.on_selection_button_clicked)

        # setting up the layout, putting the treeview in a scrollwindow, and the buttons in a row
        self.scrollable_treelist = Gtk.ScrolledWindow()
        self.scrollable_treelist.set_vexpand(True)
        self.grid.attach(self.scrollable_treelist, 0, 0, 8, 10)
        self.grid.attach_next_to(
            self.buttons[0], self.scrollable_treelist, Gtk.PositionType.BOTTOM, 1, 1
        )
        for i, button in enumerate(self.buttons[1:]):
            self.grid.attach_next_to(
                button, self.buttons[i], Gtk.PositionType.RIGHT, 1, 1
            )
        self.scrollable_treelist.add(self.treeview)

        self.show_all()

    def manufacturer_filter_func(self, model, iter, data):
        """Tests if the language in the row is the one in the filter"""
        if (
            self.current_filter_manufacturer is None
            or self.current_filter_manufacturer == "None"
        ):
            return True
        else:
            return model[iter][self.COLUMN_MANUFACTURER] == self.current_filter_manufacturer

    def on_selection_button_clicked(self, widget):
        """Called on any of the button clicks"""
        # we set the current language filter to the button's label
        self.current_filter_manufacturer = widget.get_label()
        print("%s manufacturer selected!" % self.current_filter_manufacturer)
        # we update the filter, which updates in turn the view
        self.manufacturer_filter.refilter()

    def on_combo_changed(self, widget, path, text):
        self.name_store[path][self.COLUMN_SELLER] = text