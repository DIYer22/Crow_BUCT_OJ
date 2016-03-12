# -*- coding: utf-8 -*-
"""
Created on Wed Dec 30 22:49:43 2015

@author: yl
"""

#如果你尝试看源代码 奉劝一句：编码问题很恶心,解决它花了很多代码。。。。

#==============================================================================
#待解决：
#1.qq截图 名字带中文的没法下载
#
#==============================================================================


from __future__ import unicode_literals

import re,os
import urllib2
from bs4 import BeautifulSoup
import webbrowser

CONST_MAX_PAGE = 17  # 开发的时候 一共有 17 页问题
FULL_VIEW_TAG = 0  # 0 为摘要模式 1 为全局模式
RAW_URL = 'http://coder.buct.edu.cn:8088/JudgeOnline/problemset.php?page='

class NoneError(Exception):
    pass

def download(url):
    if url is None:
        return None
    try:
        response = urllib2.urlopen(url)
    except :
        return None

    if response.getcode() !=200:
        return None
    if url[-4:].lower() == '.jpg' or url[-4:].lower() == '.png' or url[-4:].lower() == '.gif':
        return response.read()
    return response.read().decode('utf-8')


def get_page_url(page = 17):

    l = range(page)
    global RAW_URL
    url = RAW_URL
    def f(x):
        global RAW_URL
        url = RAW_URL
        return url + str(x+1)
    l = map(f, l)
    return l



def get_cont(d):
    req = download(d['url'])
    soup = BeautifulSoup(req, 'html.parser', from_encoding='utf-8')
    div = soup.find('div', id="main")

    div = str(div).decode('utf-8')
    if 'class="content"' not in div:
        raise NoneError

#==============================================================================
# 所用替换，处理规则
#==============================================================================

    div = div.replace('src="/JudgeOnline/','src="').replace('</pre>', '</div>').replace('<pre', '<dvi').replace('nobr', 'div')
    div = re.sub(re.compile(r'width:.+?;')            , 'width:auto;', div)
    div = re.sub(re.compile(r'<div id="foot">[\S\s]+?end foot-->'), ' ', div)
    div = re.sub(re.compile(r'<title>.+?</h2>.+?</h2>'), ' ', div)

    soup_div = BeautifulSoup(div, 'html.parser', from_encoding='utf-8')

    content = soup_div.find('div', class_="content")
    txt = content.get_text()

    content = str(content).decode('utf-8')


    download_thing(content, d['url'], r'(?:src|href) ?= ?["\']?[\./]?[^ "\'>]+?\.(?:jpg|gif|png|JPG|GIF|PNG)')
    d['script_short'] = txt
    d['script'] = content
    d['cont'] = div
    global RAW_URL
    d['upload'] = RAW_URL + d['id']

def save(d):
    f = open('BUCT OJ.html', 'a')
    row = d['row']
    url = os.path.dirname(d['url']) + '/'
    url = 'href=\'' + url
    row = row.replace('href=\'',url )
    row = '<tr class="row"><td><table><tbody>'+ row +'</tbody></table></td></tr>'

    f = open('BUCT OJ.html', 'a')
    f.write(row.encode('utf-8'))

    write = d['script']

    global FULL_VIEW_TAG
    if FULL_VIEW_TAG == 1:
        write = d['cont']
    f.write(('<tr class="script"><td style="width:900px"> %s <br></td></tr>'% write).encode('utf-8'))
    f.close()

def download_thing(content, url, pa=r'(?:src|href) ?= ?["\']?[\./]?[^ "\'>]+?\.(?:jpg|png|gif|css)'):

    ''' content:网页内容  url:当前地址 pa:正则 '''
    pa = re.compile(pa)
    l = re.findall(pa, content)

    #oj 项目专用代码
#    l = filter(lambda x :0 if x[-8:]=='logo.png' else 1, l)

    if l == []:
        return
    print l
    raw_url = re.search(r'http:.+/', url).group()
    def save_img(scr, raw_url):
        path = re.search(r'= *["\']?(.+?\.(?:jpg|png|gif|css|JPG|PNG|GIF|CSS))', scr).group(1)
        if path[0] == '.':
            path = path[2:]
        img = download(raw_url + path)
        try:
            if '\\' in path or '/' in path and not os.path.isdir(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))


            f = open(path ,'wb')
            f.write(img)
            f.close()
        except:
            return


    for scr in l:
        save_img(scr, raw_url)

