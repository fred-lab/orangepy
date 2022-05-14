import subprocess


def ping(host):
    command = ['ping', '-c 3', '-s 1', '-v', host]

    return subprocess.run(command).returncode == 0
