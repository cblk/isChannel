import time

from driver_common import Chrome
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
        设置浏览器尺寸参数
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
        对于处于页面下半部分的元素，追加额外的距离
        :param xpath:
        :return:
        """
        x, y = self.center(xpath)
        x = (x - self.__pageHalfWidth) / self.__pageHalfWidth
        y = (y - self.__pageHalfHeight) / self.__pageHalfHeight
        if y > 0:
            y = y * 1.5
        return (x ** 2 + y ** 2) ** 0.5 + 0.0001

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

    def factor(self, xpath, link_area_list):
        """
        计算页面的权重，用于筛选出中心位置的元素
        :param link_area_list:
        :param xpath:
        :return:
        """
        if len(link_area_list) == 0:
            return 0
        link_sum = 0
        link_height_sum = 0
        for link_area in link_area_list:
            link_sum += len(link_area.items)
            link_height = 0
            for _item in link_area.items:
                link_height += self.size(_item.xpath)['height']
            link_height_sum += link_height
        link_area_height = self.size(xpath)['height']
        return self.area(xpath) / self.center_dis(xpath) * (link_height_sum / link_area_height) * (link_sum / 10)

    def find_list(self):
        """
        获取列表
        :return:
        """
        res, _ = ListArea.find_list(page_src=self.driver.page_source)
        for list_path in res:
            res[list_path] = [list_area for list_area in res[list_path] if self.check_link_area(list_area)]

        res = sorted(res.items(), key=lambda x: self.factor(x[0], x[1]), reverse=True)
        has_list = False
        for list_path, link_area_list in res:
            for link_area in link_area_list:
                self.print_link_area(link_area)
                has_list = True
                break
        if not has_list:
            print('未找到列表')

    def check_link_area(self, link_area):
        """
        检查列表区域是否符合要求
        1. 是否垂直分布
        2. 是否有不可见的元素
        3. 单个列表项的文字长度大于5
        :param link_area:
        :return:
        """
        return self.is_vertical(link_area.items) and self.is_displayed_links(
            link_area.items) and link_area.avg_words() > 5

    def print_link_area(self, link_area):
        """
        输出格式化列表
        :param link_area:
        :return:
        """
        list_path = link_area.list_path
        print('---------------------------------------------')
        print("列表:   {}\nsize:  {}\nloc: {}\n".
              format(list_path, self.size(list_path), self.location(list_path)))
        for item in link_area.items:
            print("title: {}\nurl:   {}\nsize: {}\nloc:   {}\nxpath: {}\n".
                  format(item.content, item.link.get('href'), self.size(item.xpath),
                         self.location(item.xpath), item.rel_xpath))

    def is_vertical(self, items):
        """
        检查一个列表是否在页面上垂直布局
        :param items:
        :return:
        """
        loc0 = self.location(items[0].xpath)
        loc1 = self.location(items[1].xpath)
        loc2 = self.location(items[2].xpath)
        return loc0['y'] < loc1['y'] < loc2['y']
        # return abs(loc0['y'] - loc1['y']) > abs(loc0['x'] - loc1['x'])

    def is_displayed(self, xpath):
        """
        检查页面元素是否可见
        :param xpath:
        :return:
        """
        return self.driver.find_element_by_xpath(xpath).is_displayed()

    def is_displayed_links(self, items):
        """
        检查列表是否全部可见
        :param items:
        :return:
        """
        for _item in items:
            if not self.is_displayed(_item.xpath):
                return False
        return True

    @staticmethod
    def run(url):
        """
        根据url中获取列表
        :param url:
        :return:
        """
        c = Chrome()
        c.open_url(url)
        window = Window(c.driver)
        window.set_size()
        window.find_list()
        time.sleep(100)


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
    # Window.run("http://mrdx.cn/content/20200320/Page03DK.htm")
    # Window.run("https://www.shobserver.com/journal/2020-03-12/page_12.htm")
    # Window.run("https://www.shobserver.com/news/list?section=1")
    # Window.run("https://tophub.today/n/KqndgxeLl9")
    # Window.run("http://www.zgdazxw.com.cn/culture/node_2016.htm")
    # Window.run("http://www.zgdazxw.com.cn/news/yaowen.html")
    # Window.run("http://www.zgsjbs.com/zgsjb/sj/")
    # Window.run("http://www.moe.gov.cn/jyb_xwfb/xw_zt/moe_357/jyzt_2019n/2019_zt2/zt1902_dbwy/")
    # Window.run("http://www.sciencenet.cn/life/")
    # Window.run("https://coffee.pmcaff.com/?type=2")
    # Window.run("http://www.moe.gov.cn/jyb_xwfb/xw_zt/moe_357/jyzt_2020n/2020_zt03/")
    # #Window.run("https://www.thepaper.cn/list_90069")
    # Window.run("http://kdslife.com/f_15.html")
    Window.run("https://www.qbitai.com/")
    # Window.run("")
    # Window.run("")
