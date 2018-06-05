import subprocess


def install_apk(path):
    subprocess.call(['adb', 'install', path])


def uninstall_apk(package):
    subprocess.call(['adb', 'uninstall', package])


