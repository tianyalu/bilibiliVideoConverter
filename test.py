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


if __name__ == '__main__':
    test()