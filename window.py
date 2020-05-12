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
        self.__pageWidthJs = 'return document.body.scrollWidth;'
        self.__pageHeightJs = 'return document.body.scrollHeight;'

        # 浏览器driver
        self.driver = driver

    def set_size(self):
        """
        设置浏览器大小
        :return: None
        """
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

        print("页面宽度: {} 页面高度: {}\n".format(self.__pageWidth, self.__pageHeight))

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
        """
        获取页面元素的坐标
        :param xpath:
        :return:
        """
        return self.driver.find_element_by_xpath(xpath).location

    def size(self, xpath):
        """
        获取页面元素的尺寸
        :param xpath:
        :return:
        """
        return self.driver.find_element_by_xpath(xpath).size

    def center(self, xpath):
        """
        计算页面元素的中心坐标
        :param xpath:
        :return:
        """
        loc = self.location(xpath)
        siz = self.size(xpath)
        return loc['x'] + siz['width'] / 2, loc['y'] + siz['height'] / 2

    def center_dis(self, xpath):
        """
        计算页面元素的中心和页面中心的距离（归一化）
        :param xpath:
        :return:
        """
        x, y = self.center(xpath)
        x = (x - self.__pageHalfWidth) / self.__pageHalfWidth
        y = (y - self.__pageHalfHeight) / self.__pageHalfHeight
        return (x ** 2 + y ** 2) ** 0.5

    def area(self, xpath):
        """
        计算页面元素的面积（归一化）
        :param xpath:
        :return:
        """
        siz = self.size(xpath)
        x = siz['width'] / self.__pageWidth
        y = siz['height'] / self.__pageHeight
        return x * y

    def factor(self, xpath):
        """
        计算页面的权重，用于筛选出中心位置的元素
        :param xpath:
        :return:
        """
        return self.area(xpath) / self.center_dis(xpath)

    def find_list(self):
        """
        获取列表
        :return:
        """
        res, _ = ListArea.find_list(page_src=self.driver.page_source)
        res = sorted(res.items(), key=lambda x: self.factor(x[0]), reverse=True)
        # res.sort(key=lambda x: self.factor(x.list_path), reverse=True)
        for list_path, link_area_list in res:
            for link_area in link_area_list:
                if self.check_link_area(link_area):
                    break

    def check_link_area(self, link_area):
        """
        检查列表区域是否符合要求
        1. 是否垂直分布
        2. 是否有不可见的元素
        3. 单个列表项的文字长度大于5
        :param link_area:
        :return:
        """
        if self.is_vertical(link_area.links) and self.is_displayed_links(
                link_area.links) and link_area.avg_words > 5:
            path_list, list_path, item_path = link_area.print_list()
            print("列表:   {}\nsize:  {}\nloc: {}\n".
                  format(list_path, self.size(list_path), self.location(list_path)))
            print("列表项:  {}\n".format(item_path))
            for content, link, xpath in path_list:
                print("title: {}\nurl:   {}\nsize: {}\nloc:   {}\n".
                      format(content, link.get('href'), self.size(xpath), self.location(xpath)))
            return True
        return False

    def is_vertical(self, links):
        """
        检查一个列表是否在页面上垂直布局
        :param links:
        :return:
        """
        loc0 = self.location(ListArea.get_path(links[0]))
        loc1 = self.location(ListArea.get_path(links[1]))
        return abs(loc0['y'] - loc1['y']) > abs(loc0['x'] - loc1['x'])

    def is_displayed(self, xpath):
        """
        检查页面元素是否可见
        :param xpath:
        :return:
        """
        return self.driver.find_element_by_xpath(xpath).is_displayed()

    def is_displayed_links(self, links):
        """
        检查列表是否全部可见
        :param links:
        :return:
        """
        for link in links:
            xpath = ListArea.get_path(link)
            if not self.is_displayed(xpath):
                return False
        return True


if __name__ == '__main__':
    # Window.run("https://guba.eastmoney.com/default,1_1.html")
    # Window.run("https://stock.cngold.org/gundong/")
    # Window.run("http://www.zichanjie.com/zhuanlan/zepinghongguan")
    # Window.run("http://paper.jyb.cn/zgjyb/html/2020-03/20/node_2.htm")
    # Window.run("http://www.jyb.cn/rmtsy1240/zt/sxxy/")
    # Window.run("http://mrdx.cn/content/20200320/Page16DK.htm")
    # Window.run("http://mrdx.cn/content/20200320/Page01DK.htm")
    # Window.run("http://digitalpaper.stdaily.com/http_www.kjrb.com/kjrb/html/2020-03/12/node_4.htm")
    # Window.run("http://paper.ce.cn/jjrb/html/2020-03/16/node_2.htm")
    # Window.run("https://epaper.gmw.cn/gmrb/html/2020-03/16/nbs.D110000gmrb_01.htm")
    # Window.run("http://www.81.cn/jfjbmap/content/2020-03/12/node_3.htm")
    # Window.run("http://dz.jjckb.cn/www/pages/webpage2009/html/2020-03/12/node_4.htm")
    Window.run("http://mrdx.cn/content/20200320/Page03DK.htm")