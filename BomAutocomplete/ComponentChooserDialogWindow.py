import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class CompontentChooserDialog():
    COLUMN_MANUFACTURER = 0
    COLUMN_SELLER = 3

    def __init__(self, componentList):
        builder = Gtk.Builder()
        builder.add_from_file("ComponentChooserDialog.glade")

        self.window = builder.get_object("ComponentChooserDialog")

        self.components_store = Gtk.ListStore(str, str, float, str, str, str)
        for el in componentList:
            self.components_store.append(el)
        self.current_filter_manufacturer = None

        # Creating the filter, feeding it with the liststore model
        self.manufacturer_filter = self.components_store.filter_new()
        # setting the filter function, note that we're not using the
        self.manufacturer_filter.set_visible_func(self.manufacturer_filter_func)

        liststore_sellers = Gtk.ListStore(str)
        # FIXME: hier müssten eigentlich die dinger aus dem result stehen
        sellers = set([el[self.COLUMN_SELLER] for el in componentList])
        for item in sellers:
            liststore_sellers.append([item])

        # creating the treeview, making it use the filter as a model, and adding the columns
        self.treeview = builder.get_object("ComponentsTreeView")
        self.treeview.set_model(Gtk.TreeModelSort(self.manufacturer_filter))

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

            column.set_sort_column_id(0)
            self.treeview.append_column(column)

        self.window.connect("destroy", Gtk.main_quit)
        self.window.show_all()
        Gtk.main()

    def manufacturer_filter_func(self, model, iter, data):
        """Tests if the language in the row is the one in the filter"""
        if (
            self.current_filter_manufacturer is None
            or self.current_filter_manufacturer == "None"
        ):
            return True
        else:
            return model[iter][self.COLUMN_MANUFACTURER] == self.current_filter_manufacturer

    def on_combo_changed(self, widget, path, text):
        self.components_store[path][self.COLUMN_SELLER] = text