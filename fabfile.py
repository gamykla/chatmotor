import sys
import os
import signal
import distutils.spawn
import subprocess
import socket
import time

from fabric.api import task, local

RABBIT_MQ_IMAGE = "rabbitmq:3.5.4"


@task
def runserver():
    os.environ['CM_CONFIG_HOME'] = os.environ.get('CM_CONFIG_HOME', _get_default_config_dir())
    os.environ['CM_BINDINGS'] = os.environ.get('CM_BINDINGS', _get_default_bindings_file())

    sys.path.append(os.path.abspath('.'))
    from chatmotor import main
    main.run()


def _get_default_config_dir():
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'configuration')


def _get_default_bindings_file():
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'chatmotor', 'bindings.py')


@task
def clean():
    _remove_coverage()
    local('rm -fr coverage_html')
    local('rm -fr package')
    local('find . -name "*.pyc" -delete')


def _remove_coverage():
    local('rm -fr .coverage')



@task
def test_integration():
    server_subprocess = None
    rabbit_container_id = None

    try:
        # Start Rabbit
        run_cmd = "docker run -d -p 5672:5672 --hostname rmq --name rmq {}".format(RABBIT_MQ_IMAGE)
        rabbit_container_id = local(run_cmd, capture=True)
        _wait_for_server_availability(host="127.0.0.1", port=5672)

        time.sleep(5)

        # Start Tornado
        server_subprocess = _runserver_in_subprocess()
        _wait_for_server_availability(host="127.0.0.1", port=8888)

        local('nosetests tests/integration')

    finally:
        if server_subprocess is not None:
            os.killpg(server_subprocess.pid, signal.SIGTERM)

        if rabbit_container_id is not None:
            local('docker stop {}'.format(rabbit_container_id))
            local('docker rm {}'.format(rabbit_container_id))


@task
def test_units():
    import coverage
    import nose
    from nose.loader import TestLoader

    _remove_coverage()
    cov = coverage.coverage(branch=True, source=['chatmotor'])
    cov.start()
    nose.run(suite=TestLoader().loadTestsFromName("tests/unit"))
    cov.stop()
    cov.save()
    local('coverage report -m')


@task
def flake8():
    local('flake8 --max-line-length=120 .')


@task
def test_all():
    flake8()
    test_units()
    test_integration()
    local('piprot  requirements/development.txt')


@task
def build_docker_base():
    local('cd docker/base && docker build -t chatmotor_base .')


@task
def build_chatmotor_docker():
    clean()

    local('mkdir package')
    local('cp --recursive chatmotor package')
    local('cp fabfile.py package')
    local('cp docker/base/startup.sh package')
    local('cp --recursive requirements package')
    local('cp docker/chatmotor/Dockerfile package')

    local('cd package && docker build -t chatmotor .')


def _runserver_in_subprocess():
    runserver_args = [distutils.spawn.find_executable('fab'), 'runserver']

    return subprocess.Popen(
        runserver_args,
        stderr=subprocess.STDOUT,
        preexec_fn=os.setsid,
        env=os.environ.copy())


def _wait_for_server_availability(host="127.0.0.1", port=8888):
    print("Waiting for server port...")

    for _ in range(int(5 / 0.1)):
        sys.stdout.write('*')
        sys.stdout.flush()
        s = socket.socket()
        if s.connect_ex((host, port)) == 0:
            return
        time.sleep(0.1)

    sys.stdout.write("Unable to connect to port.. Exiting")
    sys.exit(1)


if __name__ == "__main__":
    runserver()
