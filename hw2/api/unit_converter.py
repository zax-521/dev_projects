"""
单位转换器API模块
提供各种单位转换功能
"""

import math

def convert_units(value, from_unit, to_unit, category="length"):
    """
    转换单位
    
    Args:
        value: 数值
        from_unit: 源单位
        to_unit: 目标单位
        category: 单位类别（length, weight, temperature, volume, speed, area, time, data）
    
    Returns:
        转换结果字典
    """
    # 根据类别选择转换函数
    conversion_functions = {
        'length': convert_length,
        'weight': convert_weight,
        'temperature': convert_temperature,
        'volume': convert_volume,
        'speed': convert_speed,
        'area': convert_area,
        'time': convert_time,
        'data': convert_data
    }
    
    if category not in conversion_functions:
        raise ValueError(f"不支持的单位类别: {category}")
    
    try:
        result = conversion_functions[category](value, from_unit, to_unit)
        return {
            'value': value,
            'from_unit': from_unit,
            'to_unit': to_unit,
            'converted_value': result,
            'category': category,
            'category_name': get_category_name(category)
        }
    except Exception as e:
        raise ValueError(f"单位转换失败: {str(e)}")

def convert_length(value, from_unit, to_unit):
    """长度单位转换"""
    # 转换为米（基准单位）
    to_meter = {
        'meter': 1,
        'kilometer': 1000,
        'centimeter': 0.01,
        'millimeter': 0.001,
        'mile': 1609.344,
        'yard': 0.9144,
        'foot': 0.3048,
        'inch': 0.0254,
        'nautical_mile': 1852,
        'li': 500,  # 里（中国单位）
        'zhang': 3.333,  # 丈
        'chi': 0.3333,  # 尺
        'cun': 0.03333  # 寸
    }
    
    # 从米转换
    from_meter = {k: 1/v for k, v in to_meter.items()}
    
    if from_unit not in to_meter or to_unit not in from_meter:
        raise ValueError(f"不支持的长度单位: {from_unit} 或 {to_unit}")
    
    meters = value * to_meter[from_unit]
    return meters * from_meter[to_unit]

def convert_weight(value, from_unit, to_unit):
    """重量单位转换"""
    # 转换为千克（基准单位）
    to_kilogram = {
        'kilogram': 1,
        'gram': 0.001,
        'milligram': 0.000001,
        'ton': 1000,
        'pound': 0.45359237,
        'ounce': 0.028349523125,
        'jin': 0.5,  # 斤（中国单位）
        'liang': 0.05,  # 两
        'qian': 0.005  # 钱
    }
    
    # 从千克转换
    from_kilogram = {k: 1/v for k, v in to_kilogram.items()}
    
    if from_unit not in to_kilogram or to_unit not in from_kilogram:
        raise ValueError(f"不支持的重量单位: {from_unit} 或 {to_unit}")
    
    kilograms = value * to_kilogram[from_unit]
    return kilograms * from_kilogram[to_unit]

def convert_temperature(value, from_unit, to_unit):
    """温度单位转换"""
    # 转换为摄氏度（基准单位）
    if from_unit == 'celsius':
        celsius = value
    elif from_unit == 'fahrenheit':
        celsius = (value - 32) * 5/9
    elif from_unit == 'kelvin':
        celsius = value - 273.15
    else:
        raise ValueError(f"不支持的温度单位: {from_unit}")
    
    # 从摄氏度转换
    if to_unit == 'celsius':
        return celsius
    elif to_unit == 'fahrenheit':
        return celsius * 9/5 + 32
    elif to_unit == 'kelvin':
        return celsius + 273.15
    else:
        raise ValueError(f"不支持的温度单位: {to_unit}")

def convert_volume(value, from_unit, to_unit):
    """体积单位转换"""
    # 转换为升（基准单位）
    to_liter = {
        'liter': 1,
        'milliliter': 0.001,
        'cubic_meter': 1000,
        'cubic_centimeter': 0.001,
        'gallon': 3.78541,  # 美制加仑
        'quart': 0.946353,
        'pint': 0.473176,
        'cup': 0.236588,
        'sheng': 1,  # 升（中国单位）
        'dou': 10  # 斗
    }
    
    # 从升转换
    from_liter = {k: 1/v for k, v in to_liter.items()}
    
    if from_unit not in to_liter or to_unit not in from_liter:
        raise ValueError(f"不支持的体积单位: {from_unit} 或 {to_unit}")
    
    liters = value * to_liter[from_unit]
    return liters * from_liter[to_unit]

def convert_speed(value, from_unit, to_unit):
    """速度单位转换"""
    # 转换为米/秒（基准单位）
    to_mps = {
        'mps': 1,  # 米/秒
        'kph': 0.277778,  # 千米/小时
        'mph': 0.44704,  # 英里/小时
        'knot': 0.514444,  # 节
        'mach': 340.3  # 马赫（在海平面）
    }
    
    # 从米/秒转换
    from_mps = {k: 1/v for k, v in to_mps.items()}
    
    if from_unit not in to_mps or to_unit not in from_mps:
        raise ValueError(f"不支持的速度单位: {from_unit} 或 {to_unit}")
    
    mps = value * to_mps[from_unit]
    return mps * from_mps[to_unit]

