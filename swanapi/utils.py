def check_elements_in_list(A, B):
    set_B = set(B)
    for element in A:
        if element not in set_B:
            return False
    return True


def bytes_encoder(obj):
    """
    对图像字节流进行编码
    """
    if isinstance(obj, bytes):
        return obj.decode('utf-8')  # 将字节流转换为字符串
    raise TypeError("Object of type {} is not JSON serializable".format(type(obj)))


def is_float(value):
    """
    判断是否为浮点数
    """
    try:
        float(value)
        return True
    except ValueError:
        return False


def is_list(value):
    """
    判断是否为列表，并返回转为后的字典
    """
    list_obj = eval(value)
    assert isinstance(list_obj, list), "输入的类型与定义的list类型不一致"
    return list_obj


def is_dict(value):
    """
    判断是否为字典，并返回转为后的字典
    """
    dict_obj = eval(value)
    print(dict_obj, type(dict_obj))
    assert isinstance(dict_obj, dict), "输入的类型与定义的dict类型不一致"
    return dict_obj