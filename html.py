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
    if node1.tag != node2.tag or node1.keys() != node2.keys():
        return False
    if 'class' in node1.keys() and node1.get('class') != node2.get('class'):
        return False
    if find_link(node1)[0] is None or find_link(node2)[0] is None:
        return False
    return True


def list_range(node):
    """
    :param node: Element对象
    :return: 该Element的子节点中最长的list结构
    """
    children = node.getchildren()
    if len(children) < 3:
        return [], 0
    _, max_link_content = find_link(children[0])

    last = children[0]
    total_words = len(max_link_content)
    max_len = 0
    cur_len = 1
    start_idx = 0

    for i in range(1, len(children)):
        _, max_link_content = find_link(children[i])
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
    return children[start_idx:start_idx + max_len - 1], total_words
