#!/usr/bin/env python
"""
Bootstrap script for prepare environ for project
"""

import os
import subprocess
import optparse
import sys
try:
    from urllib2 import Request, urlopen, HTTPError, URLError
except ImportError:
    from urllib.request import Request, urlopen, \
                                HTTPError, URLError

BOOTSTRAP_MOD = 'bootstrap'
BOOTSTRAP_ETAG = '._' + BOOTSTRAP_MOD + '.etag'
BOOTSTRAP_PY = BOOTSTRAP_MOD + '.py'
BOOTSTRAP_URL = 'https://raw.github.com/jellycrystal/bootstrap/master/bootstrap.py'
DEFAULT_PRE_REQS = ['virtualenv']

def _warn(msg):
    sys.stderr.write("Warn: %s\n" % (msg,))

def _err(msg):
    sys.stderr.write("Error: %s\n" % (msg,))
    sys.exit(1)

def get_pre_reqs(pre_req_txt):
    """Getting list of pre-requirement executables"""
    try:
        pre_reqs = open(pre_req_txt).readlines()
    except IOError:
        _warn("Couldn't find pre-reqs file: %s, use default pre-reqs" % pre_req_txt)
        # There are no pre-reqs yet.
        pre_reqs = DEFAULT_PRE_REQS
    for pre_req in pre_reqs:
        pre_req = pre_req.strip()
        # Skip empty lines and comments
        if not pre_req or pre_req.startswith('#'):
            continue
        yield pre_req

def check_pre_req(pre_req):
    """Check for pre-requirement"""
    if subprocess.call(['which', pre_req],
                       stderr=subprocess.PIPE, stdout=subprocess.PIPE) == 1:
        _err("Couldn't find '%s' in PATH" % pre_req)

def provide_virtualenv(ve_target, no_site=True, interpreter=None):
    """Provide virtualenv"""
    args = ['--distribute']
    if no_site:
        args.append('--no-site')
    if interpreter is not None:
        args.append('--python={0}'.format(interpreter))
    if not os.path.exists(ve_target):
        subprocess.call(['virtualenv'] + args + [ve_target])

def install_pip_requirements(ve_target, upgrade=False):
    """Install required Python packages into virtualenv"""
    version = sys.version_info
    prefix = "py"
    if hasattr(sys, "pypy_version_info"):
        version = sys.pypy_version_info
        prefix = "pypy"

    elif isinstance(version, tuple):
        major, minor, micro, t, b = version
    else:
        major = version.major
        minor = version.minor
        micro = version.micro

    req_name = "requirements"
    extensions = [
        "generic",
        "txt",
        "{0}_{1}".format(prefix, major),
        "{0}_{1}{2}".format(prefix, major, minor),
        "{0}_{1}{2}{3}".format(prefix, major, minor, micro)
    ]

    pip_path = os.path.join(ve_target, 'bin', 'pip')
    for ext in extensions:
        filename = "{0}.{1}".format(req_name, ext)
        if os.path.exists(filename):
            sys.stderr.write("Installing {0}...".format(filename))
            call_args = [pip_path, 'install', '-r', filename]
            if upgrade:
                call_args.append('--upgrade')
            try:
                if subprocess.call(call_args):
                    _err("Failed to install requirements")
            except OSError:
                _err("Something went wrong during installation requirements: " + \
                     " ".join(call_args))

def pass_control_to_doit(ve_target):
    """Passing further control to doit"""
    try:
        import dodo
    except ImportError:
        return

    if hasattr(dodo, 'task_bootstrap'):
        doit = os.path.join(ve_target, 'bin', 'doit')
        subprocess.call([doit, 'bootstrap'])

