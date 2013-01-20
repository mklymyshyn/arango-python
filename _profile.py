import hotshot
import hotshot.stats
import os
import time
import tempfile
import sys

PROFILE_LOG_BASE = tempfile.gettempdir()


def profile(log_file):
    """Profile some callable.

    This decorator uses the hotshot profiler to profile some callable (like
    a view function or method) and dumps the profile data somewhere sensible
    for later processing and examination.

    It takes one argument, the profile log name. If it's a relative path, it
    places it under the PROFILE_LOG_BASE. It also inserts a time stamp into the
    file name, such that 'my_view.prof' become 'my_view-20100211T170321.prof',
    where the time stamp is in UTC. This makes it easy to run and compare
    multiple trials.

    Profiling will work only if ``DEBUG = True`` within ``settings.py``
    or if ``settings`` django package isn't accessible.

    Usage::

        @profile("my_view.prof")
        def my_view(request):
            ...


        @profile("some_func.prof")
        def utility_func(arg1, arg2, arg3, **kwargs):
            ...

    """

    if not os.path.isabs(log_file):
        log_file = os.path.join(PROFILE_LOG_BASE, log_file)

    def _outer(f):
        def _inner(*args, **kwargs):
            # Add a timestamp to the profile output when the callable
            # is actually called.

            (base, ext) = os.path.splitext(log_file)
            base = base + "-" + time.strftime("%Y%m%dT%H%M%S", time.gmtime())
            final_log_file = base + ext

            sys.stderr.write(
                "\n --> PROFILING REPORT: {}\n\n".format(final_log_file))
            prof = hotshot.Profile(final_log_file)
            try:
                ret = prof.runcall(f, *args, **kwargs)
            finally:
                prof.close()
                stats = hotshot.stats.load(final_log_file)
                stats.strip_dirs()
                stats.sort_stats('time', 'calls')
                stats.print_stats(20)

            return ret

        return _inner
    return _outer
