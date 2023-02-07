import os, sys
import kicad_netlist_reader


sys.path.append(os.getcwd() + "/../nexar-first-supply-query/python/SupplyQueryDemo")
from nexarClient import NexarClient

QUERY_PARTS = '''
query PartSearch($query: String) {
  supSearch(
    q: $query
    inStockOnly: true
    limit: 4
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

if __name__ == '__main__':

    clientId = os.environ['NEXAR_CLIENT_ID']
    clientSecret = os.environ['NEXAR_CLIENT_SECRET']
    nexar = NexarClient(clientId, clientSecret)

    mpn = input('Search MPN: ')
    if not mpn:
        sys.exit()

    variables = {
        'query': mpn
    }

    kicad_netlist_reader.netlist(sys.argv[1])
    # Get all of the components in groups of matching parts + values
    # (see kicad_netlist_reader.py)
    grouped = net.groupComponents()

    results = nexar.get_query(QUERY_PARTS, variables)

    if results:
        print(str(results))
        for it in results.get("supSearchMpn", {}).get("results", {}):
            print(str(it))
            # print(f'MPN: {it.get("part", {}).get("mpn")}')
            # print(f'Description: {it.get("part", {}).get("shortDescription")}')
            # print(f'Manufacturer: {it.get("part", {}).get("manufacturer", {}).get("name")}')
            # print(f'Lifecycle Status: {getLifecycleStatus(it.get("part", {}).get("specs", {}))}')
            print()
    else:
        print('Sorry, no parts found')
        print()

