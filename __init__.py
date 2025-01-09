"""
一个用于在sqlite数据库中进行简单操作的方法库，可以将数据库光标转换为一个可迭代数据类型，进行便利、数据查找、数据增减等。如果您不需要对数据库进
行过于复杂的操作，那么这个库将会是个很好的选择。
"""
from sqlite3 import *

from hardType import *


class SQBool:
    """
    数据库布尔类型，用于生成数据库布尔条件代码
    """
    def __init__(self, left, symbol, right):
        """
        初始化类，创建该类时调用
        :param left:   被运算项
        :param symbol: 运算符
        :param right:  运算项
        """
        if symbol not in [">", "<", "=", ">=", "<=", "!=", "&", "|", "+", "-", "*", "/"]:
            raise SyntaxError(f"unknown symbol: {symbol}")
        self.left = left
        self.symbol = symbol
        self.right = right

    def __gt__(self, other):
        return SQBool(self, ">", other)

    def __lt__(self, other):
        return SQBool(self, "<", other)

    def __eq__(self, other):
        return SQBool(self, "=", other)

    def __ge__(self, other):
        return SQBool(self, ">=", other)

    def __le__(self, other):
        return SQBool(self, "<=", other)

    def __ne__(self, other):
        return SQBool(self, "!=", other)

    def __and__(self, other):
        return SQBool(self, "&", other)

    def __or__(self, other):
        return SQBool(self, "|", other)

    # ==========加========== #
    def __add__(self, other):
        return SQBool(self, "+", other)

    def __radd__(self, other):
        return SQBool(other, "+", self)

    # ==========减========== #
    def __sub__(self, other):
        return SQBool(self, "-", other)

    def __rsub__(self, other):
        return SQBool(other, "-", self)

    # ==========乘========== #
    def __mul__(self, other):
        return SQBool(self, "*", other)

    def __rmul__(self, other):
        return SQBool(other, "*", self)

    # ==========除========== #
    def __truediv__(self, other):
        return SQBool(self, "/", other)

    def __rtruediv__(self, other):
        return SQBool(other, "/", self)

    # ====================== #
    def __str__(self):
        b = bool_in_sql(self)
        return f"{b[0]}\n{b[1]}"


class EzCursor:
    """
    简化光标，让光标可以像python中的字典一样操作。
    """
    def __init__(self, conn: Connection):
        """
        初始化类，创建该类时调用
        :param conn: 调用该类时传入的数据库连接
        """
        check_type(conn, "conn", Connection)

        self.conn = conn
        self.cursor = conn.cursor()

    def __getitem__(self, item):
        """
        获取简化数据表，可以这样调用：EzCursor[item]
        :param item: 数据表名称
        :return: 简化数据表
        """
        return EzList(self, item)

    def __setitem__(self, key, value):
        """
        给数据库添加数据表，可以这样调用：EzCursor[key] = value
        :param key:   表名
        :param value: 表头信息，格式：["{list_head1} {other_args}", "{list_head2} {other_args}", ...]
        :return: None
        """
        # 创建sql语句
        sql_command = f"CREATE TABLE IF NOT EXISTS {key} (\n"
        sql_command += f"    {value[0]},\n"

        for column in value[1:]:
            sql_command += f"    {column},\n"

        sql_command = sql_command.rstrip(',\n')

        sql_command += "\n);"

        # 如果已有该表，删除该表
        self.cursor.execute(f"DROP TABLE IF EXISTS {key};")

        # 创建表
        self.cursor.execute(sql_command)

    def __iter__(self):
        """
        创建该类的迭代器，让数据库可迭代
        :return: 迭代器
        """
        return self.ls_table().__iter__()

    def __contains__(self, item):
        """
        判断数据库中是否有某个表，可以这样调用：item in EzCursor
        :param item: 数据表名称
        :return: 是否有该表的布尔值
        """
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (item,))
        return self.cursor.fetchone() is not None

    def __str__(self):
        """
        可视化整个数据库(使用时需注意，数据量大时会很消耗性能)
        :return:
        """
        r = ""
        for table in self.ls_table():
            r += f"\n\n====={table}=====\n"
            r += str(self[table])
        return r

    def ls_table(self) -> list:
        """
        创建所有数据表名称的列表
        :return: 所有数据表名称的列表
        """
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = self.cursor.fetchall()
        return [i[0] for i in tables]

    def rm_table(self, *tables):
        """
        删除一个或多个表
        :param tables: 要删除的所有表的表名
        :return: None
        """
        for table in tables:
            self.cursor.execute(f"DROP TABLE {table};")

    get_table = __getitem__

    mk_table = __setitem__