def do(func, *args, **kwargs):
    """Announce func.__doc__ and run func with provided arguments"""
    doc = getattr(func, '__doc__')
    if doc is None:
        doc = func.__name__
    func_args = ', '.join(str(a) for a in args)
    func_kwargs = ', '.join("%s=%s" % (k, str(kwargs.get(k)))
                            for k in kwargs.keys())
    msg = "%s... %s %s\n" % (doc, func_args, func_kwargs)
    sys.stderr.write(msg)
    return func(*args, **kwargs)


def bootstrap(pre_req_txt, ve_target, no_site=True,
        upgrade=False, interpreter=None):
    ve_target = os.path.normpath(os.path.abspath(ve_target))
    os.environ['BOOTSTRAP_VIRTUALENV_TARGET'] = ve_target
    for pre_req in do(get_pre_reqs, pre_req_txt):
        do(check_pre_req, pre_req)
    do(provide_virtualenv, ve_target, no_site=no_site, interpreter=interpreter)
    do(install_pip_requirements, ve_target, upgrade=upgrade)
    do(pass_control_to_doit, ve_target)

def update(**kwargs):
    """
    Self-update bootstrapping script.
    """
    # Idea taken from
    # http://tarekziade.wordpress.com/2011/02/10/a-simple-self-upgrade-build-pattern/
    if kwargs.pop('disable_bootstrap_update', False):
        bootstrap(**kwargs)
    headers = {}
    etag = current_etag = None
    # Getting the file age
    if os.path.exists(BOOTSTRAP_ETAG):
        with open(BOOTSTRAP_ETAG) as fh:
            current_etag = fh.read().strip()
            headers['If-None-Match'] = current_etag

    request = Request(BOOTSTRAP_URL, headers=headers)
    # Checking the last version on server
    try:
        sys.stderr.write("Fetching bootstrap's updates from %s..." %
                         BOOTSTRAP_URL)
        url = urlopen(request, timeout=5)
        etag = url.headers.get('ETag')
    except HTTPError as e:
        if e.getcode() not in (304, 412):
            raise
        # We're up to date -- 412 precondition failed
        etag = current_etag
        sys.stderr.write("Done. Up to date.\n")
    except URLError:
        # Timeout error
        etag = None
        sys.stderr.write("Fail. Connection error.\n")

    if etag is not None and current_etag != etag:
        sys.stderr.write("Done. New version available.\n")
        # We should update our version
        content = url.read()
        with open(BOOTSTRAP_PY, 'w') as fh:
            fh.write(content)
        with open(BOOTSTRAP_ETAG, 'w') as fh:
            fh.write(etag)
        sys.stderr.write("Bootstrap is updated to %s version.\n" % etag)

    mod = __import__(BOOTSTRAP_MOD)
    mod.bootstrap(**kwargs)


def main(args):
    parser = optparse.OptionParser()
    parser.add_option("-p", "--pre-requirements", dest="pre_requirements",
                      default="pre-reqs.txt", action="store", type="string",
                      help="File with list of pre-reqs")
    parser.add_option("-E", "--virtualenv", dest="virtualenv",
                      default='ve', action="store", type="string",
                      help="Path to virtualenv to use")
    parser.add_option("-P", "--python", dest="interpreter",
                      default=None, action="store", type="string",
                      help="Path to Python Interpreter to use")
    parser.add_option("-s", "--no-site", dest="no_site",
                      default=False, action="store_true",
                      help="Don't use global site-packages on create virtualenv")
    parser.add_option("-u", "--upgrade", dest="upgrade",
                      default=False, action="store_true",
                      help="Upgrade packages")
    parser.add_option("-b", "--disable-bootstrap-update",
                      dest="disable_bootstrap_update", default=False,
                      action="store_true",
                      help="Disable self-update of bootstrap script.")
    options, args = parser.parse_args(args)
    update(
        disable_bootstrap_update=options.disable_bootstrap_update,
        pre_req_txt=options.pre_requirements,
        ve_target=options.virtualenv,
        no_site=options.no_site,
        interpreter=options.interpreter,
        upgrade=options.upgrade)

if __name__ == '__main__':
    main(sys.argv)
