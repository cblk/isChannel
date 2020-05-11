import time

from driver_common import chrome_option
from list import ListArea


class Window:
    def __init__(self, driver):
        # 浏览器大小
        self.__driverWidth = 1500
        self.__driverHeight = 1000

        # 页面属性
        self.__pageWidth = 0
        self.__pageHalfWidth = 0
        self.__pageHeight = 0
        self.__pageHalfHeight = 0
        self.__listPosMaxY = 960  # 列表允许出现的最底部位置
        self.__pageWidthJs = 'return document.body.scrollWidth;'
        self.__pageHeightJs = 'return document.body.scrollHeight;'

        # 浏览器driver
        self.driver = driver

    def set_size(self):
        try:
            self.__pageWidth = int(self.driver.execute_script(self.__pageWidthJs))
            self.__pageHeight = int(self.driver.execute_script(self.__pageHeightJs))
        except Exception as e:
            print("get page width err: {}".format(e))
            self.__pageWidth = 0
            self.__pageHeight = 0
        self.__pageWidth = self.__driverWidth if self.__pageWidth < self.__driverWidth else self.__pageWidth
        self.__pageHalfWidth = self.__pageWidth / 2

        self.__pageHeight = self.__driverHeight if self.__pageHeight < self.__driverHeight else self.__pageHeight
        self.__pageHalfHeight = self.__pageHeight / 2

        try:
            self.driver.set_window_size(self.__pageWidth, self.__pageHeight)
        except Exception as e:
            print("set_window_size err: {}".format(e))

        print("页面 width:{} 页面 height:{}".format(self.__pageWidth, self.__pageHeight))

    @staticmethod
    def run(url):
        c = chrome_option("test", False)
        driver = c.chrome_init()
        c.open_url(url, driver)
        window = Window(driver)
        window.set_size()
        window.find_list()
        time.sleep(100)

    def location(self, xpath):
        return self.driver.find_element_by_xpath(xpath).location

    def size(self, xpath):
        return self.driver.find_element_by_xpath(xpath).size

    def find_list(self):
        path_list, parent = ListArea.find_list(page_src=self.driver.page_source, idx=5)
        print("列表区域:{}\nsize : {}\nloc  :  {}\n".format(parent, self.size(parent), self.location(parent)))
        for content, link, xpath in path_list:
            print("title: {}\nurl:   {}\nsize: {}\nloc:   {}\n".
                  format(content, link.get('href'), self.size(xpath), self.location(xpath)))


if __name__ == '__main__':
    Window.run("https://stock.cngold.org/gundong")
