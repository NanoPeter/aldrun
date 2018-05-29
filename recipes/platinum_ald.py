from .recipe import AbstractRecipe, run_and_wait, register, logable
from .recipe import FloatValue, IntegerValue

from threading import Event


@register('Platinum ALD')
class PlatinumALD(AbstractRecipe):
    def __init__(self, mqtt_client, signal_interface,
                 n:int=500,
                 flow_wait:float=10,
                 flush_wait:float=10,
                 close_wait:float=5,
                 oxygen_wait:float=10,
                 platinum_wait:float=10):

        super().__init__(mqtt_client, signal_interface)

        mqtt_client.subscribe('ald/recipes/platinum/cmd')
        mqtt_client.message_callback_add('ald/recipes/platinum/cmd', self._cmd)

        self._number_of_loops = n

        wait = self._interrupt_event.wait

        self._flush_center_and_wait = run_and_wait(self._flush_center, total_run_time=flush_wait, sleep_function=wait)
        self._close_center_and_wait = run_and_wait(self._close_center, total_run_time=close_wait, sleep_function=wait)
        self._open_oxygen_and_wait = run_and_wait(self._open_oxygen, total_run_time=oxygen_wait, sleep_function=wait)
        self._stabilize_flow_and_wait = run_and_wait(self._stabilize_flow, total_run_time=flow_wait, sleep_function=wait)
        self._open_platinum_and_wait = run_and_wait(self._open_platinum, total_run_time=platinum_wait, sleep_function=wait)

    def _cmd(self, client, user_data, message):
        if message.payload == b'stop':
            self.stop()

    @logable('stabilizing platinum flow')
    def _stabilize_flow(self):
        pass

    @logable('open platinum')
    def _open_platinum(self):
        pass

    @logable('close platinum')
    def _close_platinum(self):
        pass

    @logable('Flush center')
    def _flush_center(self):
        pass

    @logable('Close center')
    def _close_center(self):
        pass

    @logable('Open oxygen')
    def _open_oxygen(self):
        pass

    @logable('Close oxygen')
    def _close_oxygen(self):
        pass

    @logable('Close all valves')
    def _close_all(self):
        pass

    def max_process_value(self):
        return self._number_of_loops

    @staticmethod
    def inputs():
        return {'n': IntegerValue('Number of Loops', default=500),
                'flow_wait': FloatValue('Stabilize Flow Duration (s)', default=10),
                'flush_wait': FloatValue('Flush Duration (s)', default=10),
                'close_wait': FloatValue('Close Center Duration (s)', default=10),
                'oxygen_wait': FloatValue('Oxygen Open Duration (s)', default=10),
                'platinum_wait': FloatValue('Platinum Open Duration (s)', default=10)}

    def _run(self):
        loop = [self._stabilize_flow_and_wait,
                self._open_platinum_and_wait,
                self._close_platinum,
                self._flush_center_and_wait,
                self._open_oxygen_and_wait,
                self._close_center_and_wait,
                self._close_oxygen]

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
