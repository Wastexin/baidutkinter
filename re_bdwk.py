#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: WeiXin
'''

import os
from bs4 import BeautifulSoup
import re
import json
import requests
import chardet

#创建基类
class BaiduWk():
    def __init__(self, url):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/70.0.3538.110 Safari/537.36',
            'charset':'gb2312'
        }
        self.url = url
        self.title = None
        self.doctype = None
        self.get_response_sources(self.url)
        self.get_doctype()
        self.get_title()

    def get_response_sources(self, url):
        #异常处理
        try:
            response = requests.get(url, headers=self.headers)
            #返回二进制文件content，text 再尝试
            return response.content
        except Exception:
            print(Exception)
            pass

    def get_title(self):
        try:
            # 获取网页源代码
            html = self.get_response_sources(self.url)
            # 解析源码
            content = html.decode('gbk')
            # 使用beautifulsuop库进行解析
            soup = BeautifulSoup(content, 'lxml')
            #print(soup.title.string)
            # 获取文档标题
            self.title = soup.title.string
            return self.title
        except:
            pass


    def get_doctype(self):
        try:
            # 获取网页源代码
            html = self.get_response_sources(self.url)
            # 解析源码
            content = html.decode('gbk')
            # 使用正则表达式进行解析
            # 获取文档标题
            self.doctype = re.findall(r"docType.*?\:.*?\'(.*?)\'\,",
                                      content)[0] #非贪婪匹配  .*?非贪婪匹配 \, 匹配逗号
                                                  # 括号中（.*?）为匹配的东西
            #print(re.findall(r"docType.*?\:.*?\'(.*?)\'\,", content)[0])
            #print(self.doctype)
        except:
            pass

class WKPpt(BaiduWk):
    def __init__(self, url):
        super().__init__(url)
        self.images_url_list = list()
        self.ppt_url = None
        self.pptID = None

    def get_ppt_ID(self):
        #获取网页源代码
        ppt_html = self.get_response_sources(self.url)
        #解析源码
        content = ppt_html.decode('gbk')
        #使用正则表达式进行解析
        self.pptID = re.findall(r"docId.*?(\w{24}?)\'\,", content)[0]
        return self.pptID

    def get_url(self):
        #获取ID
        self.get_ppt_ID()
        #获取PPT列表的url
        ppt_images_url = 'https://wenku.baidu.com/browse' \
                         '/getbcsurl?doc_id=%s&type=ppt&' \
                         'callback=wx' % self.pptID
        self.ppt_url = ppt_images_url
        return self.ppt_url

    def get_ppt_images(self):
        # 获取url
        self.get_url()
        # 获取源码
        ppt_source_html = self.get_response_sources(self.ppt_url).decode()
        # 获取字符串类型的json数据
        #ppt_images_json = ppt_source_html.decode()
        # 使用正则表达式匹配需要的东西
        ppt_url_str = re.match(r'.*?\((.*?)\)', ppt_source_html).group(1)  # group(0)是原字符串
                                                                # group(1)之后是正则之后获取的列表
        # 将str转换成dict
        #ppt_url_list = ppt_url_str.strip(',').split(',')
        ppt_url_dict = json.loads(ppt_url_str)

        # 遍历获得的dict
        # 建立临时列表保存url
        for url in ppt_url_dict['list']:
            tem_url_list = list()
            # 将image_url 和 image_page 保存到临时列表中
            tem_url_list.append(url['zoom'])
            tem_url_list.append(url['page'])
            # 再将临时列表保存到self.images_url_list中
            # 将每个image的url和page当做一个元素保存在其中
            self.images_url_list.append(tem_url_list)

        # 保存文件
        try:
            os.makedirs("./ppt/%s" % self.title)
        except Exception as e:
            pass
            #print(e)

        length = len(self.images_url_list)
        for image_url in self.images_url_list:
            #print("一共%d页，正在下载第%d页。") % (image_url['page'], length)
            ppt_image = self.get_response_sources(image_url[0])
            path = './ppt/%s/%s_%d%s' % (self.title, self.title, image_url[1], '.jpg')
            with open(path, 'wb') as  f:
                f.write(ppt_image)
        #print("下载完成")


class WKDoc(BaiduWk):
    def __init__(self, url):
        super().__init__(url)
        # 用列表保存网站源代码中的url
        self.doc_url_list = list()

    def get_doc_urls(self):
        # 获取网站源代码,返回response.content
        doc_source_html = self.get_response_sources(self.url)
        # 进行解码
        #print(chardet.detect(doc_source_html))
        doc_html_content = doc_source_html.decode('unicode_escape') #Unicode解码中文
        # 使用正则表达式获取源码中的doc_url(一系列json请求的代码)
        all_url = re.findall(r'wkbjcloudbos\.bdimg\.com.*?json.*?Expire.*?\}', doc_html_content)
        url_list = list()
        # 获取doc_title
        self.title = self.get_title()
        # 对all_url中的进行处理,将获得的url存入url_list中
        for url in all_url:
            url = "https://" + url.replace("\\\\", "")
            url_list.append(url)
        # 将url_list保存到self.doc_url_list中
        self.doc_url_list = url_list
        return self.doc_url_list

    def get_save_doc_content(self, url_list):
        #self.get_doc_urls()
        doc_content = ""
        #temp_content = ""
        #从url_list中开始下载
        for url in url_list:
            try:
                # 获取source_html
                # 使用unicode_escape进行Unicode解码
                html_content = self.get_response_sources(url[:-2]).decode()
                # print(html_content) 'unicode_escape'
                # 使用正则表达式进行选择
                content = re.match(r'.*?\((.*)\)$', html_content).group(1)
                # 将获得的str转成dict
                all_body_info = json.loads(content)
                for body_info in all_body_info["body"]:
                    try:
                        # 从all_body_info中逐条获取数据
                        if type(body_info["c"]) == dict:
                            continue
                        doc_content = doc_content + body_info["c"].strip()
                        #doc_content = doc_content + body_info["c"]
                        # 是否可以保持格式
                    except Exception as e:
                        #print(e)
                        pass
            except Exception as e:
                pass
                #print(e)
        # doc_content = doc_content.encode()
        # doc_content = doc_content.decode('GBK')
        doc_content.encode('gbk')
        # print(doc_content)
        # 创建目录进行保存
        try:
            path = "./doc/%s" % self.title
            os.makedirs(path)
        except:
            pass
        #创建文件保存
        try:
            filename = self.title + '.txt'
            with open("./doc/%s/%s" %(self.title, filename), 'w', encoding="gbk") as f :
                f.write(doc_content)
            #print(f.encoding)
        except:
            pass





class WKTxt(BaiduWk):
    def __init__(self, url):
        super().__init__(url)
        self.txtID = None

    def get_txt(self):
        # 获取网页源代码
        txt_html = self.get_response_sources(self.url)
        # 解析源码
        content = txt_html.decode('gbk')
        # 使用正则表达式进行解析
        self.txtID = re.findall(r"docId.*?(\w{24}?)\'\,", content)[0]
        # 拼接url
        pre_txt_url = "https://wenku.baidu.com/api/doc/getdocinfo?callback=cb&doc_id=" + self.txtID
        # 再次请求
        first_json = self.get_response_sources(pre_txt_url).decode()
        str_first_json = re.match(r'.*?\((\{.*?\})\).*', first_json).group(1)
        # print(str_first_json)
        the_first_json = json.loads(str_first_json)
        md5sum = the_first_json["md5sum"]
        rn = the_first_json["docInfo"]["totalPageNum"]
        rsign = the_first_json["rsign"]
        # 请求目标url
        target_url = "https://wkretype.bdimg.com/retype/text/" + self.txtID \
                     + "?" + md5sum + "&callback=cb" + "&pn=1&rn=" + rn \
                     + "&type=txt" + "&rsign=" + rsign


        sec_json = self.get_response_sources(target_url).decode('GBK')
        str_sec_json = re.match(r'.*?\(\[(.*)\]\)$', sec_json).group(1)
        str_sec_json += ","
        str_json_list = str_sec_json.split('},')
        result_txt = ""
        # 截取尾部空格
        str_json_list = str_json_list[:-1]
        for str_json in str_json_list:
            str_json += "}"
            pure_dic = json.loads(str_json)
            pure_txt = pure_dic["parags"][0]["c"].strip()
            result_txt += pure_txt

        # 创建文件目录
        try:
            path = "." + os.sep + self.doctype
            os.makedirs(path)
        except Exception as e:
            pass
        # 创建文件,保存信息
        try:
            file_name = "." + os.sep + self.doctype + os.sep + self.title + ".txt"
            with open(file_name, 'w') as f:
                f.write(result_txt)
                #
        except Exception as e:
            # print(e)
            pass


# def main():
#     try:
#         url = input("请输入资源所在的网址:")
#         docType = BaiduWk(url).doctype
#     except:
#         print("您输入的url,有误请重新输入!")
#
#     print("类型为", "-->", docType)
#
#     if docType == "ppt":
#
#         ppt = WKPpt(url)
#         print("您将要获取的演示文稿(ppt)名称为:", ppt.title)
#         ppt.get_ppt_images()
#
#     elif docType == "doc":
#         word = WKDoc(url)
#         print("您将要获取的文档(word)名称为", word.title)
#         pure_addr_list = word.get_doc_urls()
#         word.get_save_doc_content(pure_addr_list)
#
#     elif docType == "pdf":
#         pdf = WKDoc(url)
#         print("您将要获取的PDF名称为:", pdf.title)
#         pure_addr_list = pdf.get_doc_urls()
#         pdf.get_save_doc_content(pure_addr_list)
#
#     elif docType == "txt":
#
#         txt = WKTxt(url)
#         print("您将要下载的文本文档(txt)名称为:", txt.title)
#         txt.get_txt()
#
#     else:
#         other = WKPpt(url)
#         print("暂不支持下载%s类型" % (other.doctype))
#         pass
#
#
# if __name__ == '__main__':
#     main()
#

url = "https://wenku.baidu.com/view/064d03e40975f46527d3e1e4.html?from=search"
# https://wenku.baidu.com/view/5987d426f78a6529647d53ac.html?from=search
# https://wenku.baidu.com/view/50037a0e4a7302768e9939f2.html?from=search
# https://wenku.baidu.com/view/064d03e40975f46527d3e1e4.html?from=search
# https://wenku.baidu.com/view/ab0e72dd3968011ca200912b.html?from=search
# doc = WKDoc(url)
# # doc.get_doc_urls()
# # doc.get_save_doc_content(doc.doc_url_list)
# # for url in doc.doc_url_list:
# #     print(url)