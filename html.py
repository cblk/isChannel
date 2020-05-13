item_size = 3


def find_link(node):
    """
    :param node:
    :return: 该Element的子节点中拥有最长内容的<a></a>元素，以及该元素对应的文字内容
    """
    if node.tag == 'a':
        return node, node.xpath('string(.)').strip(), True
    links = node.xpath('.//a')
    link_content_len = 0
    max_link = None
    max_link_content = ''
    for link in links:
        link_content = link.xpath('string(.)').strip()
        link_content = ''.join(link_content.split())
        if len(link_content) >= link_content_len:
            link_content_len = len(link_content)
            max_link = link
            max_link_content = link_content
    if max_link is None:
        return None, '', False
    else:
        return max_link, max_link_content, False


def list_merge(node):
    """
    将node元素的子元素根据标签类型进行合并
    :param node:
    :return:
    """
    child_map = {}
    children = node.getchildren()
    if len(children) < item_size:
        return []
    for child in children:
        tag = child.tag
        attr = child.attrib
        if tag == 'div':
            if attr.get('class') is not None:
                tag += attr.get('class')
            else:
                tag += str(attr)
        child_map.setdefault(tag, []).append(child)
    if 0 < len(child_map):
        sorted_items = sorted(child_map.items(), key=lambda x: len(x[1]), reverse=True)
        _res = []
        for tag, items in sorted_items:
            if len(items) >= item_size:
                _res.append(items)
        return _res
    else:
        return []
