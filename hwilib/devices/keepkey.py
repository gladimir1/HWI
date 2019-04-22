# KeepKey interaction script

from ..errors import HWWError, UNKNOWN_ERROR
from .trezorlib.transport import enumerate_devices
from .trezor import TrezorClient
from ..base58 import get_xpub_fingerprint_hex

py_enumerate = enumerate # Need to use the enumerate built-in but there's another function already named that

class KeepkeyClient(TrezorClient):
    def __init__(self, path, password=''):
        super(KeepkeyClient, self).__init__(path, password)
        self.type = 'Keepkey'

def enumerate(password=''):
    results = []
    for dev in enumerate_devices():
        d_data = {}

        d_data['type'] = 'keepkey'
        d_data['path'] = dev.get_path()

        client = None
        try:
            client = KeepkeyClient(d_data['path'], password)
            client.client.init_device()
            if not 'keepkey' in client.client.features.vendor:
                continue
            d_data['needs_passphrase_sent'] = client.client.features.passphrase_protection and not client.client.features.passphrase_cached
            if d_data['needs_passphrase_sent'] and not password:
                raise DeviceNotReadyError("Passphrase needs to be specified before the fingerprint information can be retrieved")
            if client.client.features.initialized:
                master_xpub = client.get_pubkey_at_path('m/0h')['xpub']
                d_data['fingerprint'] = get_xpub_fingerprint_hex(master_xpub)
                d_data['needs_passphrase_sent'] = False # Passphrase is always needed for the above to have worked, so it's already sent
            else:
                d_data['error'] = 'Not initialized'
        except HWWError as e:
            d_data['error'] = "Could not open client or get fingerprint information: " + e.get_msg()
            d_data['code'] = e.get_code()
        except Exception as e:
            d_data['error'] = "Could not open client or get fingerprint information: " + str(e)
            d_data['code'] = UNKNOWN_ERROR

        if client:
            client.close()

        results.append(d_data)
    return results
