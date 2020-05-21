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


def is_same_tag(node1, node2):
    tag1 = None
    tag2 = None
    if node1 is not None:
        tag1 = node1.tag
    if node2 is not None:
        tag2 = node2.tag
    return tag1 == tag2


def is_same(node1, node2):
    attr1 = node1.attrib
    attr2 = node2.attrib
    for key in attr2:
        if key not in attr1:
            return False
    return is_same_tag(node1, node2) and is_same_tag(node1.getparent(), node2.getparent()) and (
            is_same_tag(node1.getnext(), node2.getnext()) or is_same_tag(node1.getprevious(), node2.getprevious()))


def scan_node(node):
    res = {}
    for child in node.getchildren():
        key = str(child.tag)
        res[key] = res.get(key, 0) + 1
    return res


def is_same_node(node1, node2):
    if not is_same(node1, node2):
        return False
    res1 = scan_node(node1)
    res2 = scan_node(node2)
    diff = 0
    total = 0
    for key in res1:
        diff += abs(res1[key] - res2.get(key, 0))
        total += res1[key]
    return diff / total < 0.1


def find_node(node, doc):
    res = []
    for child in doc.iter():
        if is_same_node(node, child):
            res.append(child)
    return res


def find_node2(node, doc):
    node_path = get_node_path(node)
    node_lis = [n for n in get_depth_in_tree(doc, len(node_path) - 1) if
                is_same_tag(n, node) and get_node_path(n) == node_path]
    node_lis = [n for n in node_lis if is_same_node(node, n)]
    return node_lis


def get_depth_in_tree(root, n):
    if n < 0 or root is None:
        return []
    if n == 0:
        return [root]
    res = []
    for node in get_depth_in_tree(root, n - 1):
        res.extend(node.getchildren())
    return res


def get_node_path(node):
    res = []
    while node is not None:
        res.append(str(node.tag))
        node = node.getparent()
    return res
