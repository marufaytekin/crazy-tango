import time
import logging
from random import shuffle

log = logging.getLogger(__name__)


class TaskStatus(object):
    """ A class for enumerating task statuses """
    FAILURE = 0
    SUCCESS = 1
    RUNNING = 2


class Task(object):
    """ The base Task class """

    def __init__(self, name, children=None, reset_after=False, announce=False, *args, **kwargs):
        self.name = name
        self.status = None
        self.reset_after = reset_after
        self._announce = announce

        if children is None:
            children = []

        self.children = children

    def __str__(self):
        return self.name

    def run(self):
        pass

    def reset(self):
        for c in self.children:
            c.reset()

        self.status = None

    def add_child(self, c):
        self.children.append(c)

    def remove_child(self, c):
        self.children.remove(c)

    def prepend_child(self, c):
        self.children.insert(0, c)

    def insert_child(self, c, i):
        self.children.insert(i, c)

    def get_status(self):
        return self.status

    def set_status(self, s):
        self.status = s

    def announce(self):
        log.info("Executing " + str(self.__class__.__name__ + " " + self.name))

    def get_type(self):
        return type(self)

    # These next two functions allow us to use the 'with' syntax
    def __enter__(self):
        return self.name

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            return False
        return True


class Iterator(Task):
    """
        Iterate through all child tasks ignoring failure.
    """

    def __init__(self, name, *args, **kwargs):
        super(Iterator, self).__init__(name, *args, **kwargs)

    def run(self):
        for c in self.children:
            c.status = c.run()
            if c.status == TaskStatus.RUNNING:
                return c.status
        if self.reset_after:
            self.reset()
        return TaskStatus.SUCCESS


class Invert(Task):
    """
        Turn SUCCESS into FAILURE and vice-versa
    """

    def __init__(self, name, *args, **kwargs):
        super(Invert, self).__init__(name, *args, **kwargs)

    def run(self):
        for c in self.children:
            c.status = c.run()
            if c.status == TaskStatus.FAILURE:
                return TaskStatus.SUCCESS
            elif c.status == TaskStatus.SUCCESS:
                return TaskStatus.FAILURE
            else:
                return c.status


class Sequence(Task):
    """
        A sequence runs each task in order until one fails,
        at which point it returns FAILURE. If all tasks succeed, a SUCCESS
        status is returned.  If a subtask is still RUNNING, then a RUNNING
        status is returned and processing continues until either SUCCESS
        or FAILURE is returned from the subtask.
    """

    def __init__(self, name, *args, **kwargs):
        super(Sequence, self).__init__(name, *args, **kwargs)

    def next_move(self):
        if len(self.children) > 0:
            c = self.children.pop(0)
            if isinstance(c, Task):
                return c
            elif isinstance(c, Sequence):
                return c.next_move()
        else:
            return None

    def run(self):
        if self._announce:
            self.announce()
        for c in self.children:
            c.status = c.run()
            if c.status != TaskStatus.SUCCESS:
                if c.status == TaskStatus.FAILURE:
                    if self.reset_after:
                        self.reset()
                        return TaskStatus.FAILURE
                return c.status

        if self.reset_after:
            self.reset()

        return TaskStatus.SUCCESS


class Selector(Task):
    """ A selector runs each task in order until one succeeds,
        at which point it returns SUCCESS. If all tasks fail, a FAILURE
        status is returned.  If a subtask is still RUNNING, then a RUNNING
        status is returned and processing continues until either SUCCESS
        or FAILURE is returned from the subtask.
    """

    def __init__(self, name, *args, **kwargs):
        super(Selector, self).__init__(name, *args, **kwargs)

    def run(self):
        if self._announce:
            self.announce()
        for c in self.children:
            c.status = c.run()
            if c.status != TaskStatus.FAILURE:
                if c.status == TaskStatus.SUCCESS:
                    if self.reset_after:
                        self.reset()
                        return TaskStatus.SUCCESS
                    else:
                        return c.status
                return c.status
        if self.reset_after:
            self.reset()
        return TaskStatus.FAILURE


class RandomSelector(Task):
    """ A selector runs each task in order until one succeeds,
        at which point it returns SUCCESS. If all tasks fail, a FAILURE
        status is returned.  If a subtask is still RUNNING, then a RUNNING
        status is returned and processing continues until either SUCCESS
        or FAILURE is returned from the subtask.
    """

    def __init__(self, name, *args, **kwargs):
        super(RandomSelector, self).__init__(name, *args, **kwargs)
        self.shuffled = False

    def run(self):
        if self._announce:
            self.announce()
        if not self.shuffled:
            shuffle(self.children)
            self.shuffled = True
        for c in self.children:
            c.status = c.run()
            if c.status != TaskStatus.FAILURE:
                if c.status == TaskStatus.SUCCESS:
                    if self.reset_after:
                        self.reset()
                        return TaskStatus.SUCCESS
                    else:
                        return c.status
                return c.status
        if self.reset_after:
            self.reset()
        return TaskStatus.FAILURE


