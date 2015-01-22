# *************************************************************************
# Copyright (c) 2014 - Maven Medical
# ************************
# AUTHOR:
__author__ = 'Tom DuBois'
# ************************
# DESCRIPTION:   This builder.py is designed to be SUB-CLASSED in order to function properly.
#
#
#
#
# ************************
# ASSUMES:
# ************************
# SIDE EFFECTS:
# ************************
# LAST MODIFIED FOR JIRA ISSUE:
# *************************************************************************

import asyncio
import traceback
import maven_logging as ML


# placeholder for a function which should never be called explicitly.
def _never_call(*args, **kwargs):
    raise Exception('This function cannot be called explicitly')


class builder():
    """ builder is a class designed to handle dependency resolution when building an object
    in an asyncronous way.  Here's some sample code:

    build = builder()

    @build.build(lambda: {})
    def build_composition(self, obj, username, patient):
        return obj

    @build.provide(Types.StaticTest1)
    def _StaticTest1(self, username, patient):
        return {username: patient}

    @build.provide(Types.StaticTest2)
    def _StaticTest2(self, username, patient):
        return {patient: username}

    @build.provide(Types.Unused1)
    def _Unused1(self, username, patient):
        print('running unused dependency')
        return {patient: username}

    @build.require(Types.StaticTest1, Types.StaticTest2)
    def _build_sample(self, obj, demographics, procedures):
        obj['demographics'] = demographics
        obj['procedures'] = procedures


    Calling self.build_composition(username, patient) will fire off _StaticTest1 and StaticTest2.
    When they complete, their results will be passed to _build_sample as it's 3rd and 4th args.
    When it (and any other "required" method complete, build_composition will be called
    _Unused is never called because the dependency it provides is never used
    """

    def __init__(self):
        pass
    providers = {}  # a map from dependencies to coroutines satisfying them
    workers = {}  # a map from coroutines (that take dependencies) to the dependencies they need

    @classmethod
    def provide(cls, dep):
        """ decorator function for instance functions in scheduler.
        The decorated function will be called, with arguments of self, username, patient
        whenever the dependency dep is required when building an object.
        The decorated function's name will be bound to an error - as it should not be called explicitly.
        """
        if dep in cls.providers:
            raise Exception('Cannot register multiple providers for ' + str(dep))

        def decorator(func):
            """ decorated function must take a self, username, patient
            """
            cls.providers[dep] = asyncio.coroutine(func)
            return _never_call

        return decorator

    @classmethod
    def require(cls, *args):
        """ decorator function for methods which parse the EHR's output and add them to the fhir composition
        _require's args are a list of types.  Each of these types must be registered using _provide
        Once the providers return, the decorated function will be called, passing in a composition object
        and the providers' return values (in the same order as specified in args.
        There is no return value (the function should modify the composition.
        Explicitly calling this function will raise an error.
        """
        if set(args).difference(cls.providers.keys()):
            raise Exception('Cannot satisfy requirements - no provider for '
                            + str(set(args).difference(cls.providers.keys())))

        def decorator(func):

            def worker(cls, obj, *args):
                # wait for all of the requirements to be satisfied
                done, pending = yield from asyncio.wait(args, return_when=asyncio.FIRST_EXCEPTION)
                task_errors = list(filter(lambda task: task.exception(), done))
                if pending or any(task_errors):
                    ML.INFO((task_errors, pending))
                    for task in task_errors:
                        ML.EXCEPTION(traceback.format_exception_only(type(task.exception()), task.exception()), False)
                    raise Exception('error processing dependencies: ' + str(task_errors))
                arg_results = [f.result() for f in args]
                yield from asyncio.coroutine(func)(cls, obj, *arg_results)  # call the function

            cls.workers[asyncio.coroutine(worker)] = args
            return _never_call

        return decorator

    @classmethod
    def build(cls, obj_factory):
        """ decorator function for methods which take a completely built object
        :params obj_factor: calling obj_factory() should return a base object to be filled out
                            by the workers registered with @require
        Once the object is built, it will yield from the decorated function, called with the
        same self, the object, and then the other parameters
        """

        def decorator(func):

            def worker(s, *args):
                obj = obj_factory()  # create the new object
                # find all dependencies needed by the workers
                dependencies = {dep for deps in cls.workers.values() for dep in deps}
                # map each dependency to an asyncio.Task for it's provider
                try:
                    dep_tasks = {dep: asyncio.Task(cls.providers[dep](s, *args))
                                 for dep in dependencies}
                    # create a Task for each worker, pass in the obj and the tasks for its dependencies
                    worker_tasks = {asyncio.Task(worker(s, obj, *[dep_tasks[dep] for dep in deps]))
                                    for worker, deps in cls.workers.items()}
                    # wait for all workers to finish
                    done, pending = yield from asyncio.wait(worker_tasks, timeout=10,
                                                            return_when=asyncio.FIRST_EXCEPTION)
                    task_errors = list(filter(lambda task: task.exception(), done))
                    if pending or any(task_errors):
                        ML.INFO((task_errors, pending))
                        for task in task_errors:
                            ML.EXCEPTION(traceback.format_exception_only(type(task.exception()), task.exception()), False)
                        ML.report('/composition_failed')
                        raise Exception('Error processing dependencies: ' + str(task_errors))
                    # pass the obj to the original function
                    return (yield from asyncio.coroutine(func)(s, obj, *args))
                finally:
                    # if any tasks haven't finished
                    [task.done() or task.cancel for task in worker_tasks]
                    [task.done() or task.cancel for task in dep_tasks.values()]

            return asyncio.coroutine(worker)
        return decorator
