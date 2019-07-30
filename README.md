atssh
===

用python完成的一个简单的基于expect链接远程主机的工具，只用首次连接时输入相关的登录信息（IP地址、用户名、密码、端口），之后登陆只需通过制定ip即可登陆
密码会经过加密之后保存，不会直接保存明文
支持Python2.7+

安装
---
```bash
$ git clone https://github.com/Agnewee/atssh.git
$ cd atssh
$ chmod +x build.sh
$ ./build.sh ~/.zshrc
```

使用
---
```
$ atssh -h
usage: atssh.py [-h] [-P PORT] [-u USER] [-p PWD] [-a] [-d DELETE] [host]

Simple ssh tool for mac

positional arguments:
  host                  Destnation host ip address

optional arguments:
  -h, --help            show this help message and exit
  -P PORT, --port PORT  SSH protacol port (defalt 22)
  -u USER, --user USER  SSH authentication username
  -p PWD, --pwd PWD     SSH authentication password
  -a, --all             List all host ip addresses
  -d DELETE, --delete DELETE
                        Delete the specified host record

# ssh默认访问端口22，若为其他端口需要指定
$ atssh -h 192.168.1.12 -u root -p rootpassword -P 10022

$ atssh -a
*************** All Hosts ***************
Host: 192.168.1.12	Port: 22
*****************************************

$ atssh -d 192.168.1.12
Remove host 127.0.0.1 successfully

$ atssh -d 192.168.1.12
IP not exists in the cache
```

卸载
---
```
$ cd atssh
$ ./remove.sh
```

待完成
---

- [ ] 支持通过别名的方式登陆远程主机
- [ ] 初次登陆时，如果登陆成功立即将密码保存
- [ ] 支持scp传输文件