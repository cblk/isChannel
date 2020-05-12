import lxml.html as lh
import requests
from lxml import etree

from html import *

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 '
                  'Safari/537.36 '
}


class ListArea:
    tree = None

    def __init__(self, links, list_node, avg_words):
        self.links = links
        self.list_node = list_node
        self.list_path = ListArea.get_path(list_node)
        self.avg_words = avg_words
        self.tag = links[0].tag
        _link, _ = find_link(self.links[0])
        self.item_path = ListArea.get_relative_path(self.links[0], _link)

    @staticmethod
    def get_path(node):
        if ListArea.tree is not None:
            return ListArea.tree.getpath(node)

    @staticmethod
    def get_relative_path(ctx, node):
        if ctx is not None and node is not None:
            tree = etree.ElementTree(ctx)
            return tree.getpath(node)

    def print_list(self):
        """
        :return: 输出列表的详细信息
        """
        _path_list = []
        for child in self.links:
            _link, _content = find_link(child)
            if _link is not None:
                _xpath = ListArea.get_path(_link)
                _path_list.append((_content, _link, _xpath))
        return _path_list, self.list_path, self.item_path

    @staticmethod
    def get_tree(_content, url=None):
        """
        :param url: 网页地址
        :param _content: 网页内容
        :return: 解析后的Element对象
        """
        if url is not None:
            r = requests.get(url)
            r.encoding = r.apparent_encoding
            document = lh.fromstring(r.text)
        else:
            document = lh.fromstring(_content)
        ListArea.tree = etree.ElementTree(document)
        return document

    @staticmethod
    def find_list(page_src=None, url=None, idx=-1):
        """
        :param url: 网页地址
        :param page_src: 网页内容
        :param idx: 列表选择
        :return: 所有list结构
        """
        document = ListArea.get_tree(page_src, url)
        # document = document.xpath('//*[@id="middle"]/tbody/tr/td[1]/div/div[4]/div/ul')[0]
        return ListArea.find_list_in_doc(document)

    @staticmethod
    def find_list_in_doc(document):
        res = {}
        lis = []
        for child in document.iter():
            list_max, total_words = list_merge(child)
            if len(list_max) > 2:
                list_area = ListArea(list_max, child, total_words / len(list_max))
                res.setdefault(list_area.list_path, []).append(list_area)
                lis.append(list_area)
        return res, lis


if __name__ == '__main__':
    _, res = ListArea.find_list(url='http://finance.camase.com/c4.aspx')
    res.sort(key=lambda x: len(x.links), reverse=True)
    path_list, list_path, item_path = res[4].print_list()

    print("列表:   {}\n列表项: {}\n".format(list_path, item_path))
    for content, link, xpath in path_list:
        print("title: {}\nurl:   {}\nxpath: {}\n".format(content, link.get('href'), xpath))
