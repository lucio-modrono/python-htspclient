import sys
from tvh.htsp import HTSPClient
from tvh.api import HTSPApi
#from .scripts import CONFIG
import tvh.log
import binascii

try:
    limit = int(sys.argv[1])
except (IndexError, ValueError):
    limit = 500

try:
    filename = sys.argv[2]
except (IndexError):
    filename = 'channels.txt'

#htsp = HTSPClient((CONFIG['hostname'], 9982))
htsp = HTSPClient(('tvheadend', 9982))
msg = htsp.hello()
#htsp.authenticate(CONFIG['username'], CONFIG['password'])
htsp.authenticate('','')
#log.debug_init(0)
htspapi = HTSPApi(htsp=htsp)

muxes_kwargs = {
    'start': 0,
    'limit': 999999,
    'sort': 'name',
    'dir': 'ASC',
    'filter': [
#        {'type': 'string', 'value': 'scraper-ts', 'field': 'network'},
#        {'type': 'numeric', 'comparison': 'gt', 'value': 1, 'intsplit': 1000000, 'field': 'num_chn'},
        {'type': 'numeric', 'comparison': 'gt', 'value': 2, 'intsplit': 1000000, 'field': 'scan_result'}
    ],
    'all': 1
}

muxes = htspapi.get_muxes_grid(kwargs=muxes_kwargs)
for mux in muxes:
    mux_uuid = binascii.hexlify(mux.get('uuid')).decode('utf-8')
    print ("Delete mux: uuid: %s; network: %s;  name: %s; tags: %s" % (mux_uuid, mux.get('network'), mux.get('iptv_sname'), mux.get('iptv_tags')))
    print ( "%s" % (htspapi.delete_channels([mux_uuid])))

#channels_kwargs = {
#    'start': 0,
#    'limit': 999999,
#    'sort': 'name',
#    'dir': 'ASC',
#    'all': 1
#}

#channels = htspapi.get_channels_grid(kwargs=channels_kwargs)
#for channel in channels:
#    print ("%s;%s" % (channel.get('name'), channel))
#    name_regex = '^%s$' % mux.get('name')
#    icon = mux.get('icon')
#    services = channel.get('services')
#    services = htspapi.get_serviceuuids_from_channeluuid(channel.get('uuid'))
#    multiplex_value = ''
#    for service_uuid in services:
#        print ("%s" % (service_uuid))
#        service = htspapi.get_idnode_value(service_uuid, 'response')
#        print ("%s" % (service))
#        for pdict in service
#            pid = pdict.get('id')
#            if pid == 'multiplex':
#                multiplex_value = pdict.get('value')

#    print ("%s;%s;%s" % (name_regex, icon, multiplex_value))
