import os
import re
def reFilter(SourceStr: str, filter_re: str = r""):
    result = SourceStr
    it = re.finditer(filter_re, SourceStr, re.S)
    for match in it: 
        num = match.group()
        result = result.replace(num,f'{int(num):0>5d}')
    return result 

      
filter = r'[0-9]+'
dir = input("请输入目录(文件夹)的路径(对文件夹按住shift,右键,再按A即可快速复制路径) : ")
for i in os.listdir(dir if dir[0] != '\"' else dir[1:-1]):
    newName = reFilter(i,filter)
    os.rename(dir+os.sep+i,dir+os.sep+newName)

input(f"\n\n文件重命名完毕。\n>>>按任意键或右上角退出")