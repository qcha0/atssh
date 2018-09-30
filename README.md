atssh
======

用python完成的一个简单的基于expect链接远程主机的工具，只用首次连接时输入相关的登录信息（IP地址、用户名、密码、端口）
过后只需通过指定IP即可

```bash
# 安装
bash build.sh ~/.zshrc

# 用法
atssh IP USERNAME PASSWORD PORT

# 第一次连接
atssh 192.168.1.99 root root 22

# 再次连接
atssh 192.168.1.99

```

目前只是初版，有待完善...