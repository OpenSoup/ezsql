# ezsql
这是一个用于简化sqlite的操作的工具包，您可以像操作python中的列表(数组)一样操作您的sqlite  

如果您的设备已安装pip,您可以打开命令行，并使用以下代码进行安装：  
```
pip install --trusted-host 114.115.172.126 -i http://114.115.172.126:3141/simple/ ezsql
```
随后在python代码开始处加入：
```python
from ezsql import*
```
即可正常使用该工具包
您可以像这样操作您的sqlite：
```python
from ezsql import *

conn = connect("test.db")  # 链接sqlite文件
cursor = EzCursor(conn)    # 创建光标

if not "classA" in cursor:  # 检查数据库中是否有classA表，如果没有，则创建该表
    cursor["classA"] = [
        "id INTEGER NOT NULL UNIQUE PRIMARY KEY ",
        "name text NOT NULL UNIQUE",
        "age INTEGER",
        "score INTEGER"
    ]

print(cursor)  # 输出整个数据库

cursor["classA"].mk_row(name="mike", age=12, score=98)  # 放入同学mike的信息

print(cursor)

conn.commit()
conn.close()
```
