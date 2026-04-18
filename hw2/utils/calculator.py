"""
计算器模块
提供数学表达式计算功能
"""

import math
import re
from datetime import datetime

def calculate_expression(expression):
    """
    计算数学表达式
    
    Args:
        expression: 数学表达式字符串
    
    Returns:
        计算结果
    """
    try:
        # 清理表达式
        expr = expression.strip()
        
        # 安全检查：防止执行危险代码
        if not is_safe_expression(expr):
            raise ValueError("表达式包含不安全的内容")
        
        # 替换常见数学函数和常量
        expr = replace_math_functions(expr)
        
        # 计算表达式
        result = eval(expr, {"__builtins__": {}}, SAFE_GLOBALS)
        
        # 处理特殊结果
        if isinstance(result, (int, float)):
            # 如果是整数，返回整数，否则保留适当的小数位数
            if result == int(result):
                return int(result)
            else:
                # 保留最多6位小数
                return round(result, 6)
        else:
            return result
            
    except Exception as e:
        raise ValueError(f"计算错误: {str(e)}")

def is_safe_expression(expression):
    """检查表达式是否安全"""
    # 禁止的危险模式
    dangerous_patterns = [
        r'__.*__',  # 双下划线属性
        r'import\s+',  # import语句
        r'exec\s*\(',  # exec函数
        r'eval\s*\(',  # eval函数
        r'compile\s*\(',  # compile函数
        r'open\s*\(',  # open函数
        r'file\s*\(',  # file函数
        r'os\.',  # os模块
        r'sys\.',  # sys模块
        r'subprocess\.',  # subprocess模块
        r'\.\./',  # 目录遍历
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, expression, re.IGNORECASE):
            return False
    
    # 检查括号是否匹配
    if expression.count('(') != expression.count(')'):
        return False
    
    # 检查是否有不安全的字符
    safe_chars = set('0123456789+-*/.()^%!πe \t\n\r')
    math_funcs = ['sin', 'cos', 'tan', 'asin', 'acos', 'atan', 
                  'sinh', 'cosh', 'tanh', 'log', 'log10', 'exp',
                  'sqrt', 'abs', 'round', 'floor', 'ceil', 'pi', 'e']
    
    # 提取所有标识符
    identifiers = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*', expression)
    for ident in identifiers:
        if ident not in math_funcs and ident not in ['pi', 'e']:
            return False
    
    return True

def replace_math_functions(expression):
    """替换数学函数为Python可识别的形式"""
    replacements = {
        r'sin\s*\((.*?)\)': r'math.sin(\1)',
        r'cos\s*\((.*?)\)': r'math.cos(\1)',
        r'tan\s*\((.*?)\)': r'math.tan(\1)',
        r'asin\s*\((.*?)\)': r'math.asin(\1)',
        r'acos\s*\((.*?)\)': r'math.acos(\1)',
        r'atan\s*\((.*?)\)': r'math.atan(\1)',
        r'sinh\s*\((.*?)\)': r'math.sinh(\1)',
        r'cosh\s*\((.*?)\)': r'math.cosh(\1)',
        r'tanh\s*\((.*?)\)': r'math.tanh(\1)',
        r'log\s*\((.*?)\)': r'math.log(\1)',
        r'log10\s*\((.*?)\)': r'math.log10(\1)',
        r'exp\s*\((.*?)\)': r'math.exp(\1)',
        r'sqrt\s*\((.*?)\)': r'math.sqrt(\1)',
        r'abs\s*\((.*?)\)': r'abs(\1)',
        r'round\s*\((.*?)\)': r'round(\1)',
        r'floor\s*\((.*?)\)': r'math.floor(\1)',
        r'ceil\s*\((.*?)\)': r'math.ceil(\1)',
        r'π': 'math.pi',
        r'pi': 'math.pi',
        r'e\b(?!\w)': 'math.e',  # 匹配单独的e，不是单词的一部分
        r'\^': '**',  # 将^替换为**
        r'\!': 'math.factorial',  # 阶乘
    }
    
    expr = expression
    for pattern, replacement in replacements.items():
        expr = re.sub(pattern, replacement, expr, flags=re.IGNORECASE)
    
    # 处理阶乘的特殊情况
    expr = re.sub(r'(\d+)\s*\!', r'math.factorial(\1)', expr)
    
    return expr

# 安全的环境变量
SAFE_GLOBALS = {
    'math': math,
    'abs': abs,
    'round': round,
    'int': int,
    'float': float,
    'pow': pow,
    'sum': sum,
    'min': min,
    'max': max,
}

def calculate_with_history(expression, history=None):
    """
    计算表达式并保存到历史记录
    
    Args:
        expression: 数学表达式
        history: 历史记录列表（可选）
    
    Returns:
        (结果, 更新后的历史记录)
    """
    try:
        result = calculate_expression(expression)
        
        if history is None:
            history = []
        
        # 添加到历史记录
        history_entry = {
            'expression': expression,
            'result': result,
            'timestamp': datetime.now().isoformat()
        }
        
        # 保持历史记录大小
        history.append(history_entry)
        if len(history) > 50:
            history = history[-50:]
        
        return result, history
        
    except Exception as e:
        raise ValueError(f"计算失败: {str(e)}")

def get_calculator_functions():
    """获取支持的数学函数列表"""
    return {
        '基本运算': ['+', '-', '*', '/', '** (幂)', '% (模)'],
        '三角函数': ['sin(x)', 'cos(x)', 'tan(x)', 'asin(x)', 'acos(x)', 'atan(x)'],
        '双曲函数': ['sinh(x)', 'cosh(x)', 'tanh(x)'],
        '对数函数': ['log(x) - 自然对数', 'log10(x) - 常用对数'],
        '指数函数': ['exp(x) - e的x次方'],
        '其他函数': ['sqrt(x) - 平方根', 'abs(x) - 绝对值', 'round(x) - 四舍五入'],
        '常数': ['π 或 pi - 圆周率', 'e - 自然常数'],
        '特殊运算': ['x! - 阶乘']
    }

if __name__ == '__main__':
    # 测试代码
    test_expressions = [
        "2 + 3 * 4",
        "sin(π/2)",
        "log10(100)",
        "sqrt(16)",
        "2^3 + 5!",
        "3 * π"
    ]
    
    for expr in test_expressions:
        try:
            result = calculate_expression(expr)
            print(f"{expr} = {result}")
        except Exception as e:
            print(f"{expr} 错误: {e}")
