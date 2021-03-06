import datetime
import sys
import time

from logstash_test import send_by_type, message_types


caputlog_time_format = '%d-%b-%y %H:%M:%S'
caputlog_now = datetime.datetime.now().strftime(caputlog_time_format)
twincat_now = time.time()

test_messages = [
    ('epics_errlog', 'IOC=LogTest sevr=major ** log system test message **'),
    ('caputlog', (f'IOC=LogTest {caputlog_now} ctl-logdev01 klauer '
                 'CAPUTLOGTEST:VALUE new=0 old=1 min=0 max=1')),
    ('plc',
          (f'{{"schema":"twincat-event-0","ts":{twincat_now},"plc":"LogTest",'
            '"severity":4,"id":0,'
            '"event_class":"C0FFEEC0-FFEE-COFF-EECO-FFEEC0FFEEC0",'
            '"msg":"Critical (Log system test.)",'
            '"source":"pcds_logstash.testing.fbLogger/Debug",'
            '"event_type":3,"json":"{}"}'
            ),
    ),
    ('python_json_udp',
     '{"msg": "** log system test**", "pathname": "pcds-logstash/testing/emit_event_now.py", "filename": "emit_event_now.py", "exc_text": null, "lineno": 66, "schema": "python-event-0", "source": "logstash_test.log_and_receive:66", "versions": {"logstash_test": "3.10.1"}, "hostname": "ctl-logdev01", "host_info": {"system": "Linux", "node": "ctl-logdev01", "release": "3.10.0-1127.10.1.el7.x86_64", "version": "#1 SMP Tue May 26 15:05:43 EDT 2020", "machine": "x86_64", "processor": "x86_64"}}',  # noqa
    ),
    ('python_json_udp', 
     r"""{"msg": "Caught an exception", "pathname": "pcds-logstash/testing/emit_event_now.py", "filename": "emit_event_now.py", "exc_text": "Traceback (most recent call last):\n File \"/reg/neh/home5/klauer/Repos/pcds-logstash/testing/logstash_test.py\", line 338, in log_func\n raise Exception('this is a an exception from the test suite')\nException: this is a an exception from the test suite", "lineno": 340, "schema": "python-event-0", "source": "logstash_test.log_func:340", "versions": {"re": "2.2.1"}, "hostname": "ctl-logdev01", "host_info": {"system": "Linux", "node": "ctl-logdev01", "release": "3.10.0-1127.10.1.el7.x86_64", "version": "#1 SMP Tue May 26 15:05:43 EDT 2020", "machine": "x86_64", "processor": "x86_64"}}""",  # noqa
    ),

]

if __name__ == '__main__':
    if sys.argv[1] == 'all':
        types = list(set(type_ for type_, _ in test_messages))
    else:
        types = sys.argv[1:]

    for type_ in types:
        for message_type, message in test_messages:
            if type_ == message_type:
                print(f'Sending message type: {message_type}')
                send_by_type(message_type, message)