def save_page(page_url):
    req = download(page_url)
    pa = re.compile(r"<tr class='\w{3}\w?row'><td>.+?</a></div></td></tr>")
    l = re.findall(pa, req)
    def dic(x):
        d = {}
        d['row'] = x.replace('<td>\t<div class=none> </div></td>','')
        soup = BeautifulSoup(x, 'html.parser', from_encoding='utf-8')
        name = soup.find('a', href=re.compile(r"problem\.php\?id=\d+"))
        d['name'] = name.get_text()
        d['id'] = name['href'][-4:]
        global RAW_URL
        d['url'] = os.path.dirname(RAW_URL) + '/' +name['href']
        print 'crow:',d['url']
        try:
            get_cont(d)
        except NoneError:
            print d['id']+'is NULL!'
            d['script'] = d['id']+'is NULL!'
            d['cont'] = '<h2>'+d['id']+'is NULL!'+'/<h2>'
            d['upload'] = ''
            return '<h2>'+d['id']+'is NULL!'+'/<h2>'
        save(d)
        return x
    l  = map(dic, l)
    return l



html_head = """
<html>
<head>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
	<title>BUCT OJ by 小磊</title>

<style>
a {
    color: #1A5CC8;
    text-decoration: none;
}
a:hover {
    color: orange;
    text-decoration: underline;
}
h2 {
    color: blue;
}


.toprow a:hover {
    color: orange;
    font-family: Arial;
    font-size: 18px;
    font-weight: bold;
    margin: 15px;
}
.oddrow {
    background-color: #E5ECF9;
    white-space: nowrap;
}
.evenrow {
    background-color: #E5ECF9;
    white-space: nowrap;
}
body {
    background-color: #FFFFFF;
    background-image: url("image/background.jpg");
    font-family: "Microsoft YaHei";
}

span.exadmin {
    color: gray;
}
.center,#center {
	width:100px;
    text-align: center;
    color: withe;
}
.script {
    background: none repeat scroll 0 0 #E4F0F8;
    font-family: Times New Roman;
    font-size: 20px;
    line-height: 24px;
    height: auto;
    margin: 0;
    padding: 0 20px;
    text-align: left;
    white-space:normal;

}
.left {
	width:411px;
    text-align: left;
    color: white;
}
div.content {
    background: none repeat scroll 0 0 #E4F0F8;
    font-family: Times New Roman;
    font-size: 20px;
    line-height: 24px;
    height: auto;
    margin: 0;
    padding: 0 20px;
    text-align: left;
    white-space:normal;
}




.sampledata {
    background: none repeat scroll 0 0 #8DB8FF;
    font-family: Monospace;
    font-size: 18px;
    white-space: pre;
}

</style>
</head>
<body>
<br>
<h1 align="center"><a href="https://github.com/DIYer22/Crow_BUCT_OJ">BUCT OJ</a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<h1>
<h3 align="center">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;by&nbsp;小磊<h3>
<div id="main">
<table id='problemset' class='table'  align="center">
<tbody>
<tr class="row"><td><table><tbody>
<tr class='evenrow'><td>	<div class='center'>编号</div></td><td>	<div class='left' style="color: black";>名称</div></td><td>
<div class='center'><nobr>来源</nobr></div ></td><td>	<div class='center'>提交</div></td><td>	<div class='center'>通过</div></td><td>	<div class='center'>难度</div></td></tr>
</tbody></table></td></tr>

"""


###############################################################################
#                 main()
###############################################################################

print u'\n\n          BUCT OJ 信息聚合爬虫 v0.10\n\
                     by UCE 小磊\n\n'
print u'请将爬虫放入一个新的文件夹下，爬虫将会把爬取的图片和HTML放到此文件夹内\n\n\
按"c"键继续，"g"键获取源代码与更新，"q"键退出！'


a = raw_input()
while a=='g':
    webbrowser.open('https://github.com/DIYer22/Crow_BUCT_OJ')
    print '按"c"键为摘要模式，"g"键获取源代码与更新，"q"键退出！'
    a = raw_input()
if a != 'c':
    if a == 'a':
        FULL_VIEW_TAG = 1
    else:
        quit()
print '\n正在获取数据....\n\n'

f = open('BUCT OJ.html', 'w')
f.write(html_head.encode('utf-8'))
f.close()


l = get_page_url(CONST_MAX_PAGE)


for url in l:
    save_page(url)


f = open('BUCT OJ.html', 'a')
f.write("</tbody></table></div></body></html>")
f.close()


webbrowser.open('BUCT OJ.html')
print u'\n\n\n\n已经在此文件夹成功保存了HTML及其图片,请按任意键退出！\n\n'
a = raw_input()




