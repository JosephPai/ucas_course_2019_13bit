# ucas_course_2019_13bit

中国科学院大学（国科大，UCAS）2019年9月选课脚本，支持新版13位课程编码，支持轮询选课，当有人退课时自动选课。

## 安装

### 环境依赖

Python 2.x

### Mac

```bash
brew install python
sudo easy_install pip
sudo pip install requests
```

### Linux

```bash
sudo apt install python-pip
sudo pip install requests
```

### Windows

官网中安装Python后安装requests

```bash
python -m pip install requests
```

## 初始化

在当前目录下创建 `auth` 文件并填入登录信息，格式如下：

```
xxx@mails.ucas.ac.cn
password
```

第一行为用户名，第二行为密码

在当前目录下创建 `courseid` 文件并填入课程，格式如下：

```
学院简称 课程编号（中间有空格）
```
例如
```
计算机 081201M05003H
心理 040200MGX008H
```

学院简称从[college_names](./college_names)查询，请务必按照该简称填写。

config文件中共有三个配置，单次请求等待时间，单位为秒s，轮询最短时间和轮询最长时间，可根据需求修改

## 持久运行

非校园网环境登录需要验证码，须长期轮询是否有人退课时，可使用 ``python enroll.py -c`` 命令运行， 此时会在目录下生成captcha.jpg文件，根据该图片的内容输入验证码即可登录。


## 致谢

原项目地址：https://github.com/LyleMi/ucas

代码是在UCAS前辈提供的项目基础上修改，表示郑重感谢！

主要针对在2019年9月选课过程中，课程编码变为13位修改了部分逻辑。

欢迎Star和各种PR，祝同学们都能抢到心仪的课程！
