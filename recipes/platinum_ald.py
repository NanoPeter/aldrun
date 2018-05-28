from .recipe import AbstractRecipe, run_and_wait, register, logable
from .recipe import FloatValue, IntegerValue


@register('Platinum ALD')
class OxygenPurification(AbstractRecipe):
    def __init__(self, n:int=500,
                 flow_wait:float=10,
                 flush_wait:float=10,
                 close_wait:float=5,
                 oxygen_wait:float=10,
                 platinum_wait:float=10):
        super().__init__()

        self._number_of_loops = n

        self._flush_center_and_wait = run_and_wait(self._flush_center, total_run_time=flush_wait)
        self._close_center_and_wait = run_and_wait(self._close_center, total_run_time=close_wait)
        self._open_oxygen_and_wait = run_and_wait(self._open_oxygen, total_run_time=oxygen_wait)
        self._stabilize_flow_and_wait = run_and_wait(self._stabilize_flow, total_run_time=flow_wait)
        self._open_platinum_and_wait = run_and_wait(self._open_platinum, total_run_time=platinum_wait)

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

    @staticmethod
    def inputs():
        return {'n': IntegerValue('Number of Loops', default=100),
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
            for command in loop:
                command()
                if self._stop_process.is_set():
                    break
            if self._stop_process.is_set():
                break

        self._close_all()
