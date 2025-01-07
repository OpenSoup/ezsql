<h1 style="text-align: center;">ezsql</h1>

`ezsql` 是一个用于简化 SQLite 数据库操作的 Python 工具包。它允许您像操作 Python 中的列表和字典一样操作 SQLite 数据库，从而减少了编写复杂 SQL 语句的需求。如果您不需要对数据库进行过于复杂的操作，`ezsql` 将是一个非常好的选择。

## 主要功能

- **简化数据库操作**：通过封装 SQLite 的常用操作，`ezsql` 使得数据库的增删改查操作更加直观和简单。
- **类字典操作**：您可以通过类似字典的方式访问和操作数据库表，使得代码更加易读和易写。
- **自动提交和关闭连接**：在终端调试模式下，`ezsql` 会自动处理数据库连接的提交和关闭，避免因意外终止导致的文件损坏或数据丢失。
- **可视化输出**：`ezsql` 提供了可视化的数据库输出功能，方便您快速查看数据库内容。

## 安装

如果您的设备已安装 `pip`，您可以打开命令行，并使用以下代码进行安装：

```bash
pip install --trusted-host osoup.top -i http://osoup.top/simple ezsql
```

## 在脚本中调用

在您的 Python 脚本开头处添加以下代码即可正常使用该工具包：

```python
from ezsql import *
```

### 示例代码

以下是一个简单的示例，展示了如何使用 `ezsql` 操作 SQLite 数据库：

```python
from ezsql import *

conn = connect("test.db")  # 链接 SQLite 文件
cursor = EzCursor(conn)    # 创建光标

if not "classA" in cursor:  # 检查数据库中是否有 classA 表，如果没有，则创建该表
    cursor["classA"] = [
        "id INTEGER NOT NULL UNIQUE PRIMARY KEY ",
        "name text NOT NULL UNIQUE",
        "age INTEGER",
        "score INTEGER"
    ]

print(cursor)  # 输出整个数据库

cursor["classA"].mk_row(name="mike", age=12, score=98)  # 放入同学 mike 的信息

print(cursor)

conn.commit()
conn.close()
```

## 使用终端调试

### Linux

1. 使用您喜欢的编辑器编辑 `~/.bashrc`，这里以 `nano` 编辑器为例：

    ```bash
    nano ~/.bashrc
    ```

2. 在文件底部添加如下内容（其中 `path/to/your/ezsql/__init__.py` 替换为您安装 `ezsql` 的位置）：

    ```bash
    alias ezsql="python3 path/to/your/ezsql/__init__.py"
    ```

3. 随后重启终端，在终端输入以下命令即可正常使用：

    ```bash
    ezsql
    ```

4. 运行后，出现以下提示字样时输入您的 SQLite 文件位置即可对文件进行编辑：

    ```
    pls enter path to your sqlite:
    ```

5. 运行该程序时，会自动运行以下内容，无需再次手动运行：

    ```python
    conn = connect(db_file_path)
    cursor = EzCursor(conn)
    ```

6. 如调试完成，请输入 `/exit` 结束运行，**直接 `Ctrl+C` 终止运行可能会造成文件未保存成功、文件损坏等问题！**

## 注意事项

- **性能问题**：在处理大量数据时，可视化输出功能可能会消耗较多性能，请谨慎使用。
- **文件保存**：在终端调试模式下，请使用 `/exit` 命令退出程序，以确保数据库文件正确保存。
