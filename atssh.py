# coding: utf-8
from __future__ import print_function
import os
import re
import sys
import argparse
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


MAGIC_NUM = 1


def encrypt(to_encrypt):
    result = []
    for i in to_encrypt:
        result.append(chr(ord(i) + MAGIC_NUM).encode())
    if is_bytes:
        return 'new___' + encry(b''.join(result)).decode().strip()
    else:
        return 'new___' + encry(''.join(result)).strip()


def decrypt(to_decrypt):
    # 兼容原本明文保存密码的方式
    if not to_decrypt.startswith('new___'):
        return to_decrypt
    to_decrypt = to_decrypt.lstrip('new___')
    strings = decry(to_decrypt.encode()).decode() if is_bytes else decry(
        to_decrypt)
    result = []
    num = 0
    for i in strings:
        result.append(chr(ord(i) - MAGIC_NUM))
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
        self.config_file = get_config_file()

    @property
    def config(self):
        if not self._config:
            self._config = ConfigParser()
            self._config.read(self.config_file)
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
            print('The {} has no cache and Cannot find Login'
                  'info in the input message'.format(ip))
            sys.exit(1)

    def list_all_ip(self):
        print('========== All Hosts ==========')
        for ip in self.config.sections():
            print('Host: {}\tPort: {}'.format(ip, self.config.get(ip, 'port')))
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

    def action(self):
        args = parse_arg()
        if args.all:
            self.list_all_ip()
        elif args.delete:
            self.remove_ip(args.delete)
        else:
            self.run(args.host, args.user, args.pwd, args.port)


def parse_arg():
    parser = argparse.ArgumentParser(description='Simple ssh tool for mac')
    parser.add_argument('host', nargs='?',
                        help='Destnation host ip address')
    parser.add_argument('-P', '--port', type=int, default=22,
                        help='SSH protacol port (defalt 22)')
    parser.add_argument('-u', '--user',
                        help='SSH authentication username')
    parser.add_argument('-p', '--pwd',
                        help='SSH authentication password')
    parser.add_argument('-a', '--all', action='store_true',
                        help='List all host ip addresses')
    parser.add_argument('-d', '--delete',
                        help='Delete the specified host record')
    args = parser.parse_args()
    if not any((args.host, args.all, args.delete)):
        sys.exit(1)
    return args


if __name__ == '__main__':
    atssh = ATSSH()
    atssh.action()
