# -*- encoding: utf-8 -*-
'''
Filename         :aLittleEpub.py 
Description      :用于制作图片epub文件，简而言之就是把图片打包成epub文件
Time             :2022/02/02 13:20:22
Author           :Konoha
Version          :1.0 
Environment      :python 3.9.0    Pillow 9.0.0
'''

import os
import shutil

import tkinter as tk            #tkinter 制作简约的GUI界面
from tkinter import filedialog  #文件目录选择窗口

from random import sample#用于随机生成uuid
from _thread import start_new_thread#用于多线程，否则Consolo和tkinter界面无法同时刷新内容

from time import strftime,localtime,sleep#用于获得今日日期
from PIL import Image#用于获得封面图片的尺寸



class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        #设置退出前的操作函数
        master.protocol("WM_DELETE_WINDOW", self.beforeQuit)
        self.master = master
        self.pack()        #创建各个窗口组件        
        
        
        #初始化各项数据
        self.uuid = ""
        self.img_directory = ""#图片路径
        self.coverImgName = ""
        self.mode = 'offprint'
        self.imgs = []#图片文件的名称

        self.quick_flag = False
        self.subdirs = []#如果选择的文件夹下有很多子文件夹，那么对这些子文件夹进行一一快速制作（标题默认为子文件夹名称，封面默认为子文件夹下第一张图片）。
        
        self.chapterList = []#章节的列表，放列表里方便增删查改
        self.cptIndexRbtList = []#章节按钮的组件，放列表里好管理
        self.ncx_chapContent = []#toc_ncx的内容，先放list里，后续在写入
        self.toc_chapContent = []#扉页toc的内容，同上
        
        #初始化目录路径
        self.OEBPS_dir = r"temp/OEBPS/"
        self.Images_dir = r"temp/OEBPS/Images/"
        self.Text_dir = r"temp/OEBPS/Text/"

        print(">>>aLittleEpub 准备就绪...")

        self.create_widgets()
        # os.system("echo %cd%")
        # self.initNewBook()

    #创建各个窗口组件
    def create_widgets(self):
        # 获取文件
        self.bt_chooseBookDir = tk.Button(self,font=('黑体', 16),width=20,height=1,text='选择目录',command=self.getImgDirectory)        
        self.bt_chooseBookDir.pack(side="top") 
        
        self.label_title = tk.Label(self,text="书名",anchor="w",width=55,font=('黑体', 14)).pack()
        self.et_title=tk.Entry(self,show=None, width=50,font=('黑体', 16))
        self.et_title.pack()
        self.et_title.insert(0,"")

        self.label_creator = tk.Label(self,text="作者",anchor="w",width=55,font=('黑体', 14)).pack()
        self.et_creator=tk.Entry(self,show=None, width=50,font=('黑体', 16))
        self.et_creator.pack()
        self.et_creator.insert(0,"")

        self.label_language = tk.Label(self,text="语言",anchor="w",width=55,font=('黑体', 14)).pack()
        self.et_language=tk.Entry(self,show=None, width=50,font=('黑体', 16))
        self.et_language.pack()
        self.et_language.insert(0,"")

        self.label_date = tk.Label(self,text="日期",anchor="w",width=55,font=('黑体', 14)).pack()
        self.et_date=tk.Entry(self,show=None, width=50,font=('黑体', 16))
        self.et_date.pack()
        self.et_date.insert(0,strftime("%Y-%m-%d", localtime()))

        self.bt_chooseCover = tk.Button(self,text="选择封面",font=('黑体', 16),width=20,height=1,command=self.chooseCover).pack(side="bottom")
        
        self.chapterCount = -1#章节计数器，初始为-1。

        self.chap_NO = tk.IntVar()
        self.chap_NO.set(-1)




        #add new chapter button
        self.bt_chooseChapterIndex = tk.Button(self,text="增加章节",font=('黑体', 16),width=20,height=1,command=self.addChapter).pack()
        
        #默认增加6个章节按钮，用户可以增加
        for i in range(6):
          self.addChapter()

    #增加章节按钮，章节按钮可以选择某一页为章节定位    
    def addChapter(self):
      
      #如果是第一个章节按钮
      if self.chapterCount==-1:
        self.chapterCount += 1
        self.chapterList.append(tk.Entry(self,show=None,width=50,font=('黑体', 15),\
          validate="focusout",validatecommand=self.recursion))    
        self.chapterList[self.chapterCount].pack()
        self.chapterList[self.chapterCount].insert(0,f"chapter{self.chapterCount+1}")
      else:
        self.chapterCount += 1
        self.chapterList.append(tk.Entry(self,show=None, width=50,font=('黑体', 15)))    
        self.chapterList[self.chapterCount].pack()
        self.chapterList[self.chapterCount].insert(0,f"chapter{self.getNextNO()}")
        #自动获取下一个章节的序号

      
      #增加选择按钮
      self.cptIndexRbtList.append(tk.Radiobutton(self,text=f"选择章节{self.chapterCount+1}",variable = self.chap_NO,value=self.chapterCount,\
        indicatoron=False,anchor="w",width=50,font=('黑体', 14),\
        command=lambda:self.chooseChapter(self.chap_NO.get())))
      self.cptIndexRbtList[self.chapterCount].pack()
      
      self.ncx_chapContent.append("")
      self.toc_chapContent.append("")

      #如果目录数大于8个，达到了9个，则自动缩小字体，否则不够空间
      if self.chapterCount >= 8:
        for eachChapter,eachIndex in zip(self.chapterList,self.cptIndexRbtList):
          eachChapter.config(font=('黑体', 8))
          eachIndex.config(font=('黑体', 8))

    #依次得到章节序号
    def recursion(self):
      
      chapStr = self.chapterList[0].get()
    
      try:
        if len(chapStr) <= 12 and chapStr[:7] == "chapter":
          try:
            NO = int(chapStr[7:])
          except BaseException:
            return True
          self.cptIndexRbtList[0]['text'] = f"选择章节{NO}"
          for eachChapter,eachIndex in zip(self.chapterList[1:],self.cptIndexRbtList[1:]):
            NO += 1
            eachChapter.delete(0, 'end')
            eachChapter.insert(0,f"chapter{NO}")
            eachIndex['text'] = f"选择章节{NO}"
            
            
      except BaseException as e:
        # print(e)
        pass
      finally:
        return True
    
    #自动获取下一个章节序号的子函数
    def getNextNO(self):
      lastNO = self.chapterList[self.chapterCount-1].get()
      if lastNO[:7] == "chapter":
        return int(lastNO[7:])+1
      else:
        return self.chapterCount+1

    #到此前期准备完毕，接下来是等待用户选择图片目录


    #一旦选择了目录后，进行创建书本的初始化工作,连续制作多本书籍的时候也需要再进行一次初始化。
    def initNewBook(self):
        """
        @description  : 初始化书籍信息
        ---------
        @param  : this
        -------
        @Returns  : None
        -------
        """

        #初始化各项数据
        self.uuid = ""
        self.img_directory = ""#图片路径
        self.coverImgName = ""
        self.mode = 'offprint'
        self.imgs = []#图片文件的名称

        self.subdirs = []#如果选择的文件夹下有很多子文件夹，那么对这些子文件夹进行一一快速制作（标题默认为子文件夹名称，封面默认为子文件夹下第一张图片）。
        
        self.chapterList = []#章节的列表，放列表里方便增删查改
        self.cptIndexRbtList = []#章节按钮的组件，放列表里好管理
        self.ncx_chapContent = []#toc_ncx的内容，先放list里，后续在写入
        self.toc_chapContent = []#扉页toc的内容，同上
        
        #初始化目录路径
        self.OEBPS_dir = r"temp/OEBPS/"
        self.Images_dir = r"temp/OEBPS/Images/"
        self.Text_dir = r"temp/OEBPS/Text/"

        #获取uuid
        self.uuid = self.createUUID()
        
        #写出各个数据的开头部分
        #初始化NCX
        self.toc_ncx = f'''<?xml version='1.0' encoding='utf-8'?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta content="urn:uuid:{self.uuid}" name="dtb:uid"/>
    <meta content="0" name="dtb:depth"/>
    <meta content="0" name="dtb:totalPageCount"/>
    <meta content="0" name="dtb:maxPageNumber"/>
  </head>
  <docTitle>
    <text>Unknown</text>
  </docTitle>
  <navMap>
'''

        #扉页目录table of contents
        self.TOC = '''<?xml version='1.0' encoding='utf-8'?>
<html xmlns="http://www.w3.org/1999/xhtml">

<head>
  <style>
        div.sgc-toc-title {
        font-size: 2em;
        font-weight: bold;
        margin-bottom: 1em;
        text-align: center;
      }
      div.sgc-toc-level-1 {
        margin-left: 0;
      }
      div.sgc-toc-level-2 {
        margin-left: 2em;
      }
      div.sgc-toc-level-3 {
        margin-left: 2em;
      }
      div.sgc-toc-level-4 {
        margin-left: 2em;
      }
      div.sgc-toc-level-5 {
        margin-left: 2em;
      }
      div.sgc-toc-level-6 {
        margin-left: 2em;
      }
  </style>
  <title>Table of Contents</title>
</head>

<body>

  <div class="sgc-toc-title">Table of Contents</div>

'''

        #contents.opf文件的开头部分，包含版本信息
        self.opfHead = ""

        #清单
        self.manifest = '''  <manifest>
\t<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
\t<item id="cover.xhtml" href="Text/cover.xhtml" media-type="application/xhtml+xml"/>
'''
        #主心骨，用于指定各个文件摆放的顺序
        
        self.spine = '''  <spine toc="ncx">
\t<itemref idref="cover.xhtml"/>
'''
        #主心骨的图片引用部分
        self.spine_itemrefPart = ''
        self.manifest_itemrefPart = ''



    def createUUID(self) -> str:
        #UUID样例urn:uuid:7f9dda2f-ec04-4309-a7d8-3eb7e0c609c8
        #8-4-4-4-12
        strSet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        p1 = ''.join(sample(strSet,8))
        p2 = ''.join(sample(strSet,4))
        p3 = ''.join(sample(strSet,4))
        p4 = ''.join(sample(strSet,4))
        p5 = ''.join(sample(strSet,12))
        return f"{p1}-{p2}-{p3}-{p4}-{p5}"
        # return "H4LtYCw9-IlHo-uRlG-jXLv-hLx6b1dFlApJ"



    #用户选择图片目录,起始点
    def getImgDirectory(self):
        # #初始化
        # self.initNewBook()

        #如果用户已经选过一次了，但是发现选错了，此时可以再选一次，而优先选择上次的那个目录
        if self.img_directory != "" :
          initdir = os.path.dirname(self.img_directory)
          self.img_directory = str(tk.filedialog.askdirectory(title=u'选择文件',initialdir=os.path.normpath(initdir)))
        else:#调取上一本书的目录
          with open("configution/configution.cfg",'r',encoding='utf-8') as cfg:
            initdir = cfg.read()
          self.img_directory = str(tk.filedialog.askdirectory(title=u'选择文件',initialdir=os.path.normpath(initdir)))
          
        #用户取消选择
        if self.img_directory == "":
            return               
        
        print("getDirectory: "+self.img_directory)

        #将本次选择的目录的父目录写入cfg文件中，以便下次读取，根据空间局部性，用户很可能会将很多目标文件夹放在一个目录下。
        with open("configution/configution.cfg",'w',encoding='utf-8') as cfg:
          cfg.write(os.path.dirname(self.img_directory))

        
        
        self.quick_flag = False
        self.subdirs.clear()

        for dir in os.listdir(self.img_directory):
          # print(dir)
          if os.path.isdir(self.img_directory+os.sep+dir):
            self.quick_flag = True
            print(f"检测到目录 : {dir}")
            self.subdirs.append(self.img_directory+os.sep+dir)
        # print(self.subdirs)

        if self.quick_flag:
          print("即将进入快速制作书籍模式")
          sleep(3)
        else:
          self.subdirs.clear()
          self.subdirs.append(self.img_directory)



        for subdir in self.subdirs:
          #初始化
          self.initNewBook()

          self.img_directory = subdir

          self.et_title.delete(0,'end')
          if self.quick_flag:
            self.et_title.insert(0,self.img_directory[self.img_directory.rfind(os.sep)+1:])
          else:
            self.et_title.insert(0,self.img_directory[self.img_directory.rfind("/")+1:])

          #生成目录结构，复制两个固定文件
          # start_new_thread(self.createDirectoryTree,())
          self.createDirectoryTree()
        
        if self.quick_flag:
          print("\n\n>>>快速制作完成<<<\n\n")

    #生成目录结构
    def createDirectoryTree(self):
                
        #无论什么原因，只要temp目录还存在，则必须删除旧的temp。usecase：用户上次选错了目录，或者用户连续制作好几本书。
        if os.path.exists("temp/"):
            os.system("rmdir /s/q temp")

        #这个复制的时候会自动生成目录
        # shutil.copytree("resources/","temp/")
        os.system("xcopy /si resources temp")
        print(">>>epub框架部署完毕")
        
        if not os.path.exists(self.Text_dir):
          os.makedirs(self.Text_dir)
        if not os.path.exists(self.Images_dir):
          os.makedirs(self.Images_dir)
        
        try:
          imgDir = self.img_directory.replace("/","\\")
          os.system(f'copy "{imgDir}" temp\\OEBPS\\Images')
          print(">>>图片文件导入完毕")
          
          count_chapter = 0
          for filename in os.listdir(self.Images_dir):
              if '00001' == filename[-9:-4] :
                count_chapter += 1
              os.rename(self.Images_dir+filename,f'{self.Images_dir}{count_chapter:0>3d}{filename[-9:]}')
        except BaseException as e:
          print(str(e))
          print("\n!!!请确保文件夹下只有图片文件!!!")
          sleep(4)
          return
            
        print(">>>图片文件重命名完毕")

        self.createXHTML()
        print(">>>opf_ncx构建完毕")

    #创建TEXT目录下的XHTML文件
    def createXHTML(self):     
        count_chapters = 1
        img = ""

        

        #遍历图片文件夹
        for img in os.listdir(self.Images_dir):                     
            #将图片文件纳入manifest清单
            imgType = 'jpeg'
            if img[-3:]=='png':
                imgType = 'png'
            self.manifest_itemrefPart += f'''\t<item id="x{img}" href="Images/{img}" media-type="image/{imgType}"/>
'''
            # print(">>>Img {}引用成功".format(newname))

            #最后生成xhtml文件
            


            html_content = '''<?xml version='1.0' encoding='utf-8'?>
<html xmlns="http://www.w3.org/1999/xhtml">

<head>
  <style>
    img, div{
    width:100%;
    max-width: 100%;
    display: block;
    }
  </style>'''
            html_content += f'''
  <title>page_{count_chapters}</title>
</head>

<body>

  <div style="text-align: center; padding: 0pt; margin: 0pt;">

    <img src="../Images/{img}" alt="Images to epub"/>

  </div>

</body>

</html>'''
            
            #xhtml内容write to文件
            htmlFileName = f'page{img}.xhtml'
            htmlFilePath = self.Text_dir+htmlFileName
            count_chapters += 1
            with open(htmlFilePath,'w',encoding='utf-8') as file_object:
                file_object.write(html_content)
            # print(">>>XHTML {}生成成功".format(htmlFilePath))


            #将xhtml文件纳入manifest清单
            self.manifest_itemrefPart += f'''\t<item id="{htmlFileName}" href="Text/{htmlFileName}" media-type="application/xhtml+xml"/>
'''


            #主心骨结构
            self.spine_itemrefPart += f'''\t<itemref idref="{htmlFileName}"/>
'''                
        #至此，结束for循环

        # if self.mode == 'anthology':
        #   self.chooseCover()
        if self.quick_flag:
          self.chooseCover()

        

    def chooseChapter(self,count:int = 1):
      
      filedialog_title = "选择章节"
      chapterIndexPath = filedialog.askopenfilename(title = filedialog_title,multiple=False,\
          initialdir = self.Images_dir,filetypes=[("图片文件",('.jpg','.png')),('All Files', '*')])
      if chapterIndexPath=="":
          return
      chapterIndexImgName = chapterIndexPath[chapterIndexPath.rfind("/")+1:]

      self.cptIndexRbtList[count].config(bd=5,fg='gold')
      
      chapter = self.chapterList[self.chap_NO.get()].get()
      
      print(f"选择章节目录[{chapter}]---{chapterIndexImgName}")

      #主目录
      self.ncx_chapContent[count] = f'''    <navPoint id="navPoint-{count+1}" playOrder="{count+1}">
      <navLabel>
        <text>{chapter}</text>
      </navLabel>
      <content src="Text/page{chapterIndexImgName}.xhtml"/>
    </navPoint>

'''
#count+1是因为那边是从0开始算的（list的下标
                
      #TOC目录
      self.toc_chapContent[count] = f'''  <div class="sgc-toc-level-1">
  <a href="page{chapterIndexImgName}.xhtml">{chapter}</a>
</div>
'''
      

    def chooseCover(self):
        
        try:
          if self.quick_flag:
            self.coverImgName = os.listdir(self.Images_dir)[0]
            coverImg_FullPath = self.Images_dir + os.sep + self.coverImgName
          else:
            filedialog_title = "选择封面图片"
            coverImg_FullPath = filedialog.askopenfilename(title = filedialog_title,multiple=False,\
              initialdir = self.Images_dir,filetypes=[("图片文件",('.jpg','.png')),('All Files', '*')])
            if coverImg_FullPath=="":
                return
            # coverImgPath = "D:/##resource/##getPic/autoEpub/temp/OEBPS/Images/10001001.jpg"
            self.coverImgName = coverImg_FullPath[coverImg_FullPath.rfind("/")+1:]#从路径中取文件名
        except IOError as fne:
          print("!!!上一本(批)书籍的制作已经完成,无需进一步操作!!!\n!!!或者您正在制作一本新的书籍，则请先选择目录(最上面的按键)!!!")
          return

        #添加章节
        isTOC = False
        for eachTOC,eachNCX in zip(self.toc_chapContent,self.ncx_chapContent):
          if eachTOC!="":
            isTOC = True
            self.TOC += eachTOC
            self.toc_ncx += eachNCX
        #收尾
        self.TOC += '''
</body>

</html>'''
        self.toc_ncx += '''  </navMap>\n</ncx>'''

        #如果用户没有选择任何目录，那么不需要生成TOC.xhtml文件
        if isTOC:
          with open(self.Text_dir+"TOC.xhtml",'w',encoding='utf-8') as opf:
                  opf.write(self.TOC)
        with open(self.OEBPS_dir+"toc.ncx",'w',encoding='utf-8') as opf:
            opf.write(self.toc_ncx)

        
        img = Image.open(coverImg_FullPath)
        coverWidth = img.size[0]
        coverHeight = img.size[1]
        img.close()

        coverXHTML_content = f'''<?xml version='1.0' encoding='utf-8'?>
<html xmlns="http://www.w3.org/1999/xhtml">

<head>
  <title>Cover</title>
</head>

<body>

  <div style="text-align: center; padding: 0pt; margin: 0pt;">

    <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" height="100%" preserveAspectRatio="xMidYMid meet" version="1.1" viewBox="0 0 {coverWidth} {coverHeight}" width="100%">
      <image width="{coverWidth}" height="{coverHeight}" xlink:href="../Images/{self.coverImgName}"/>
    </svg>

  </div>

</body>

</html>'''



        #生成cover.xhtml文件
        with open(self.Text_dir+"cover.xhtml",'w',encoding='utf-8') as opf:
            opf.write(coverXHTML_content)

        
        #生成opf的head
        self.opfHead = f'''<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="2.0" unique-identifier="BookId">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
    <dc:title>{self.et_title.get()}</dc:title>
    <dc:creator>{self.et_creator.get()}</dc:creator>
    <dc:language>{self.et_language.get()}</dc:language>
    <dc:identifier id="BookId" opf:scheme="UUID">urn:uuid:{self.uuid}</dc:identifier>
    <dc:date opf:event="modification">{self.et_date.get()}</dc:date>
    <meta name="cover" content="x{self.coverImgName}"/>
    <meta content="1.5.1" name="Sigil version"/>
  </metadata>

''' 
        #opf文件的清单和骨架收尾部分的结尾
        if isTOC:
          self.spine += '\t<itemref idref="TOC.xhtml"/>\n'
          self.manifest += '\t<item id="TOC.xhtml" href="Text/TOC.xhtml" media-type="application/xhtml+xml"/>\n'        
        
        self.spine += self.spine_itemrefPart
        self.manifest += self.manifest_itemrefPart
        self.spine += "  </spine>\n\n"    
        self.manifest += "  </manifest>\n\n" 

        self.opfHead += self.manifest
        self.opfHead += self.spine

        #opf文件的guide部分
        addTOC = ''
        if isTOC:
          addTOC = '<reference type="toc" title="Table of Contents" href="Text/TOC.xhtml"/>'
        self.opfHead += f'''  <guide>
    <reference type="cover" title="Cover" href="Text/cover.xhtml"/>
    {addTOC}
  </guide>
  
</package>
        '''
        
        with open(self.OEBPS_dir+"content.opf",'w',encoding='utf-8') as opf:
            opf.write(self.opfHead)
        print(">>>content.opf生成")

        print(">>>准备完毕，开始打包")
        
        if self.quick_flag:
          pass
        baseName = self.et_title.get()
        outputDir = os.path.dirname(self.img_directory)
        
        epubFileName = self.et_title.get()+'.epub'
        outputDir = os.path.dirname(self.img_directory)
        
        cmd_7z = f'cd temp && ..\\configution\\7z.exe a "{epubFileName}" -mmt16'
        print(cmd_7z)
        os.system(cmd_7z)

        cmd_mv_rm = f'move /Y "temp\\{epubFileName}" "{outputDir}" && rmdir /s/q temp'
        # _thread.start_new_thread(os.system,(cmd_mv_rm,))
        os.system(cmd_mv_rm)

        print(f">>>{epubFileName}制作完成！\n epub保存路径:{outputDir}")
        print("-----------finish-----------")
        
    def beforeQuit(self):
      if os.path.exists("temp/"):
        # shutil.rmtree("temp/")
        os.system("rmdir /s/q temp")
      super().quit()
        
             
if __name__ == '__main__':
    root = tk.Tk()
    root.title("aLittleEpub  |  by Konoha")
    # root.geometry("500x400+650+300")
    root.geometry("%dx%d+%d+0" %(root.winfo_screenwidth()/2,root.winfo_screenheight(),root.winfo_screenwidth()/2))
    app =  Application(master=root)
    try:
        app.mainloop()
    except BaseException:
        pass
    finally:
        app.beforeQuit()