class Loop(Task):
    """
        Loop over one or more subtasks for the given number of iterations
        Use the value -1 to indicate a continual loop.
    """

    def __init__(self, name, announce=True, *args, **kwargs):
        super(Loop, self).__init__(name, *args, **kwargs)

        self.iterations = kwargs['iterations']
        self._announce = announce
        self.loop_count = 0
        self.name = name
        log.info("Loop iterations: " + str(self.iterations))

    def run(self):
        c = self.children[0]
        while self.iterations == -1 or self.loop_count < self.iterations:
            c.status = c.run()
            status = c.status
            self.status = status
            if status == TaskStatus.SUCCESS or status == TaskStatus.FAILURE:
                self.loop_count += 1
                if self._announce:
                    log.info(self.name + " COMPLETED " + str(self.loop_count) + " LOOP(S)")
                c.reset()
            return status


class Wait(Task):
    """
        This is a *blocking* wait task.  The interval argument is in seconds.
    """

    def __init__(self, name, interval, *args, **kwargs):
        super(Wait, self).__init__(name, *args, **kwargs)
        self._interval = interval

    def run(self):
        if self._announce:
            self.announce()
        time.sleep(self._interval)

        return TaskStatus.SUCCESS


class Limit(Task):
    """
        Limit the number of times a task can execute
    """

    def __init__(self, name, announce=True, *args, **kwargs):
        super(Limit, self).__init__(name, *args, **kwargs)

        self.max_executions = kwargs['max_executions']
        self._announce = announce
        self.execution_count = 0
        self.name = name
        log.info("Limit number of executions to: " + str(self.max_executions))

    def run(self):
        c = self.children[0]
        if self.execution_count >= self.max_executions:
            if self._announce:
                log.info(self.name + " reached maximum number (" + str(self.max_executions) + ") of executions.")
            if self.reset_after:
                self.reset()
            return TaskStatus.FAILURE
        c.status = c.run()
        if c.status != TaskStatus.RUNNING:
            self.execution_count += 1
        return c.status

    def reset(self):
        c = self.children[0]
        c.reset()
        self.execution_count = 0
        self.status = None


class ParallelOne(Task):
    """
    A parallel task runs each child task  at (roughly) the same time.
    The ParallelOne task returns success as soon as any child succeeds.
    """

    def __init__(self, name, *args, **kwargs):
        super(ParallelOne, self).__init__(name, *args, **kwargs)

    def run(self):
        for c in self.children:
            c.status = c.run()
            if c.status == TaskStatus.SUCCESS:
                if self.reset_after:
                    self.reset()
                return TaskStatus.SUCCESS
        if self.reset_after:
            self.reset()

        return TaskStatus.FAILURE


class ParallelAll(Task):
    """
    A parallel task runs each child task at (roughly) the same time.
    The ParallelAll task requires all subtasks to succeed for it to succeed.
    """

    def __init__(self, name, *args, **kwargs):
        super(ParallelAll, self).__init__(name, *args, **kwargs)

    def run(self):
        n_success = 0
        n_children = len(self.children)
        for c in self.children:
            c.status = c.run()
            if c.status == TaskStatus.SUCCESS:
                n_success += 1
            if c.status == TaskStatus.FAILURE:
                return TaskStatus.FAILURE
            if n_success == n_children:
                return TaskStatus.SUCCESS
            else:
                return TaskStatus.RUNNING


class CallbackTask(Task):
    """
        Turn any callback function (cb) into a task
    """

    def __init__(self, name, cb=None, cb_args=[], cb_kwargs={}, **kwargs):
        super(CallbackTask, self).__init__(name, cb=None, cb_args=[], cb_kwargs={}, **kwargs)

        self.name = name
        self.cb = cb
        self.cb_args = cb_args
        self.cb_kwargs = cb_kwargs

    def run(self):
        status = self.cb(*self.cb_args, **self.cb_kwargs)

        if status is None:
            self.status = TaskStatus.RUNNING

        elif status:
            self.status = TaskStatus.SUCCESS

        else:
            self.status = TaskStatus.FAILURE

        return self.status

    def reset(self):
        self.status = None