class EzList:
    """
    简化数据表，让数据表可以像python中的字典一样操作
    """
    def __init__(self, ez_cursor: EzCursor, table: str):
        """
        初始化类，创建该类时调用
        :param ez_cursor: 该表所属于的光标
        :param table:     表名
        """
        check_type(ez_cursor, "ez_cursor", EzCursor)
        check_type(table, "table", str)

        self.ez_cursor = ez_cursor
        self.conn = self.ez_cursor.conn
        self.cursor = self.ez_cursor.cursor
        self.table = table
        if self.table not in self.ez_cursor:
            raise IndexError(f"no such table: {table}")

    def __getitem__(self, item):
        """
        获取一列，可以这样调用：EzList[item]
        :param item: 需要获取列内容的表头
        :return: 列方法类
        """
        return Column(self, item)

    def __iter__(self):
        """
        创建该类的迭代器，让数据库可迭代
        :return: 迭代器
        """
        return self.ls_column().__iter__()

    def __len__(self):
        """
        获取该表的列数
        :return: 该表的列数
        """
        return len(self.ls_column())

    def __contains__(self, item):
        """
        判断表格中是否含有某表头，可以这样调用：item in EzCursor
        :param item: 表头名称
        :return: 是否有该表头的布尔值
        """
        self.cursor.execute(f"SELECT name FROM pragma_table_info('{self.table}')")
        column_list = [row[0] for row in self.cursor.fetchall()]
        return item not in column_list

    def __str__(self):
        """
        列表可视化(使用时需注意，数据量大时会很消耗性能)
        :return: 由字符串组成的列表
        """
        return str(RowMatcher(self, True))

    def ls_column(self) -> list:
        """
        列出所有表头
        :return: 所有表头的列表
        """
        self.cursor.execute(f"SELECT name FROM pragma_table_info('{self.table}')")
        column_list = [row[0] for row in self.cursor.fetchall()]
        return column_list

    def mk_column(self, *columns):
        """
        添加一列或多列
        :param columns: 所有列名以及其他关于此列的参数
        :return: None
        """
        for column in columns:
            self.cursor.execute(f"ALTER TABLE {self.table} ADD COLUMN {column};")

    def rm_column(self, *columns):
        """
        删除一列或多列
        :param columns: 所有要删除的列名
        :return: None
        """
        for column in columns:
            self.cursor.execute(f"ALTER TABLE {self.table} DROP COLUMN {column};")

    def mk_row(self, **items):
        """
        添加一行
        :param items: 该行中的所有数据，格式：{head1: item1, head2: item2, ...}
        :return: None
        """
        first = True
        code = f"INSERT INTO {self.table} ("
        for i in items:
            if first:
                code += i
                first = False
            else:
                code += f", {i}"
        code += ")\nVALUES ("
        first = True
        for i in items:
            if first:
                code += "?"
                first = False
            else:
                code += f", ?"
        code += ")"
        self.cursor.execute(code, [items[i] for i in items])

    get_column = __getitem__


