#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: WeiXin
'''

from tkinter import *
from tkinter import ttk
from re_bdwk import *

# 定义下载功能
def download():
    try:
        if not  user_input_url is None:
            url = user_input_url.get()
            docType = BaiduWk(url).doctype
            info_text.insert(END, docType)
    except:
        info_text.insert(END, "ERROR:URL有误，请重新输入\n")

    if not docType is None:
        info_text.insert(END, "\n---->类型为：%s" %docType)
    #print("类型为", "-->", docType)

    if docType == "ppt":
        try:
            ppt = WKPpt(url)
            info_text.insert(END, "\n---->要获取的PPT名称为：%s" % ppt.title)
            #page = ppt.get_url()
            #page_lenth = len(page)
            # for p in page_lenth:
            #     info_text.insert(END,"\n正在下载第%s，共%s页" %(p,page_lenth))
            ppt.get_ppt_images()
            info_text.insert(END, "\n---->已经保存为：%s" % ppt.title)
            info_text.insert(END, "\n========================")
            #print("您将要获取的演示文稿(ppt)名称为:", ppt.title)
        except:
            info_text.insert(END, "\n---->收费文档暂时无法下载")

    elif docType == "doc":
        word = WKDoc(url)
        #print("您将要获取的文档(word)名称为", word.title)
        info_text.insert(END, "\n---->要获取的word文档名称为：%s" % word.title)
        pure_addr_list = word.get_doc_urls()
        word.get_save_doc_content(pure_addr_list)
        info_text.insert(END, "\n---->已经保存为：%s" % word.title)
        info_text.insert(END, "\n========================")


    elif docType == "txt":

        txt = WKTxt(url)
        info_text.insert(END, "\n---->要获取的txt文档名称为：%s" % txt.title)
        info_text.insert(END, "\n---->已经保存为：%s" % txt.title + '.txt')
        txt.get_txt()
        info_text.insert(END, "\n========================")

    else:
        other = WKPpt(url)
        info_text.insert(END, "---->暂不支持下载%s类型：%s" % other.title)
        info_text.insert(END, "\n========================")
        pass



#设置tkinter窗口
root = Tk()
root.title("文库Downloader")
# 设置窗口大小
root.geometry('494x500')

user_input_url = StringVar()
op_message = StringVar()
nothing= StringVar()


#设置主框架
download_frame = ttk.Frame(root, width=494, height=150, borderwidth=3,
                      relief='raised').pack(side='top')
# 设置下载地址和下载按钮框架
#download_frame = ttk.Frame(mainframe).pack(side="top")
# label
tip_label = ttk.Label(download_frame, text="请输入下载url:", font=10,
                      )
tip_label.place(x=20,y=30)
    # 输入框
entry = ttk.Entry(download_frame, show=None, width=50,
                  textvariable=user_input_url)
entry.place(x=15,y=60)
    # 下载按钮
button = ttk.Button(download_frame, text="下载", command=download,
                    )
button.place(x=380,y=58)
copyright_label1 = ttk.Label(download_frame, text="Copyright By Wx", font=10)
copyright_label2 = ttk.Label(download_frame, text="www.wwxin.club", font=10)
copyright_label3 = ttk.Label(download_frame, text="仅限交流使用 请勿非法用途", font=10)
copyright_label1.place(x=295,y=95)
copyright_label2.place(x=295,y=120)
copyright_label3.place(x=15,y=120)
# 设置信息框和进度条
info_frame = ttk.Frame(root, width=494, height=350, borderwidth=3,
                      relief='groove').pack(side='bottom')
# 消息输出框label
info_label = ttk.Label(info_frame, text="输出情况:", font=10)
info_label.place(x=20,y=160)


# 消息输出框text
info_text = Text(info_frame, width=65, height=20)
info_text.place(x=15, y=180)

root.mainloop()

