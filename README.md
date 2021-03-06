## 轻型epub制作脚本，仅支持图片打包 by Konoha
（如果单纯只想打包图片，其实打包成PDF也是很不错的，足够简单足够稳定）[PDFMaker](https://github.com/KonohaVio/PDFMaker)

### 找到【##aLittleEpub.exe】，双击启动
### 推荐【##aLittleEpub.exe】右键生成快捷方式，把快捷方式放到你喜欢的地方

----源代码文件【##aLittleEpub_v1.01.py】可在python环境下运行，具体环境可见源代码文件开头部分。
----若要单独运行源文件，应将【configution】和【resources】这两个文件夹与源代码放在同一文件夹下，其他文件均可抛弃。

##### 准备工作：将一本书的所有图片放在一个文件夹下，并保证顺序正确。(##rename.exe可以重命名图片以确保顺序)

1. 选择目录，选择要打包的图片所在的文件夹，默认会将其所有文件一起打包，如果有非图片文件可能会导致出错。
2. 书名必填，剩下作者，语言，日期，章节目录均为选填。章节不够可以增加，但有上限。
3. 选择章节，制作目录，此时建议在弹出的窗口右上角切换为大图模式，更方便选择。
4. 选择封面，在此之前的数据都可以更改，但是一旦选择了封面并确定，则会同时完成整个制作流程，打包好的epub文件放在图片目录的上一级目录。
5. 批量制作：目前因tkinker框架受限，无法同时选择对个文件夹。只能将要批量制作的文件夹再放到一个文件夹下，然后在软件中选择这个文件夹，即可批量制作。此时书籍名默认为各个子文件夹的名称，封面默认为各个子文件夹下第一张图片。
#### 一些注意事项：

##### 最好不要放C盘
##### 暂不支持jpg和png以外的图片格式
##### 选择的图片文件夹内尽量都是待打包的图片
##### iPad推荐阅读器KyBook3（免费版）
##### 竖屏滚动推荐使用eBoox
##### 可以尝试更多的阅读器，以满足你的阅读习惯。
##### 软件或许仍有诸多bug，可以的话请联系我

##### py源代码环境：python 3.7.0--3.9.0   &&   pip3 install Pillow 9.0.0
##### 源代码的运行只需要同目录下有configuration和resources这两个文件夹即可

### ##rename.exe效果如下
![image](https://user-images.githubusercontent.com/61352919/169464274-6d22eb43-a411-4c81-9c35-067863ddfd12.png)


### 制作的书籍经Calibre等专业ePub软件检测合格
![image](https://user-images.githubusercontent.com/61352919/152534630-fd571b11-eb4a-4047-a5f0-19f1427bbd37.png)
![image](https://user-images.githubusercontent.com/61352919/152534996-1aa2ec1a-8a03-4cf7-80c5-74c3b718bbe6.png)
![image](https://user-images.githubusercontent.com/61352919/152534952-a26a59df-c07c-40a3-9876-0d1950c4daed.png)

## -
### iPad横屏模式下双页效果图（kybook3免费版）效果良好
![VNIJNY0K 6(@0E1T(N0K(7D](https://user-images.githubusercontent.com/61352919/152537687-7b94162c-7a13-4169-bdf9-85a3e74b0981.jpg)
### iPad竖屏模式下单页效果 (kybook3免费版) 几乎全屏铺满
![9TTOX5GQLD9L_F7_86~ L26](https://user-images.githubusercontent.com/61352919/152537971-d3c281ab-64c8-4dfe-bb0c-87294ae94178.jpg)
### 竖屏滚动模式下的效果图 (eboox阅读器) 上下两张图片拼接缝隙（间距）较小
![QQ图片20220204023916](https://user-images.githubusercontent.com/61352919/152408465-7753d482-c4bf-49bd-9971-c0f3ef1b4566.png)
