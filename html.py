item_size = 4


def find_link(node):
    """
    :param node:
    :return: 该Element的子节点中最长的<a></a>对象
    """
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
        return None, ''
    else:
        return max_link, max_link_content


def is_same_style(node1, node2):
    """
    :param node1:比较节点1
    :param node2: 比较节点2
    :return: 判断节点1和节点2是否有相同的xpath结构
    """
    if node1.tag != node2.tag:
        return False
    if node1.tag == 'div':
        return node1.get('class') == node2.get('class')
    return True


def list_range(node):
    """
    :param node: Element对象
    :return: 该Element的子节点中最长的list结构
    """
    children = node.getchildren()
    if len(children) < item_size:
        return [], 0
    _, max_link_content = find_link(children[0])

    last = children[0]
    total_words = len(max_link_content)
    max_len = 0
    cur_len = 1
    start_idx = 0

    for i in range(1, len(children)):
        _link, max_link_content = find_link(children[i])
        if _link is None:
            last = children[i]
            cur_len = 1
            total_words = 0
            continue

        if is_same_style(children[i], last):
            cur_len += 1
            total_words += len(max_link_content)
            if cur_len > max_len:
                max_len = cur_len
                start_idx = i - cur_len + 1
        else:
            last = children[i]
            cur_len = 1
            total_words = len(max_link_content)

    return children[start_idx:start_idx + max_len], total_words


def list_merge(node):
    """
    将node元素的子元素根据标签类型进行合并，并检查是否包含链接
    :param node:
    :return:
    """
    child_map = {}
    words_map = {}
    children = node.getchildren()
    if len(children) < item_size:
        return [], 0
    for child in children:
        tag = child.tag
        _link, max_link_content = find_link(child)
        if _link is None:
            continue
        else:
            words_map[tag] = words_map.get(tag, 0) + len(max_link_content)
        child_map.setdefault(tag, []).append(child)
    if len(child_map) > 0:
        sorted_items = sorted(child_map.items(), key=lambda x: len(x[1]), reverse=True)
        tag, lis = sorted_items[0]
        if len(lis) < item_size:
            return [], 0
        if tag == 'div' and not same_keys(lis):
            return [], 0
        return lis, words_map[tag]
    else:
        return [], 0


def same_keys(lis):
    key = lis[0].keys()
    cla = lis[0].get('class')
    for child in lis:
        if child.keys() != key:
            return False
        if child.get('class') != cla:
            return False
    return True
