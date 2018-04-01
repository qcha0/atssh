# coding: utf-8
from __future__ import print_function
import os
import re
import sys
import socket
from telnetlib import Telnet

if sys.version_info.major > 2:
    from configparser import ConfigParser
else:
    from ConfigParser import ConfigParser


def test_connect(ip, port, timeout=5):
    tn = Telnet()
    try:
        tn.open(ip, port, timeout=timeout)
        return True
    except (socket.timeout, socket.error, socket.gaierror):
        print('\nCannot connect IP:%s port:%s\n' % (ip, port))
        return False


class ATSSH(object):

    EXPECT_SSH = """set timeout 10
spawn ssh -o "StrictHostKeyChecking no" -p{port} -l {username} {ip}
expect {{
    "assword:" {{
        send "{password}\r";
        exp_continue
    }}
    "denied" {{
        puts "Wrong password"
        exit 1;
    }}
    "ogin:" {{
        interact
    }}
}}
"""
    EXPECT_SCP = """set timeout 10
spawn scp -P{port} {src_file} {username}@{ip}:{dest_file}
expect {{
    "assword:" {{
        send "{password}\r"
    }}
    "defied" {{
        puts "Wrong password"
        exit 1;
    }}
}}
expect eof

"""
    
    def __init__(self):
        self.config_file = self._config_file()
        self.config = self.get_config()

    def get_config(self):
        config = ConfigParser()
        config.read(self.config_file)
        return config

    def run(self, ip, username=None, password=None, port=22):
        if self.has_cache(ip):
            login_info = self.query_from_ip(ip)
            cmd = self.EXPECT_STR.format(**login_info)
            os.system("expect -c '{}'".format(cmd))
        elif username and password:
            can_connect = test_connect(ip, int(port))
            if not can_connect:
                sys.exit(1)

            cmd = self.EXPECT_SSH.format(ip=ip,
                                         username=username,
                                         password=password,
                                         port=port)
            retcode = os.system("expect -c '{}'".format(cmd))
            if retcode == 0:
                self.record_login_info(ip, username, password, port)
            else:
                print('\nPlease confirm login username or password\n')
                sys.exit(1)
        else:
            print('\nThe %s has no cache and Cannot find Login'
                  'info in the input message\n' % ip)
            sys.exit(1)

    def list_all_ip(self):
        print('========== All Hosts ==========')
        for ip in self.config.sections():
            print('{}:{}'.format(ip, self.config.get(ip, 'port')))
        print('===============================')

    def remove_ip(self, ip):
        if self.has_cache(ip):
            self.config.remove_section(ip)
            self._write_to_config()
        else:
            print('IP not exists in the cache')
            sys.exit(1)

    def has_cache(self, ip):
        return self.config.has_section(ip)

    def query_from_ip(self, ip):
        return {
                'ip': ip,
                'username': self.config.get(ip, 'username'),
                'password': self.config.get(ip, 'password'),
                'port': self.config.get(ip, 'port')
               }

    def record_login_info(self, ip, username, password, port):
        self.config.add_section(ip)
        self.config.set(ip, 'username', username)
        self.config.set(ip, 'password', password)
        self.config.set(ip, 'port', port)
        self._write_to_config()

    def _write_to_config(self):
        with open(self.config_file, 'w') as f:
            self.config.write(f)

    @staticmethod
    def _config_file():
        atssh_home = os.getenv('ATSSH_ROOT')
        if not atssh_home:
            raise OSError('Cannot load ATSSH_ROOT environ variable')
        config_file = os.path.join(atssh_home, 'config.ini')
        return config_file


if __name__ == '__main__':
    argv_len = len(sys.argv)
    if argv_len < 2:
        print('\nPlease input something\n')
        sys.exit(1)
    ip = sys.argv[1]

    atssh = ATSSH()
    if '-h' in sys.argv or '--help' in sys.argv:
        print('Simple ssh tool for mac:')
        print('-h --help             print help doc')
        print('-a --all              print all host')
        print('-d --delete host-ip   delete cache host info')
    if '-a' in sys.argv or '--all' in sys.argv:
        atssh.list_all_ip()
    if '-d' in sys.argv or '--delete' in sys.argv:
        atssh.remove_ip(ip)
    else:
        if not re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', ip):
            print('\nPlease input valid IP')
        sys.exit(1)

        if argv_len > 4:
            username = sys.argv[2]
            password = sys.argv[3]
            port = sys.argv[4]
        elif argv_len > 3:
            username = sys.argv[2]
            password = sys.argv[3]
            port = '22'
        else:
            username = None
            password = None
            port = '22'
        atssh.run(ip, username, password, port)
