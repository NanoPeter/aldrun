from .recipe import AbstractRecipe, run_and_wait, register, logable
from .recipe import FloatValue, IntegerValue

import json

@register('Oxygen On Off')
class OxygenOnOff(AbstractRecipe):
    def __init__(self, mqtt_client, signal_interface,
                 n:int=100,
                 close_wait:float=5,
                 oxygen_wait:float=10,
                 flow:float=10):

        super().__init__(mqtt_client, signal_interface)

        mqtt_client.subscribe('ald/recipes/oxygen_purification/cmd')
        mqtt_client.message_callback_add('ald/recipes/oxygen_purification/cmd', self._cmd)

        self._number_of_loops = n
        self._flow = flow

        wait = self._interrupt_event.wait

        self._close_center_and_wait = run_and_wait(self._close_center, total_run_time=close_wait, sleep_function=wait)
        self._open_oxygen_and_wait = run_and_wait(self._open_oxygen, total_run_time=oxygen_wait, sleep_function=wait)

    def _cmd(self, client, user_data, message):
        if message.payload == b'stop':
            self.stop()


    @logable('Close center')
    def _close_center(self):
        valves_to_change = {"centeroxygen": False}
        self._mqtt_client.publish('ald/io/set', json.dumps(valves_to_change))
        self._mqtt_client.publish('ald/flow/set', '0.0')

    @logable('Open oxygen')
    def _open_oxygen(self):
        valves_to_change = {"centeroxygen": True}
        self._mqtt_client.publish('ald/io/set', json.dumps(valves_to_change))
        self._mqtt_client.publish('ald/flow/set', str(self._flow))

    @logable('Close all valves')
    def _close_all(self):
        self._mqtt_client.publish('ald/io/closeall', ' ')

    def max_process_value(self):
        return self._number_of_loops

    @staticmethod
    def inputs():
        return {'n': IntegerValue('Number of Loops', default=100),
                'close_wait': FloatValue('Close Center Wait Time (s)', default=10),
                'oxygen_wait': FloatValue('Oxygen Open Time (s)', default=10),
                'flow': FloatValue('flow (a.u.)', default=10)}

    def _run(self):
        loop = [ self._close_center_and_wait,
                 self._open_oxygen_and_wait]

        for loop_number in range(self._number_of_loops):
            self._log('starting CYCLE {}'.format(loop_number + 1))
            for command in loop:
                command()
                if self._stop_process.is_set():
                    break
            if self._stop_process.is_set():
                break

        self._close_all()
