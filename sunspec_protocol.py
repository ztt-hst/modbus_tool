#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SunSpec协议解析模块 - 支持model_xxx.json格式
"""

import json
import os

class SunSpecProtocol:
    """SunSpec协议解析类"""

    def __init__(self, model_dir='.'):
        self.model_dir = model_dir
        self.models = {}
        self.base_address = 0  # 默认0，可被扫描覆盖
        self.model_base_addrs = {}  # 新增：保存扫描到的模型地址
        self.load_models()

    def load_models(self):
        """加载所有model_xxx.json文件"""
        try:
            model_files = {
                802: 'model_802.json',
                805: 'model_805.json', 
                899: 'model_899.json'
            }
            
            for table_id, filename in model_files.items():
                filepath = os.path.join(self.model_dir, filename)
                if os.path.exists(filepath):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        model_data = json.load(f)
                        self.models[table_id] = model_data
                else:
                    print(f"警告: 找不到模型文件 {filename}")
        except Exception as e:
            print(f"加载模型文件失败: {e}")

    def parse_table_data(self, table_id, data):
        """解析表格数据，支持model_xxx.json格式"""
        if table_id not in self.models:
            return None
            
        model_data = self.models[table_id]
        points = model_data['group']['points']
        parsed_data = {}

        # 解析所有字段
        current_offset = 0
        for point in points:
            name = point['name']
            field_type = point['type'].lower()
            size = point.get('size', 1)
            offset = point.get('offset', current_offset)
            raw_value = None
            value = None

            # 取出对应寄存器
            if offset + size <= len(data):
                regs = data[offset:offset+size]
                # 解析类型
                if field_type in ['uint16', 'sunssf']:
                    raw_value = regs[0]
                    if field_type == 'sunssf' or field_type == 'int16':
                        # 有符号
                        if raw_value > 32767:
                            raw_value = raw_value - 65536
                    value = raw_value
                elif field_type == 'int16':
                    raw_value = regs[0]
                    if raw_value > 32767:
                        raw_value = raw_value - 65536
                    value = raw_value
                elif field_type == 'uint32':
                    raw_value = (regs[0] << 16) | regs[1]
                    value = raw_value
                elif field_type == 'int32':
                    raw_value = (regs[0] << 16) | regs[1]
                    if raw_value > 0x7FFFFFFF:
                        raw_value = raw_value - 0x100000000
                    value = raw_value
                elif field_type == 'enum16':
                    # enum16 使用1个寄存器，按uint16解析
                    raw_value = regs[0]
                    value = raw_value
                elif field_type == 'bitfield32':
                    # bitfield32 使用2个寄存器，按uint32解析
                    raw_value = (regs[0] << 16) | regs[1]
                    value = raw_value
                elif field_type == 'string':
                    # 每个寄存器2字节，拼接为字符串
                    chars = []
                    for reg in regs:
                        chars.append(chr((reg >> 8) & 0xFF))
                        chars.append(chr(reg & 0xFF))
                    value = ''.join(chars).rstrip('\x00').strip()
                    raw_value = value
                else:
                    # 其他类型直接显示原始
                    value = regs[0]
                    raw_value = regs[0]
            else:
                value = None
                raw_value = None

            # 移除缩放因子处理，统一显示原始值
            parsed_data[name] = {
                'value': value,
                'raw': raw_value,
                'unit': point.get('units', ''),
                'type': field_type,
                'label': point.get('label', name),
                'description': point.get('desc', ''),
                'access': 'rw' if 'access' in point and point['access'] == 'RW' else 'r'
            }
            
            current_offset = offset + size

        return parsed_data

    def parse_single_field(self, table_id, field_name, data):
        """解析单个字段，根据type和size解析"""
        if table_id not in self.models:
            return None
            
        model_data = self.models[table_id]
        points = model_data['group']['points']
        
        # 找到指定字段
        for point in points:
            if point['name'] == field_name:
                field_type = point['type'].lower()
                size = point.get('size', 1)
                
                # 检查数据长度是否足够
                if len(data) < size:
                    return None
                
                # 根据类型解析
                if field_type in ['uint16', 'sunssf']:
                    raw_value = data[0]
                    if field_type == 'sunssf':
                        # sunssf是有符号的
                        if raw_value > 32767:
                            raw_value = raw_value - 65536
                    value = raw_value
                    
                elif field_type == 'int16':
                    raw_value = data[0]
                    if raw_value > 32767:
                        raw_value = raw_value - 65536
                    value = raw_value
                    
                elif field_type == 'uint32':
                    if size >= 2:
                        raw_value = (data[0] << 16) | data[1]
                        value = raw_value
                    else:
                        return None
                        
                elif field_type == 'int32':
                    if size >= 2:
                        raw_value = (data[0] << 16) | data[1]
                        if raw_value > 0x7FFFFFFF:
                            raw_value = raw_value - 0x100000000
                        value = raw_value
                    else:
                        return None
                        
                elif field_type == 'enum16':
                    # enum16 使用1个寄存器，按uint16解析
                    raw_value = data[0]
                    value = raw_value
                    
                elif field_type == 'bitfield32':
                    # bitfield32 使用2个寄存器，按uint32解析
                    if size >= 2:
                        raw_value = (data[0] << 16) | data[1]
                        value = raw_value
                    else:
                        return None
                        
                elif field_type == 'string':
                    # 字符串解析：每个寄存器2字节
                    chars = []
                    for reg in data:
                        chars.append(chr((reg >> 8) & 0xFF))
                        chars.append(chr(reg & 0xFF))
                    value = ''.join(chars).rstrip('\x00').strip()
                    raw_value = value
                    
                else:
                    # 其他类型直接显示原始
                    value = data[0]
                    raw_value = data[0]
                
                # 移除缩放因子处理，统一显示原始值
                return {
                    'value': value,
                    'raw': raw_value,
                    'unit': point.get('units', ''),
                    'type': field_type,
                    'label': point.get('label', field_name),
                    'description': point.get('desc', ''),
                    'access': 'rw' if 'access' in point and point['access'] == 'RW' else 'r'
                }
        
        return None

    def set_model_base_address(self, model_id, address):
        """设置特定模型的基地址"""
        self.model_base_addrs[model_id] = address

    def get_table_info(self, table_id):
        """获取表格信息，转换为兼容格式"""
        if table_id not in self.models:
            return None
            
        model_data = self.models[table_id]
        points = model_data['group']['points']
        
        # 转换为兼容格式，计算正确的offset
        fields = {}
        current_offset = 0
        total_registers = 0  # 新增：计算总寄存器数
        
        for point in points:
            # 如果没有显式定义offset，则按顺序计算
            if 'offset' in point:
                offset = point['offset']
            else:
                offset = current_offset
                current_offset += point.get('size', 1)  # 累加字段大小
            
            # 累加寄存器数量
            total_registers += point.get('size', 1)
            
            fields[point['name']] = {
                'offset': offset,
                'size': point.get('size', 1),
                'type': point['type'],
                'scale': point.get('sf', 1),
                'unit': point.get('units', ''),
                'access': 'rw' if 'access' in point and point['access'] == 'RW' else 'r',
                'label': point.get('label', point['name']),
                'description': point.get('desc', '')
            }
        
        # 使用扫描到的模型地址，如果没有则使用默认基地址
        base_addr = self.model_base_addrs.get(table_id, self.base_address)
        
        return {
            'name': model_data['group'].get('label', f'Model {table_id}'),
            'description': model_data['group'].get('label', f'Model {table_id}'),
            'base_address': base_addr,
            'length': total_registers,  # 修改：使用总寄存器数
            'fields': fields
        }

    def get_available_tables(self):
        """获取可用的表格列表"""
        return list(self.models.keys()) 