import queue


class Task(object):
    taskid = 0

    def __init__(self, target):
        Task.taskid += 1

        self.tid = Task.taskid
        self.target = target
        self.sendval = None

    def run(self):
        return self.target.send(self.sendval)


class SystemCall(object):
    def handle(self):
        pass


class Scheduler(object):
    def __init__(self):
        self.ready = queue.Queue()
        self.taskmap = {}

    def new(self, target):
        newtask = Task(target)
        self.taskmap[newtask.tid] = newtask
        self.schedule(newtask)
        return newtask.tid

    def schedule(self, task):
        self.ready.put(task)

    def exit(self, task):
        print('Task {0} terminated'.format(task.tid))
        del self.taskmap[task.tid]

    def mainloop(self):
        while self.taskmap:
            task = self.ready.get()
            try:
                result = task.run()
                if isinstance(result, SystemCall):
                    result.task = task
                    result.scheduler = self
                    result.handle()
                    continue
            except StopIteration:
                self.exit(task)
                continue

            self.schedule(task)


class GetTid(SystemCall):
    def handle(self):
        self.task.sendval = self.task.tid
        self.scheduler.schedule(self.task)


def foo():
    mytid = yield GetTid()
    for i in range(5):
        print("I'm foo", mytid)
        yield


def bar():
    mytid = yield GetTid()
    for i in range(10):
        print("I'm bar", mytid)
        yield


def main():
    scheduler = Scheduler()
    scheduler.new(foo())
    scheduler.new(bar())
    scheduler.mainloop()


if __name__ == '__main__':
    main()
