# !/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import time

import requests
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    )


def chrome_quit(driver):
    if driver is not None:
        driver.quit()


class Chrome(object):
    def __init__(self, headless=False):
        self.Session = requests.session()
        self.LOG = logging
        self.headless = headless
        # chrome exe and driver path
        self.chrome_path = None
        self.chrome_driver_path = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/74.0.3729.131 Safari/537.36 '
        }
        self.driver = None
        self.chrome_init()

    def get_url(self, url, last_url=None, stream=False, timeout=100):
        last_url = url
        self.headers['Referer'] = last_url
        return self.Session.get(url=url, headers=self.headers, stream=stream, timeout=timeout, verify=False)

    def chrome_init(self):
        """
        初始化浏览器
        """
        try:
            dec = DesiredCapabilities.CHROME
            dec['loggingPrefs'] = {'performance': 'ALL'}
            opts = webdriver.ChromeOptions()
            if self.headless:
                opts.add_argument('headless')
            opts.add_argument('--disable-gpu')
            opts.add_argument('--disable-images')
            opts.add_argument('--disable-plugins')
            opts.add_argument('--no-sandbox')
            opts.add_argument('--disable-dev-shm-usage')
            self.driver = webdriver.Chrome(chrome_options=opts, desired_capabilities=dec)
            self.driver.implicitly_wait(30)
            self.driver.set_page_load_timeout(25)
            return self.driver
        except Exception as e:
            self.LOG.error('chrome list driver init fail: {}'.format(e))
            return None

    def get_http_status(self):
        try:
            if self.get_url(self.driver.current_url).status_code == 200:
                self.LOG.info('{url} requests 请求成功'.format(url=self.driver.current_url))
                return 200
        except Exception as e:
            self.LOG.info('{url} requests 请求失败 {err}'.format(url=self.driver.current_url, err=e))
            return None
        for responseReceived in self.driver.get_log('performance'):
            try:
                response = json.loads(responseReceived[u'message'])[u'message'][u'params'][u'response']
                if response[u'url'] == self.driver.current_url:
                    return response[u'status']
            except Exception as e:
                self.LOG.info('{url} 当前页面无法访问 {err}'.format(url=self.driver.current_url, err=e))
                return None
        return None

    def open_url(self, url):
        try:
            self.driver.get(url)
            status = self.get_http_status()
            try_num = 0
            while try_num < 60 and status is None:
                time.sleep(1)
                try_num += 1
                status = self.get_http_status()
            # print status
            assert status == 200
        except Exception as e:
            print("open url err: ", e)

    def quit(self):
        if self.driver is not None:
            self.driver.quit()


if __name__ == '__main__':
    chrome_driver = Chrome()
    chrome_driver.open_url("http://www.npc.gov.cn/")
    print(chrome_driver.driver.title)
    chrome_driver.quit()