class Column:
    """
    列方法类
    """
    def __init__(self, ez_list: EzList, head: str):
        """
        初始化类，创建该类时调用
        :param ez_list: 该列所属于的表格的方法类
        :param head:    表头名称
        """
        check_type(ez_list, "ez_list", EzList)
        check_type(head, "head", str)

        self.ez_list = ez_list
        self.ez_cursor = self.ez_list.ez_cursor
        self.conn = self.ez_cursor.conn
        self.cursor = self.ez_cursor.cursor
        self.head = head

    def __gt__(self, other):
        return SQBool(self, ">", other)

    def __lt__(self, other):
        return SQBool(self, "<", other)

    def __eq__(self, other):
        return SQBool(self, "=", other)

    def __ge__(self, other):
        return SQBool(self, ">=", other)

    def __le__(self, other):
        return SQBool(self, "<=", other)

    def __ne__(self, other):
        return SQBool(self, "!=", other)

    def __and__(self, other):
        return SQBool(self, "&", other)

    def __or__(self, other):
        return SQBool(self, "|", other)

    # ==========加========== #
    def __add__(self, other):
        return SQBool(self, "+", other)

    def __radd__(self, other):
        return SQBool(other, "+", self)

    # ==========减========== #
    def __sub__(self, other):
        return SQBool(self, "-", other)

    def __rsub__(self, other):
        return SQBool(other, "-", self)

    # ==========乘========== #
    def __mul__(self, other):
        return SQBool(self, "*", other)

    def __rmul__(self, other):
        return SQBool(other, "*", self)

    # ==========除========== #
    def __truediv__(self, other):
        return SQBool(self, "/", other)

    def __rtruediv__(self, other):
        return SQBool(other, "/", self)

    # ====================== #

    def __contains__(self, item):
        """
        判断列中是否有某个元素，可以这样调用：item in Column
        :param item: 判断是否在列中的元素
        :return: 是否有该元素的布尔值
        """
        self.cursor.execute(f"SELECT COUNT(*) FROM {self.ez_list.table} WHERE {self.head} = ?",
                            (item,))
        return self.cursor.fetchone()[0] > 0

    def __getitem__(self, item):
        """
        获取用于匹配特定行的，可以这样调用：Column[item]
        :param item: 匹配的内容
        :return: 行方法类
        """
        return RowMatcher(self.ez_list, (self == item))

    def __iter__(self):
        """
        创建该类的迭代器，让数据库可迭代
        :return: 迭代器
        """
        return self.ls_item().__iter__()

    def __len__(self):
        """
        获取该列的长度，可以这样调用：len(Column)
        :return: 长度
        """
        self.cursor.execute(f"SELECT COUNT(*) FROM {self.ez_list.table};")
        return self.cursor.fetchone()[0]

    def __setitem__(self, key, value):
        """
        覆盖指定内容，可以这样调用：Column[key] = value
        :param key:   被覆盖的内容(被匹配的所有项目都将被覆盖)
        :param value: 替换成的内容
        :return: None
        """
        self.cursor.execute(f"UPDATE {self.ez_list} SET {self.head} = {value} WHERE {self.head} = {key}")

    def __str__(self):
        """
        列出该列的所有内容(使用时需注意，数据量大时会很消耗性能)
        :return: 该列所有内容的字符串
        """
        r = f"{self.head}\n\n"
        for i in self.ls_item():
            r += f"{i}\n"
        return r

    def ls_item(self):
        """
        列出该列所有数据
        :return: 所有数据的列表：[item1, item2, ...]
        """
        self.cursor.execute(f"SELECT {self.head} FROM {self.ez_list.table};")
        items = self.cursor.fetchall()
        return [i[0] for i in items]


