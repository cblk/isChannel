import lxml.html as lh
import requests
from lxml import etree
from detector.my_html import *

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
}


class LinkItem:
    def __init__(self, _item):
        """
        获取列表项的链接元素、文字、xpath等
        :param _item:
        """
        self.item = _item
        self.xpath = ListArea.get_path(_item)
        self.link, self.content, self.is_a = find_link(_item)
        if self.is_a:
            self.rel_xpath = './a'
        elif self.link is not None:
            self.rel_xpath = ListArea.get_relative_path(_item, self.link)
        self.tag = _item.tag
        self.loc = None

    def valid(self):
        return self.link is not None

    @staticmethod
    def get_items(_items):
        """
        批量初始化列表项
        :param _items:
        :return:
        """
        _res = []
        for _item in _items:
            link_item = LinkItem(_item)
            if link_item.valid():
                _res.append(link_item)
        return _res


class ListArea:
    tree = None

    def __init__(self, items, list_node):
        self.items = LinkItem.get_items(items)
        self.list_node = list_node
        self.list_path = ListArea.get_path(list_node)

    def item_filter(self):
        """
        根据列表项的相对路径合并列表项，并提取出最长的部分
        :return:
        """
        if not self.long_enough():
            return
        xpath_map = {}
        _items = []
        for _item in self.items:
            item_key = _item.rel_xpath
            if _item.is_a:
                item_key = 'a'
            xpath_map.setdefault(item_key, []).append(_item)
        sorted_items = sorted(xpath_map.items(), key=lambda x: len(x[1]), reverse=True)
        self.items = sorted_items[0][1]

    def long_enough(self):
        """
        判断是否为一个有效的列表
        :return:
        """
        return len(self.items) >= item_size

    def avg_words(self):
        """
        计算列表项的平均字数
        :return:
        """
        words_sum = 0
        for _item in self.items:
            words_sum += len(_item.content)
        return words_sum / len(self.items)

    @staticmethod
    def get_path(node):
        """
        获取页面元素的绝对xpath
        :param node:
        :return:
        """
        if ListArea.tree is not None:
            return ListArea.tree.getpath(node)

    @staticmethod
    def get_relative_path(ctx, node):
        """
        获取页面元素的相对路径
        :param ctx:
        :param node:
        :return:
        """
        if ctx is not None and node is not None:
            tree = etree.ElementTree(ctx)
            return tree.getpath(node)

    @staticmethod
    def get_tree(_content, url=None):
        """
        :param url: 网页地址
        :param _content: 网页内容
        :return: 解析后的Element对象
        """
        if url is not None:
            r = requests.get(url, headers=headers)
            r.encoding = r.apparent_encoding
            document = lh.fromstring(r.text)
        else:
            document = lh.fromstring(_content)
        ListArea.tree = etree.ElementTree(document)
        return document

    @staticmethod
    def find_list(page_src=None, url=None):
        """
        :param url: 网页地址
        :param page_src: 网页内容
        :return: 所有list结构
        """
        document = ListArea.get_tree(page_src, url)
        # document = document.xpath('/html/body/div[2]/div[1]/div')[0]
        return ListArea.find_list_in_doc(document)

    @staticmethod
    def find_list_in_doc(document):
        """
        从解析后的html根节点开始提取列表候选
        :param document:
        :return:
        """
        _res = {}
        lis = []
        for child in document.iter():
            items_list = list_merge(child)
            for items in items_list:
                list_area = ListArea(items, child)
                list_area.item_filter()
                if list_area.long_enough():
                    _res.setdefault(list_area.list_path, []).append(list_area)
                    lis.append(list_area)
        return _res, lis

    def find_static_path(self, _document):
        """
        根据列表在动态页面的位置，查找到其对应的静态页面的位置
        :param _document:
        :return:
        """
        target = find_node(self.list_node, _document)
        # 去重
        path_set = set()
        for t in target:
            path_set.add(etree.ElementTree(_document).getpath(t))
        return list(path_set)


if __name__ == '__main__':
    r = requests.get('https://guba.eastmoney.com/default,1_1.html', headers=headers)
    r.encoding = r.apparent_encoding
    with open('1.html', 'w') as f:
        f.write(r.text)
