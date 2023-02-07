import os, sys
import kicad_netlist_reader
import ComponentChooserDialog
import FileChooserDialog
import re

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


sys.path.append(os.getcwd() + "/../nexar-first-supply-query/python/SupplyQueryDemo")
from nexarClient import NexarClient

QUERY_PARTS = '''
query PartSearch($query: String) {
  supSearch(
    q: $query
    inStockOnly: true
    limit: 20
  ) {
    hits
    results {
      part {
        mpn
        manufacturer {
          name
          id
        }
        medianPrice1000 {
          price
          currency
          quantity
        }
        sellers(authorizedOnly: false) {
          company {
            name
            homepageUrl
          }
          isAuthorized
          offers {
            clickUrl
            inventoryLevel
            moq
            packaging
          }
        }
      }
    }
  }
}
'''


def getDescriptionFromComponent(c):
    PARTNAME_MAP = {'c': "Capacitor", "r": "Resistor"}

    description = PARTNAME_MAP[str.lower(c.getPartName())]
    if c.getValue() != "":
        description += " " + c.getValue()
    if c.getFootprint() != "":
        description += " " + re.search(r"([0-9]{4})", c.getFootprint().split(":")[-1]).group(0)

    description = description.replace("_", " ").replace(":", " ")

    words = description.split(" ")

    #we reverse to remove the duplicates starting from the end
    words.reverse()
    for word in words:
        while words.count(word) > 1:
            words.remove(word)
        if word == "":
            words.remove(word)
    words.reverse()

    description = " ".join(words)

    return description

if __name__ == '__main__':

    clientId = os.environ['NEXAR_CLIENT_ID']
    clientSecret = os.environ['NEXAR_CLIENT_SECRET']
    nexar = NexarClient(clientId, clientSecret)

    fname = ""
    if len(sys.argv) < 2:
        fname = FileChooserDialog.FileChooser()
        if len(fname) == 0:
            print("No file selected")
            exit(1)
    else:
        fname = sys.argv[1]
    net = kicad_netlist_reader.netlist(fname)
    # Get all of the components in groups of matching parts + values
    # (see kicad_netlist_reader.py)
    grouped = net.groupComponents()
    # Output all of the component information
    for group in grouped:
        # Add the reference of every component in the group and keep a reference
        # to the component so that the other data can be filled in once per group
        c = group[0]

        if len(c.getField("Mouser Part Number")):
            continue

        variables = {
            'query': getDescriptionFromComponent(c)
        }
        results = nexar.get_query(QUERY_PARTS, variables)

        if results:
            parts = []
            for it in results.get("supSearch", {}).get("results", {}):
                parts.append([it['part']['manufacturer']['name'], it['part']['mpn'],
                              it['part']['medianPrice1000']['price'] if it['part']['medianPrice1000'] else None,
                              it['part']['sellers'][0]['company']['name'] if it['part']['sellers'] else None,
                              it['part']['sellers'][0]['company']['homepageUrl'] if it['part']['sellers'] else None,
                              it['part']['sellers'][0]['offers'][0]['clickUrl'] if it['part']['sellers'] else None])

            win = ComponentChooserDialog.ComboBoxWindow(parts)
            win.connect("destroy", Gtk.main_quit)
            win.show_all()
            Gtk.main()

        else:
            print('Sorry, no parts found')
            print()