class RowMatcher:
    """
    用于匹配行的方法类
    """
    def __init__(self, ez_list: EzList, match_bool):
        """
        初始化类，创建该类时调用
        :param ez_list:    该行所属于的表格的方法类
        :param match_bool: 用于匹配元素的布尔运算式
        """
        check_type(ez_list, "ez_list", EzList)

        self.ez_list = ez_list
        self.ez_cursor = self.ez_list.ez_cursor
        self.conn = self.ez_cursor.conn
        self.cursor = self.ez_cursor.cursor
        self.bool = match_bool

    def __getitem__(self, item):
        """
        获取所有被匹配行中特定列的内容，可以这样调用：RowMatcher[item]
        :param item: 特定列的表头名称
        :return: 获取到的内容，格式：[item1, item2, ...]
        """
        sql_bool = bool_in_sql(self.bool)
        code = f"SELECT {item} FROM {self.ez_list.table} WHERE {sql_bool[0]}"
        self.ez_cursor.cursor.execute(code, sql_bool[1])
        fetch_list = self.ez_cursor.cursor.fetchall()
        return [i[0] for i in fetch_list]

    def __iter__(self):
        """
        创建该类的迭代器，让该行可迭代
        :return: 迭代器
        """
        return RowMatcherIter(self)

    def __len__(self):
        """
        获得被匹配行的数量
        :return: 被匹配行的数量
        """
        sql_bool = bool_in_sql(self.bool)
        code = f"SELECT COUNT(*) FROM {self.ez_list.table} WHERE {sql_bool[0]}"
        self.cursor.execute(code, sql_bool[1])
        return self.cursor.fetchone()[0]

    def __setitem__(self, key, value):
        """
        将所有被匹配行中的特定列替换为特定元素，可以这样调用：RowMatcher[key] = value
        :param key:   要替换的特定列
        :param value: 替换成的值
        :return: None
        """
        sql_bool = bool_in_sql(self.bool)
        code = f"UPDATE {self.ez_list.table} SET {key} = {value} WHERE {sql_bool[0]}"
        self.cursor.execute(code, sql_bool[1])

    def __str__(self):
        """
        将可被self.static_items匹配的列表可视化
        :return: 由字符串组成的列表
        """
        r = ""
        max_len = 0
        for i in self.ez_list.ls_column():
            if len(i) > max_len:
                max_len = len(i)
        for i in range(len(self)):
            for head in self.ez_list.ls_column():
                item = str(self[head][i])
                if len(item) > max_len:
                    max_len = len(item)
        r += "|"
        for i in self.ez_list.ls_column():
            r += "{:<{m}}|".format(i, m=max_len)
        list_width = len(r)
        r += f"\n{'='*list_width}\n"
        r = f"\n{'-'*list_width}\n"+r
        for i in range(len(self)):
            r += "|"
            for head in self.ez_list.ls_column():
                r += "{:<{m}}|".format(self[head][i], m=max_len)
            r += "\n"
        r += f"{'-'*list_width}\n"
        return r

    def rm_all(self):
        """
        删除所有被匹配项
        :return: None
        """
        sql_bool = bool_in_sql(self.bool)
        code = f"DELETE FROM {self.ez_list.table} WHERE {sql_bool[0]}"
        self.cursor.execute(code, sql_bool[1])


class RowMatcherIter:
    """
    用于匹配行的方法类的迭代类，当便利类RowMatcher时(像这样：for i in RowMatcher)，将会使用该类。
    便利中每次循环i都会为一列中所有被匹配项。
    """
    def __init__(self, row_matcher: RowMatcher):
        """
        初始化类，创建该类时调用
        :param row_matcher: 行的方法类
        """
        self.row_matcher = row_matcher
        self.keys = row_matcher.ez_list.ls_column()
        self.count = 0

    def __next__(self):
        """
        获取下一列中所有被匹配项(如果第一次调用，则获得第一列)
        :return: 当前列所有被匹配项，格式：[item1, item2, ...]
        """
        if self.count < len(self.keys):
            r = self.row_matcher[self.keys[self.count]]
            self.count += 1
            return r
        else:
            raise StopIteration


def bool_in_sql(item):
    """
    将SQBool类型转换为sqlite条件代码，并返回带“?”的sqlite条件代码和对应的参数列表

    :param item: 需要转换的SQBool实例或其他数据类型
    :return: 一个元组，包含sqlite条件代码字符串和填在“?”处的参数列表
    """
    sql_args = []
    if isinstance(item, SQBool):
        # 递归处理左右两边
        left = bool_in_sql(item.left)
        right = bool_in_sql(item.right)

        sql_args = left[1]+right[1]

        # 处理运算符，将&和|转换为AND和OR
        if item.symbol in ["&", "|"]:
            operator = "AND" if item.symbol == "&" else "OR"
            return f"({left[0]} {operator} {right[0]})", sql_args
        else:
            # 其他符号直接使用
            return f"({left[0]} {item.symbol} {right[0]})", sql_args
    elif isinstance(item, Column):
        return item.head, []
    else:
        # 其他类型可能需要特殊处理，这里简单返回字符串表示
        return "?", [item]


if __name__ == '__main__':
    db_file_path = input("pls enter path to your sqlite:")
    conn = connect(db_file_path)
    cursor = EzCursor(conn)
    while True:
        py_code = input(">")
        if py_code[0] == "/":
            if py_code[1:] in ["exit", "quit", "stop"]:
                conn.commit()
                conn.close()
                break
        else:
            try:
                print(eval(py_code))
            except BaseException as BE:
                try:
                    repr(BE)
                    exec(py_code)
                except BaseException as BE:
                    print(f"Error: {repr(BE)}")
                    YorN = None
                    while YorN not in ["Y", "y", "N", "n"]:
                        YorN = input("show full error and stop?(Y/n)")
                    if YorN in ["Y", "y"]:
                        raise BE
