# encoding=utf8
import math


def round_floor(num, scale):
    """
    向下四舍五入
    :param num:    需要处理的数字
    :param scale:  保留的有效数字位数
    :return: 向下四舍五入之后的数字
    """
    multiplier = 10 ** scale
    return math.floor(num * multiplier) / multiplier


def round_floor_by_min(num, min_num):
    """
    根据最小的数值将num进行向下四舍五入
    :param num:     需要处理的数字
    :param min_num: 最小数
    :return: 向下四舍五入之后的数字
    """
    # 获取min_num有多少位小数
    le = len(str(min_num)[str(min_num).find(".") + 1:])
    # 截取num，长度为小数点前的所有数字加le的长度
    return float(str(num)[:len(str(num)[:str(num).find(".")]) + le + 1])
