from lxml import etree

# XML 数据
xml_data = '''
<bookstore>
  <book category="cooking">
    <title lang="en">Everyday Italian</title>
    <author>Giada De Laurentiis</author>
    <year>2005</year>
    <price>30.00</price>
    <book category="cooking">
      <title lang="en">Everyday Italian222</title>
      <author>Giada De Laurentiis222</author>
      <year>2005</year>
      <price>30.00</price>
    </book>
  </book>
  <book category="children">
    <title lang="en">Harry Potter</title>
    <author>J.K. Rowling</author>
    <year>2005</year>
    <price>29.99</price>
    <book category="children">
      <title lang="en">Harry Potter2222</title>
      <author>J.K. Rowling2222</author>
      <year>2005</year>
      <price>29.99</price>
    </book>
  </book>
</bookstore>
'''


def parse_xml_data():
    # 解析XML数据
    root = etree.fromstring(xml_data)  # 将 XML 字符串解析为 XML 元素对象

    # 遍历并输出每本书的标题和作者
    for book in root.xpath('//book'):  # // 是用来表示从当前节点开始的递归匹配，否则只会匹配当前节点的子节点或直接子孙节点
        title = book.xpath('title')[0].text
        author = book.xpath('author')[0].text
        print(f'Title: {title}, Author: {author}')


if __name__ == '__main__':
    # print('PyCharm hhah哈哈哈 ')
    parse_xml_data()
