atssh
===

用python完成的一个简单的基于expect链接远程主机的工具，只用首次连接时输入相关的登录信息（IP地址、用户名、密码、端口）
过后只需通过指定IP即可

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
Simple ssh tool for mac:
-h --help             print help doc
-a --all              print all host
-d --delete host-ip   delete cache host info

# ssh默认访问端口22，若为其他端口需要指定
$ atssh 192.168.1.12 root rootpassword 10022

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