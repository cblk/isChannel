import lxml.html as lh
import requests


def get_xpath(xpath, url):
    r = requests.get(url)
    r.encoding = r.apparent_encoding
    document = lh.fromstring(r.text)
    return document.xpath(xpath)


if __name__ == '__main__':
    doc = get_xpath('/html/body/div[6]/div[2]/div[3]/div/div/div[3]/div/ul',
                    'https://epaper.gmw.cn/gmrb/html/2020-03/16/nbs.D110000gmrb_01.htm')[0]
    print(doc.xpath('string(.)').strip())