def convert_area(value, from_unit, to_unit):
    """面积单位转换"""
    # 转换为平方米（基准单位）
    to_sqm = {
        'square_meter': 1,
        'square_kilometer': 1000000,
        'square_centimeter': 0.0001,
        'square_millimeter': 0.000001,
        'hectare': 10000,
        'acre': 4046.86,
        'square_mile': 2589988.11,
        'square_foot': 0.092903,
        'square_inch': 0.00064516,
        'mu': 666.667,  # 亩（中国单位）
        'qing': 66666.7  # 顷
    }
    
    # 从平方米转换
    from_sqm = {k: 1/v for k, v in to_sqm.items()}
    
    if from_unit not in to_sqm or to_unit not in from_sqm:
        raise ValueError(f"不支持的面积单位: {from_unit} 或 {to_unit}")
    
    sqm = value * to_sqm[from_unit]
    return sqm * from_sqm[to_unit]

def convert_time(value, from_unit, to_unit):
    """时间单位转换"""
    # 转换为秒（基准单位）
    to_second = {
        'second': 1,
        'millisecond': 0.001,
        'microsecond': 0.000001,
        'minute': 60,
        'hour': 3600,
        'day': 86400,
        'week': 604800,
        'month': 2592000,  # 30天
        'year': 31536000  # 365天
    }
    
    # 从秒转换
    from_second = {k: 1/v for k, v in to_second.items()}
    
    if from_unit not in to_second or to_unit not in from_second:
        raise ValueError(f"不支持的时间单位: {from_unit} 或 {to_unit}")
    
    seconds = value * to_second[from_unit]
    return seconds * from_second[to_unit]

def convert_data(value, from_unit, to_unit):
    """数据存储单位转换"""
    # 转换为字节（基准单位）
    to_byte = {
        'byte': 1,
        'kilobyte': 1024,
        'megabyte': 1048576,
        'gigabyte': 1073741824,
        'terabyte': 1099511627776,
        'petabyte': 1125899906842624,
        'bit': 0.125
    }
    
    # 从字节转换
    from_byte = {k: 1/v for k, v in to_byte.items()}
    
    if from_unit not in to_byte or to_unit not in from_byte:
        raise ValueError(f"不支持的数据单位: {from_unit} 或 {to_unit}")
    
    bytes_val = value * to_byte[from_unit]
    return bytes_val * from_byte[to_unit]

def get_category_name(category):
    """获取类别名称"""
    category_names = {
        'length': '长度',
        'weight': '重量',
        'temperature': '温度',
        'volume': '体积',
        'speed': '速度',
        'area': '面积',
        'time': '时间',
        'data': '数据存储'
    }
    return category_names.get(category, category)

def get_supported_categories():
    """获取支持的单位类别"""
    return {
        'length': {
            'name': '长度',
            'units': ['meter', 'kilometer', 'centimeter', 'millimeter', 'mile', 'yard', 'foot', 'inch', 'li', 'zhang', 'chi', 'cun']
        },
        'weight': {
            'name': '重量',
            'units': ['kilogram', 'gram', 'milligram', 'ton', 'pound', 'ounce', 'jin', 'liang', 'qian']
        },
        'temperature': {
            'name': '温度',
            'units': ['celsius', 'fahrenheit', 'kelvin']
        },
        'volume': {
            'name': '体积',
            'units': ['liter', 'milliliter', 'cubic_meter', 'cubic_centimeter', 'gallon', 'quart', 'pint', 'cup', 'sheng', 'dou']
        },
        'speed': {
            'name': '速度',
            'units': ['mps', 'kph', 'mph', 'knot', 'mach']
        },
        'area': {
            'name': '面积',
            'units': ['square_meter', 'square_kilometer', 'square_centimeter', 'square_millimeter', 'hectare', 'acre', 'square_mile', 'square_foot', 'square_inch', 'mu', 'qing']
        },
        'time': {
            'name': '时间',
            'units': ['second', 'millisecond', 'microsecond', 'minute', 'hour', 'day', 'week', 'month', 'year']
        },
        'data': {
            'name': '数据存储',
            'units': ['byte', 'kilobyte', 'megabyte', 'gigabyte', 'terabyte', 'petabyte', 'bit']
        }
    }

if __name__ == '__main__':
    # 测试代码
    print("长度转换 1千米 to 米:", convert_units(1, 'kilometer', 'meter', 'length'))
    print("温度转换 100摄氏度 to 华氏度:", convert_units(100, 'celsius', 'fahrenheit', 'temperature'))
    print("重量转换 1斤 to 克:", convert_units(1, 'jin', 'gram', 'weight'))
