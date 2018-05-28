from .recipe import AbstractRecipe, run_and_wait, register, logable
from .recipe import FloatValue, IntegerValue

@register('Oxygen Purification')
class OxygenPurification(AbstractRecipe):
    def __init__(self, n:int=100, flush_wait:float=10, close_wait:float=5, oxygen_wait:float=10):
        super().__init__()

        self._number_of_loops = n

        self._flush_center_and_wait = run_and_wait(self._flush_center, total_run_time=flush_wait)
        self._close_center_and_wait = run_and_wait(self._close_center, total_run_time=close_wait)
        self._open_oxygen_and_wait = run_and_wait(self._open_oxygen, total_run_time=oxygen_wait)

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

    @staticmethod
    def inputs():
        return {'n': IntegerValue('Number of Loops', default=100),
                'flush_wait': FloatValue('Flush Wait Time (s)', default=10),
                'close_wait': FloatValue('Close Center Wait Time (s)', default=10),
                'oxygen_wait': FloatValue('Oxygen Open Time (s)', default=10)}

    def _run(self):
        for loop_number in range(self._number_of_loops):
            self._flush_center_and_wait()
            self._close_center_and_wait()
            self._open_oxygen_and_wait()
            self._close_oxygen()

        self._close_all()
