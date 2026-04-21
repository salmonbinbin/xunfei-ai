import json
import re


def parse_order_result(api_response):
    """
    解析完整的API响应，提取orderResult中的所有w字段内容并拼接

    参数:
        api_response: 完整的API响应字典
    返回:
        拼接后的文本字符串
    """
    try:
        # 从API响应中获取orderResult字段
        order_result_str = api_response.get('content', {}).get('orderResult', '{}')

        # 处理转义字符问题
        cleaned_str = re.sub(r'\\\\', r'\\', order_result_str)

        # 解析orderResult字符串为JSON对象
        order_result = json.loads(cleaned_str)

        # 提取所有w字段的值
        w_values = []

        # 遍历lattice数组
        if 'lattice' in order_result:
            for lattice_item in order_result['lattice']:
                if 'json_1best' in lattice_item:
                    # 解析json_1best字段
                    json_1best = json.loads(lattice_item['json_1best'])

                    # 处理st对象
                    if 'st' in json_1best and 'rt' in json_1best['st']:
                        for rt_item in json_1best['st']['rt']:
                            if 'ws' in rt_item:
                                for ws_item in rt_item['ws']:
                                    if 'cw' in ws_item:
                                        for cw_item in ws_item['cw']:
                                            if 'w' in cw_item:
                                                w_values.append(cw_item['w'])

        # 拼接所有w值
        return ''.join(w_values)

    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        return ""
    except Exception as e:
        print(f"处理过程中出错: {e}")
        return ""
