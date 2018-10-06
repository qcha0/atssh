# coding: utf-8
from __future__ import print_function
import os
import re
import sys
from telnetlib import Telnet

if sys.version_info.major > 2:
    from configparser import ConfigParser
    from base64 import encodebytes as encry
    from base64 import decodebytes as decry
    is_bytes = True
else:
    from ConfigParser import ConfigParser
    from base64 import encodestring as encry
    from base64 import decodestring as decry
    is_bytes = False
    input = raw_input


def encrypt(to_encrypt):
    result = []
    num = 0
    for i in to_encrypt:
        result.append(chr(ord(i) + num).encode())
        num += 1
    if is_bytes:
        return 'new___' + encry(b''.join(result)).decode().strip()
    else:
        return 'new___' + encry(''.join(result)).strip()


def decrypt(to_decrypt):
    # 兼容原本明文保存密码的方式
    if not to_decrypt.startswith('new___'):
        return to_decrypt
    to_decrypt = to_decrypt.lstrip('new___')
    strings = decry(to_decrypt.encode()).decode() if is_bytes else decry(to_decrypt)
    result = []
    num = 0
    for i in strings:
        result.append(chr(ord(i) - num))
        num += 1
    return ''.join(result)


def test_connect(host, port, timeout=5):
    """测试主机地址及端口是否可用"""
    client = Telnet()
    try:
        client.open(host, port, timeout=timeout)
        return True
    except:
        print('Cannot connect IP:{} port:{}'.format(host, port))
        return False


def check_ip(ip):
    if not re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', ip):
        print('Please input valid IP')
        sys.exit(1)


def get_config_file():
    atssh_home = os.getenv('ATSSH_ROOT')
    if not atssh_home:
        raise OSError('Cannot load ATSSH_ROOT environ variable')
    config_file = os.path.join(atssh_home, 'config.ini')
    return config_file


class ATSSH(object):

    EXPECT_SSH = """set timeout 30
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

    def __init__(self):
        self._config = None

    @property
    def config(self):
        if not self._config:
            self._config = ConfigParser()
            self._config.read(get_config_file())
        return self._config

    def run(self, ip, username=None, password=None, port=22):
        if self.has_cache(ip):
            login_info = self.query_from_ip(ip)
            cmd = self.EXPECT_SSH.format(**login_info)
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
                print('Please confirm login username or password')
                sys.exit(1)
        else:
            print('The %s has no cache and Cannot find Login'
                  'info in the input message' % ip)
            sys.exit(1)
    
    @staticmethod
    def print_help():
        print('Simple ssh tool for mac:')
        print('\natssh host [username] [password] [port]\n')
        print('-h --help             print help doc')
        print('-a --all              print all host')
        print('-d --delete host-ip   delete cache host info')

    def list_all_ip(self):
        print('========== All Hosts ==========')
        for ip in self.config.sections():
            print('\tHost: {} Port: {}'.format(ip, self.config.get(ip, 'port')))
        print('===============================')

    def remove_ip(self, ip):
        if self.has_cache(ip):
            self.config.remove_section(ip)
            self._write_to_config()
            print('Remove host {} successfully'.format(ip))
        else:
            print('IP not exists in the cache')
            sys.exit(1)

    def has_cache(self, ip):
        return self.config.has_section(ip)

    def query_from_ip(self, ip):
        return {'ip': ip,
                'username': self.config.get(ip, 'username'),
                'password': decrypt(self.config.get(ip, 'password')),
                'port': self.config.get(ip, 'port')}

    def record_login_info(self, ip, username, password, port):
        """
        将输入的用户信息录入配置文件中
        """
        self.config.add_section(ip)
        self.config.set(ip, 'username', username)
        self.config.set(ip, 'password', encrypt(password))
        self.config.set(ip, 'port', port)
        self._write_to_config()

    def _write_to_config(self):
        with open(self.config_file, 'w') as f:
            self.config.write(f)


if __name__ == '__main__':
    atssh = ATSSH()

    argv_len = len(sys.argv)
    if argv_len < 2 or '-h' in sys.argv or '--help' in sys.argv:
        atssh.print_help()
    elif '-a' in sys.argv or '--all' in sys.argv:
        atssh.list_all_ip()
    else:
        if '-d' in sys.argv or '--delete' in sys.argv:
            ip = sys.argv[2]
            check_ip(ip)
            atssh.remove_ip(ip)
        else:
            ip = sys.argv[1]
            check_ip(ip)
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
