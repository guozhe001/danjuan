import os
from pathlib import PurePosixPath

# 项目主目录
project_path = PurePosixPath(os.path.abspath(__file__)).parent.parent


# 投资文件的文件名
class FundFileName:
    fund_info_file_name = "fund_info.csv"
    fund_file_name = "fund.csv"
