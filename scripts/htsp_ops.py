import sys
import binascii
from tvh.htsp import HTSPClient
from tvh.api import HTSPApi
from scripts import CONFIG

try:
    limit = int(sys.argv[1])
except (IndexError, ValueError):
    limit = 500

try:
    filename = sys.argv[2]
except (IndexError):
    filename = 'channels.txt'

htsp = HTSPClient((CONFIG['hostname'], 9982))
msg = htsp.hello()
htsp.authenticate(CONFIG['username'], CONFIG['password'])
htspapi = HTSPApi(htsp=htsp)

muxes_kwargs = {
    'start': 0,
    'limit': 999999,
    'sort': 'name',
    'dir': 'ASC',
    'filter': [
#        {'type': 'string', 'value': 'scraper-ts', 'field': 'network'},
        {'type': 'numeric', 'comparison': 'gt', 'value': 2, 'intsplit': 1000000, 'field': 'scan_result'},
        {'type': 'numeric', 'comparison': 'gt', 'value': 1, 'intsplit': 1000000, 'field': 'num_chn'}
    ],
    'all': 1
}

muxes = htspapi.get_muxes_grid(kwargs=muxes_kwargs)
for mux in muxes:
    mux_uuid = binascii.hexlify(mux.get('uuid')).decode('utf-8')
    print ("Delete mux: uuid: %s; name: %s" % (mux_uuid, mux.get('name')))
    print ( "%s" % (htspapi.delete_channels([mux_uuid])))
