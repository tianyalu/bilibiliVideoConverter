from lxml import etree


def test():
    html = "<div class='video-description clearfix'><h1 " \
           'class="title"><span>【温】全皮肤盛宴_(:з」∠)_你喜欢的我都有！</span></h1><div> '
    etree_html = etree.HTML(html)
    # pprint.pprint(f'etree_html --> {etree_html}')
    # nodes_with_class = etree_html.xpath("//div[@class='video-description clearfix']")
    title = etree_html.xpath('//div[@class="video-description clearfix"]/h1/span/text()')
    # pprint.pprint(f'title --> {title}')
    title = title[0] if (len(title) > 0) else '未定义的title'
    print(f'title --> {title}')


def test_slice():
    s = '1234567'
    last_4_digits = s[-4:]
    # str = s[:]  # 1234567
    # str = s[2:5]  # 345
    # str = s[:5]  # 12345
    # str = s[5:]  # 67
    # str = s[:-4]  # 123
    str = s[-6:-4]  # 23
    print(f'last_4_digits: {last_4_digits}')
    print(str)


def test_break():
    for i in range(10):
        if i == 5:
            break
        print(i)


if __name__ == '__main__':
    # test()
    # test_slice()
    # test_break()
    a = 4
    print(a**3)
