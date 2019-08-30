#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import time
import random
import pickle
import logging
import requests

from config import Config


class Login:
    page = 'http://sep.ucas.ac.cn'
    url = page + '/slogin'
    system = page + '/portal/site/226/821'
    pic = page + '/changePic'


class Course:
    base = 'http://jwxk.ucas.ac.cn'
    identify = base + '/login?Identity='
    selected = base + '/courseManage/selectedCourse'
    selection = base + '/courseManage/main'
    category = base + '/courseManage/selectCourse?s='
    save = base + '/courseManage/saveCourse?s='


class NetworkSucks(Exception):
    pass


class Cli(object):

    headers = {
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:61.0) Gecko/20100101 Firefox/61.0',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
    }

    def __init__(self, user, password, captcha=False):
        super(Cli, self).__init__()
        self.logger = logging.getLogger('logger')
        self.s = requests.Session()
        self.s.headers = self.headers
        self.s.timeout = Config.timeout
        self.login(user, password, captcha)
        self.initCourse()

    def get(self, url, *args, **kwargs):
        r = self.s.get(url, *args, **kwargs)
        if r.status_code != requests.codes.ok:
            raise NetworkSucks
        return r

    def post(self, url, *args, **kwargs):
        r = self.s.post(url, *args, **kwargs)
        if r.status_code != requests.codes.ok:
            raise NetworkSucks
        return r

    def initCourse(self):
        self.courseid = []
        with open('courseid', 'rb') as fh:
            for line in fh:
                collge_name, cid = line.strip().split(' ')
                if len(collge_name) and len(cid):
                    self.courseid.append([collge_name, cid])
        self.logger.debug('course inited')
        for c in self.courseid:
            print('%s:%s\n' % (c[0], c[1]))

    def login(self, user, password, captcha):
        if os.path.exists('cookie.pkl'):
            self.load()
        else:
            self.get(Login.page)
            data = {
                'userName': user,
                'pwd': password,
                'sb': 'sb'
            }
            if captcha:
                with open('captcha.jpg', 'wb') as fh:
                    fh.write(self.get(Login.pic).content)
                data['certCode'] = raw_input('input captcha >>> ')
            self.post(Login.url, data=data)
            if 'sepuser' not in self.s.cookies.get_dict():
                self.logger.error('login fail...')
                sys.exit()
            self.logger.error('login success...')
            self.save()
        r = self.get(Login.system)
        identity = r.content.split('<meta http-equiv="refresh" content="0;url=')
        if len(identity) < 2:
            self.logger.error('login fail')
            return False
        identityUrl = identity[1].split('"')[0]
        self.identity = identityUrl.split('Identity=')[1].split('&')[0]
        self.get(identityUrl)

    def save(self):
        self.logger.debug('save cookie...')
        with open('cookie.pkl', 'wb') as f:
            pickle.dump(self.s.cookies, f)

    def load(self):
        self.logger.debug('loading cookie...')
        with open('cookie.pkl', 'rb') as f:
            cookies = pickle.load(f)
            self.s.cookies = cookies

    def enroll(self):
        r = self.get(Course.selected)
        courseid = []
        msg = ['%s' % c[1] for c in self.courseid]
        self.logger.debug(msg)
        for cid in self.courseid:
            if cid[1] in r.content:
                self.logger.info('course %s already selected' % cid[1])
                continue
            if not self.enrollCourse(cid):
                self.logger.debug('try enroll course %s fail' % cid[1])
                courseid.append(cid)
            else:
                self.logger.debug("enroll course %s success" % cid[1])
        return courseid

    def enrollCourse(self, cid):
        r = self.get(Course.selection)
        depRe = re.compile(r'<label for="id_([0-9]{3})">(.*)<\/label>')
        deptIds = depRe.findall(r.content)
        for dep in deptIds:
            if cid[0] in dep[1]:
                deptid = dep[0]
                break
        identity = r.content.split('action="/courseManage/selectCourse?s=')[1].split('"')[0]
        data = {
            'deptIds': deptid,
            'sb': 0
        }
        categoryUrl = Course.category + identity
        r = self.post(categoryUrl, data=data)
        codeRe = re.compile(r'<span id="courseCode_([A-F0-9]{16})">' + cid[1] + '<\/span>')
        code = codeRe.findall(r.content)[0]
        data = {
            'deptIds': deptid,
            'sids': code
        }
        courseSaveUrl = Course.save + identity
        r = self.post(courseSaveUrl, data=data)
        if 'class="error"></label>' in r.content:
            return True
        else:
            return False


def initLogger():
    formatStr = '[%(asctime)s] [%(levelname)s] %(message)s'
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    chformatter = logging.Formatter(formatStr)
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(chformatter)
    logger.addHandler(ch)


def main():
    initLogger()
    with open('auth', 'rb') as fh:
        user = fh.readline().strip()
        password = fh.readline().strip()
    if '-c' in sys.argv or 'captcha' in sys.argv:
        captcha = True
    else:
        captcha = False
    c = Cli(user, password, captcha)
    while True:
        try:
            courseid = c.enroll()
            if not courseid:
                break
            c.courseid = courseid
            time.sleep(random.randint(Config.minIdle, Config.maxIdle))
        except IndexError as e:
            c.logger.info("Course not found, maybe not start yet")
            time.sleep(random.randint(Config.minIdle, Config.maxIdle))
        except KeyboardInterrupt as e:
            c.logger.info('user abored')
            break
        except (
            NetworkSucks,
            requests.exceptions.ConnectionError,
            requests.exceptions.ConnectTimeout
        ) as e:
            c.logger.debug('network error')
        except Exception as e:
            c.logger.error(repr(e))


if __name__ == '__main__':
    main()
