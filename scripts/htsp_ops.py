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

def count_current_suscriptions():
    return len(htspapi.get_active_subscriptions_grid())

def refresh_networks():
    networks_kwargs = {
        'start': 0,
        'limit': 99,
        'sort': 'networkname',
        'dir': 'ASC',
        'filter': [
            {'type': 'string', 'value': 'scrap', 'field': 'networkname'}
        ],
        'all': 1,
        'groupBy': 'false',
        'groupDir': 'ASC'
    }
    for network in htspapi.get_networks_grid(networks_kwargs):
        network_uuid = binascii.hexlify(network.get('uuid')).decode('utf-8')
        print ("Re-fetching network: uuid: %s; network: %s; url: %s" % (network_uuid, network.get('networkname'), network.get('url')))
        print ( "%s" % (htspapi.update_network(network_uuid)))
    return True

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

def main():
    espera_larga = 60  # Segundos si el valor es > 0
    espera_seguridad = 15  # Segundos entre las N comprobaciones
    N = 6  # Número de comprobaciones de seguridad
    necesita_seguridad = False # Esta variable rastrea si venimos de un valor mayor a cero

    while True:
        valor = count_current_suscriptions()

        # CASO 1: Si es mayor a cero, esperamos y volvemos al inicio del bucle
        if valor > 0:
            print(f"Currently serving {valor} stream(s), wait and retry in {espera_larga}s...")
            necesita_seguridad = True  # Activamos la bandera de seguridad
            time.sleep(espera_larga)
            continue  # Salta al inicio del while para volver a rescatar el valor

        # CASO 2: Si es cero, entramos en la fase de seguridad
        # Si llegamos aquí, valor es 0.
        # Comprobamos si hay que aplicar seguridad o seguir de largo
        if necesita_seguridad:
            print(f"Service is idle now, waiting {N} times of {espera_seguridad}s to ensure it...")
            estable = True

            for _ in range(N):
                time.sleep(espera_seguridad)
                if count_current_suscriptions() > 0:
                    print("Serving streams again, wait for idle...")
                    estable = False
                    break # Sale del for, vuelve al while

            if not estable:
                continue # Reevalúa desde el principio del while

        # Si el valor fue 0 desde el inicio o pasó la seguridad
        break

    print("Re-fetching networks...")
    refresh_networks()

    time.sleep(espera_larga*5)

    # Borrar muxes con error
    for mux in get_failed_muxes():
        mux_uuid = binascii.hexlify(mux.get('uuid')).decode('utf-8')
        print ("Delete mux: uuid: %s; network: %s;  name: %s; tags: %s" % (mux_uuid, mux.get('network'), mux.get('iptv_sname'), mux.get('iptv_tags')))
        print ( "%s" % (htspapi.delete_channels([mux_uuid])))

    # Marcar para escaneo los muxes que lleven más de 5 días sin escanear
    for mux in get_old_muxes():
        mux_uuid = binascii.hexlify(mux.get('uuid')).decode('utf-8')
        print ("Reescaning mux: uuid: %s; network: %s;  name: %s; tags: %s" % (mux_uuid, mux.get('network'), mux.get('iptv_sname'), mux.get('iptv_tags')))
        print ( "%s" % (htspapi.update_channels([mux_uuid], data={'scan_state': htspapi.MUX_SCAN_STATUS_PENDING})))

    print("All done, stopping...")
    return True

main()
