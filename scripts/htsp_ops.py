import sys
from tvh.htsp import HTSPClient
from tvh.api import HTSPApi
from scripts import CONFIG
import tvh.log
import binascii
import time
import json

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

def get_failed_muxes():
    failed_muxes_kwargs = {
        'start': 0,
        'limit': 999999,
        'sort': 'name',
        'dir': 'ASC',
        'filter': [
            {'type': 'numeric', 'comparison': 'gt', 'value': htspapi.MUX_SCAN_RESULT_FAILED, 'intsplit': 1000000, 'field': 'scan_result'}
        ],
        'all': 1
    }
    return htspapi.get_muxes_grid(kwargs=failed_muxes_kwargs)

def get_old_muxes(days=5):
    # Calcular el timestamp dinámico (segundos actuales - segundos en N días)
    seconds_in_day = 86400
    timestamp_limit = int(time.time()) - (days * seconds_in_day)

    old_muxes_kwargs = {
        'start': 0,
        'limit': 999999,
        'sort': 'name',
        'dir': 'ASC',
        'filter': [
            {'type': 'numeric', 'comparison': 'eq', 'value': htspapi.MUX_SCAN_RESULT_OK, 'field': 'scan_result'},
            {'type': 'numeric', 'comparison': 'lt', 'value': timestamp_limit, 'field': 'scan_last'}
        ],
        'all': 1
    }
    print(f"Filtro de búsqueda para muxes antiguos: {json.dumps(old_muxes_kwargs)}")
    return htspapi.get_muxes_grid(kwargs=old_muxes_kwargs)

# Borrar muxes con error
for mux in get_failed_muxes():
    mux_uuid = binascii.hexlify(mux.get('uuid')).decode('utf-8')
    print ("Delete mux: uuid: %s; network: %s;  name: %s; tags: %s" % (mux_uuid, mux.get('network'), mux.get('iptv_sname'), mux.get('iptv_tags')))
    print ( "%s" % (htspapi.delete_channels([mux_uuid])))

# Marcar para escaneo los muxes que lleven más de 5 días sin escanear
#muxes = get_old_muxes()
#old_mux_uuids = [m.get('uuid') for m in muxes]
#htspapi.update_channels(old_mux_uuids, data={'scan_state': htspapi.MUX_SCAN_STATUS_PENDING})
#print(f"Orden de reescaneo enviada para {len(muxes)} muxes.")
for mux in get_old_muxes():
    mux_uuid = binascii.hexlify(mux.get('uuid')).decode('utf-8')
    print ("Reescaning mux: uuid: %s; network: %s;  name: %s; tags: %s" % (mux_uuid, mux.get('network'), mux.get('iptv_sname'), mux.get('iptv_tags')))
    print ( "%s" % (htspapi.update_channels([mux_uuid], data={'scan_state': htspapi.MUX_SCAN_STATUS_PENDING})))
