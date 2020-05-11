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

    def __init__(self, links, parent_node, avg_words):
        self.links = links
        self.parent_node = parent_node
        self.avg_words = avg_words

    @staticmethod
    def get_path(node):
        if ListArea.tree is not None:
            return ListArea.tree.getpath(node)

    def print_list(self):
        """
        :return: 输出列表的详细信息
        """
        _path_list = []
        _parent = self.get_path(self.parent_node)
        for child in self.links:
            _link, _content = find_link(child)
            if _content is not None:
                _xpath = ListArea.get_path(_link)
                _path_list.append((_content, _link, _xpath))
        return _path_list, _parent

    @staticmethod
    def get_tree(content, url=None):
        """
        :param url: 网页地址
        :param content: 网页内容
        :return: 解析后的Element对象
        """
        if url is not None:
            r = requests.get(url)
            r.encoding = 'utf-8'
            document = lh.fromstring(r.text)
        else:
            document = lh.fromstring(content)
        ListArea.tree = etree.ElementTree(document)
        return document

    @staticmethod
    def find_list(page_src=None, url=None, idx=0):
        """
        :param url: 网页地址
        :param page_src: 网页内容
        :param idx: 列表选择
        :return: 所有list结构
        """
        document = ListArea.get_tree(page_src, url)
        res = []
        for child in document.iter():
            list_max, total_words = list_range(child)
            if len(list_max) > 2:
                res.append(ListArea(list_max, child, total_words / len(list_max)))
        res.sort(key=lambda x: len(x.links), reverse=True)
        return res[idx].print_list()


if __name__ == '__main__':
    path_list, parent = ListArea.find_list(url='https://stock.cngold.org/gundong', idx=5)
    print("列表区域:{}\n".format(parent))
    for content, link, xpath in path_list:
        print("title: {}\nurl:   {}\nxpath: {}\n".format(content, link.get('href'), xpath))
