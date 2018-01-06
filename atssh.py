# coding: utf-8
from __future__ import print_function
import os
import sys
from subprocess import Popen, PIPE


def getoutput(cmd):
    p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    out, _ = p.communicate()
    return out.strip()


class ATSSH(object):

    EXPECT_STR = """set timeout 30
spawn ssh -o "StrictHostKeyChecking no" -p{port} -l {username} {ip}
expect "password:"
send "{password}\r"
interact
"""
    
    def __init__(self, ip, username=None, password=None, port=22):
        self.ip = ip
        self.username = username
        self.password = password
        self.port = port
        self.cache_dir = None
        self.init_home_dir()
    
    def init_home_dir(self):
        home_dir = getoutput('cd ~; pwd')
        self.cache_dir = os.path.join(home_dir, '.atssh')
        if not os.path.exists(self.cache_dir):
            os.mkdir(self.cache_dir)
    
    def query_cache_file(self):
        expect_file = os.path.join(self.cache_dir, self.ip)
        if not os.path.exists(expect_file):
            if self.username and self.password:
                self.gen_cache_file(expect_file)
                return True
            else:
                return False
        else:
            return True
            
    def gen_cache_file(self, expect_file):
        with open(expect_file, 'w') as f:
            f.write(self.EXPECT_STR.format(ip=self.ip,
                                           username=self.username,
                                           password=self.password,
                                           port=self.port))
        getoutput('chmod +x {expect_file}'.format(expect_file=expect_file))

    def run(self):
        result = self.query_cache_file()
        if result:
            os.system('cd {cache_dir}; ./{expect_file}'
                      .format(cache_dir=self.cache_dir,
                              expect_file=self.ip))
        else:
            print()
            print('The %s has no cache and Cannot find Login'
                  'info in the input message' % self.ip)
            print()


if __name__ == '__main__':
    argv_len = len(sys.argv)
    if argv_len < 2:
        print()
        print('Please input something')
        print()
        sys.exit(1)
    ip = sys.argv[1]
    if argv_len > 4:
        username = sys.argv[2]
        password = sys.argv[3]
        port = sys.argv[4]
    elif argv_len > 3:
        username = sys.argv[2]
        password = sys.argv[3]
        port = 22
    else:
        username = None
        password = None
        port = 22
    pssh = ATSSH(ip, username, password, port)
    pssh.run()
