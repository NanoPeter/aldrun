from .recipe import AbstractRecipe, run_and_wait, register, logable
from .recipe import FloatValue, IntegerValue

from threading import Event

import json

@register('Platinum ALD')
class PlatinumALD(AbstractRecipe):
    def __init__(self, mqtt_client, signal_interface,
                 n:int=500,
                 flow_wait:float=10,
                 flush_wait:float=10,
                 close_wait:float=5,
                 oxygen_wait:float=10,
                 platinum_wait:float=10,
                 platinum_flush_wait:float=10,
                 oxygen_flow:float=100):

        super().__init__(mqtt_client, signal_interface)

        mqtt_client.subscribe('ald/recipes/platinum/cmd')
        mqtt_client.message_callback_add('ald/recipes/platinum/cmd', self._cmd)

        self._number_of_loops = n
        self._flow = oxygen_flow

        wait = self._interrupt_event.wait

        self._flush_center_and_wait = run_and_wait(self._flush_center, total_run_time=flush_wait, sleep_function=wait)
        self._close_center_and_wait = run_and_wait(self._close_center, total_run_time=close_wait, sleep_function=wait)
        self._open_oxygen_and_wait = run_and_wait(self._open_oxygen, total_run_time=oxygen_wait, sleep_function=wait)
        self._stabilize_flow_and_wait = run_and_wait(self._stabilize_flow, total_run_time=flow_wait, sleep_function=wait)
        self._open_platinum_and_wait = run_and_wait(self._open_platinum, total_run_time=platinum_wait, sleep_function=wait)
        self._flush_platinum_and_wait = run_and_wait(self._flush_platinum, total_run_time=platinum_flush_wait, sleep_function=wait)

    def _cmd(self, client, user_data, message):
        if message.payload == b'stop':
            self.stop()

    """
    "rightpurge"
    "rightprecursorcarrier"
    "rightprecursorpurge"
    
    "centeroxygen"
    "centerpurge"
    
    "leftpurge"
    "leftprecursorcarrier"
    "leftprecursorpurge"
    """


    @logable('stabilizing platinum flow')
    def _stabilize_flow(self):
        valves_to_change = {"leftpurge": True, 
                            "leftprecursorcarrier": False,
                            "leftprecursorpurge": False,
                            "centerpurge": False,
                            "centeroxygen": False,
                            "rightpurge": False}
        self._mqtt_client.publish('ald/io/set', json.dumps(valves_to_change))
        self._mqtt_client.publish('ald/flow/set', '0.0')

    @logable('open platinum')
    def _open_platinum(self):
        valves_to_change = {"leftpurge": False, 
                            "leftprecursorcarrier": True,
                            "leftprecursorpurge": True,
                            "centerpurge": False,
                            "centeroxygen": False,
                            "rightpurge": False}
        self._mqtt_client.publish('ald/io/set', json.dumps(valves_to_change))
        self._mqtt_client.publish('ald/flow/set', '0.0')

    @logable('close platinum')
    def _close_platinum(self):
        valves_to_change = {"leftpurge": False, 
                            "leftprecursorcarrier": False,
                            "leftprecursorpurge": False,
                            "centerpurge": False,
                            "centeroxygen": False,
                            "rightpurge": False}
        self._mqtt_client.publish('ald/io/set', json.dumps(valves_to_change))
        self._mqtt_client.publish('ald/flow/set', '0.0')

    @logable('flush platinum')
    def _flush_platinum(self):
        valves_to_change = {"leftpurge": True, 
                            "leftprecursorcarrier": False,
                            "leftprecursorpurge": False,
                            "centerpurge": False,
                            "centeroxygen": False,
                            "rightpurge": False}
        self._mqtt_client.publish('ald/io/set', json.dumps(valves_to_change))
        self._mqtt_client.publish('ald/flow/set', '0.0')

    @logable('Flush center')
    def _flush_center(self):
        valves_to_change = {"leftpurge": False, 
                            "leftprecursorcarrier": False,
                            "leftprecursorpurge": False,
                            "centerpurge": True,
                            "centeroxygen": False,
                            "rightpurge": True}
        self._mqtt_client.publish('ald/io/set', json.dumps(valves_to_change))
        self._mqtt_client.publish('ald/flow/set', '0.0')

    @logable('Close center')
    def _close_center(self):
        valves_to_change = {"leftpurge": False, 
                            "leftprecursorcarrier": False,
                            "leftprecursorpurge": False,
                            "centerpurge": False,
                            "centeroxygen": False,
                            "rightpurge": False}
        self._mqtt_client.publish('ald/io/set', json.dumps(valves_to_change))
        self._mqtt_client.publish('ald/flow/set', '0.0')

    @logable('Open oxygen')
    def _open_oxygen(self):
        valves_to_change = {"leftpurge": False, 
                            "leftprecursorcarrier": False,
                            "leftprecursorpurge": False,
                            "centerpurge": False,
                            "centeroxygen": True,
                            "rightpurge": False}
        self._mqtt_client.publish('ald/io/set', json.dumps(valves_to_change))
        self._mqtt_client.publish('ald/flow/set', str(self._flow))

    @logable('Close oxygen')
    def _close_oxygen(self):
        valves_to_change = {"leftpurge": False, 
                            "leftprecursorcarrier": False,
                            "leftprecursorpurge": False,
                            "centerpurge": False,
                            "centeroxygen": False,
                            "rightpurge": False}
        self._mqtt_client.publish('ald/io/set', json.dumps(valves_to_change))
        #wait a bit to 'fill' tube
        self._interrupt_event.wait(0.2)
        self._mqtt_client.publish('ald/flow/set', '0.0')

    @logable('Close all valves')
    def _close_all(self):
        valves_to_change = {"leftpurge": False, 
                            "leftprecursorcarrier": False,
                            "leftprecursorpurge": False,
                            "centerpurge": False,
                            "centeroxygen": False,
                            "rightpurge": False}
        self._mqtt_client.publish('ald/io/set', json.dumps(valves_to_change))
        self._mqtt_client.publish('ald/flow/set', '0.0')

    def max_process_value(self):
        return self._number_of_loops

    @staticmethod
    def inputs():
        return {'n': IntegerValue('Number of Loops', default=500),
                'flow_wait': FloatValue('Stabilize Flow Duration (s)', default=2.5),
                'flush_wait': FloatValue('Flush Center Duration (s)', default=2.5),
                'close_wait': FloatValue('Close Center Duration (s)', default=2.5),
                'oxygen_wait': FloatValue('Oxygen Open Duration (s)', default=10),
                'platinum_wait': FloatValue('Platinum Open Duration (s)', default=5),
                'oxygen_flow': FloatValue('Oxygenflow (sccm)', default=80),
                'platinum_flush_wait': FloatValue('Platinum Flush Duration (s)', default=2.5)}

    def _run(self):
        loop = [self._stabilize_flow_and_wait,
                self._open_platinum_and_wait,
                self._close_platinum,
                self._flush_platinum_and_wait,
                self._flush_center_and_wait,
                self._open_oxygen_and_wait,
                self._close_oxygen,
                self._flush_center_and_wait,
                self._close_center_and_wait,
                self._flush_center_and_wait,
                self._close_center
                ]

        for loop_number in range(self._number_of_loops):
            self._signal_interface.emit_update_process_value(loop_number)
            self._log('starting CYCLE {}'.format(loop_number + 1))
            for command in loop:
                command()
                if self._stop_process.is_set():
                    break
            if self._stop_process.is_set():
                break

        self._signal_interface.emit_update_process_value(self._number_of_loops)
        self._close_all()
