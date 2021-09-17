## 蛋卷基金投资记录

获取蛋卷基金的投资记录然后记录到[google表格](https://docs.google.com/spreadsheets/d/1vwOBl9kjaLrvZdcfjdNPkd0Bwz66qJyPD-qLUkt2sms/edit?usp=sharing)
。

### 依赖的包

* github地址：https://github.com/burnash/gspread
* 文档地址：https://docs.gspread.org/en/latest/
* 开通google表格的访问权限：https://docs.gspread.org/en/latest/oauth2.html

### 如何使用

0. [开通google表格的访问权限](https://docs.gspread.org/en/latest/oauth2.html) 并且把需要修改的google sheet表格共享给此邮箱
1. 安装python3.8环境，并安装本项目的依赖`pip install -r requirements.txt`
2. 修改cookie.example.txt文件为cookie.txt
3. 在网页上登陆[蛋卷基金](https://danjuanapp.com/)
4. 登陆之后复制[蛋卷基金](https://danjuanapp.com/)
   的cookie信息（ [如何查看cookie](https://jingyan.baidu.com/article/76a7e409284a80fc3a6e1566.html) ）并粘贴到cookie.txt文件中
5. 默认写入的google表格的名称为"投资记录"，sheet页为"基金投资详情"，可以在util.google_sheet_util.py文件中修改
6. 运行main.py脚本`python3.8 main.py`;（注意需连外网）

