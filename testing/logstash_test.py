import json
import logging
import socket

import pytest


logger = logging.getLogger(__name__)

LOG_HOST = 'localhost'
LOG_OUTPUT_SERVER = (LOG_HOST, 17771)
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def send_and_receive(port, protocol, message):
    """Send message to (LOG_HOST, port) via protocol; receive logstash JSON."""
    if not message.endswith('\n'):
        message = f'{message}\n'

    payload = message.encode('utf-8')
    logger.debug('Sending %s', payload)
    dest = (LOG_HOST, port)
    with socket.create_connection(LOG_OUTPUT_SERVER) as output_sock:
        if protocol == 'tcp':
            with socket.create_connection(dest) as log_sock:
                log_sock.send(payload)
        elif protocol == 'udp':
            udp_sock.sendto(payload, dest)
        else:
            raise ValueError('Bad protocol')

        raw = output_sock.recv(8192)
        logger.debug('Received %s', raw)
        return json.loads(raw)


def dotted_getitem(d, key):
    if '.' in key:
        key, remainder = key.split('.', 1)
        return dotted_getitem(d[key], remainder)

    return d[key]


def check_vs_expected(expected, received):
    """Check for some expected keys + values in the received dictionary."""
    errors = []
    for key, expected_value in expected.items():
        try:
            received_value = dotted_getitem(received, key)
        except KeyError:
            errors.append(f'Missing key {key!r}')
        else:
            try:
                assert received_value == expected_value
            except AssertionError as ex:
                # use pytest as a quick hack
                errors.append(f'Bad value for key {key!r}: {ex}')

    if errors:
        raise ValueError('\n'.join(errors))


ports = {
    'errlog': 7004,
}

protocols = {
    'errlog': 'tcp',
}

tests = [
    pytest.param(
        'errlog',
        'IOC=VonHamos01 sevr=major error log! IOC startup',
        {
            'log.iocname': 'VonHamos01',
            'log.severity': 'major',
            'log.message': 'error log! IOC startup',
         },
        id='basic errlog',
    ),

    pytest.param(
        'errlog',
        'IOC=VonHamos01 sevr=major error log! IOC startup',
        {'log.MISSING_KEY': 'VonHamos01'},
        id='missing_key',
        marks=pytest.mark.xfail
    ),

    pytest.param(
        'errlog',
        'IOC=VonHamos01 sevr=major error log! IOC startup',
        {'log.iocname': 'BAD_VALUE'},
        id='bad_value',
        marks=pytest.mark.xfail
    ),
]

@pytest.mark.parametrize('message_type, message, expected', tests)
def test_all(message_type, message, expected):
    result = send_and_receive(ports['errlog'], protocols['errlog'], message)
    check_vs_expected(expected, result)