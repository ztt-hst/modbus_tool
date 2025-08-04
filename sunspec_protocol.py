#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SunSpec协议解析模块
"""

import json
import os

class SunSpecProtocol:
    """SunSpec协议解析类"""
    
    def __init__(self, config_file='sunspec_config.json'):
        self.config_file = config_file
        self.sunspec_tables = {}
        self.load_config()
    
    def load_config(self):
        """从配置文件加载协议定义"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.sunspec_tables = config.get('tables', {})
            else:
                # 使用默认配置
                self.sunspec_tables = self.get_default_config()
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            self.sunspec_tables = self.get_default_config()
    
    def get_default_config(self):
        """获取默认配置"""
        return {
            "802": {
                "name": "Inverter Controls",
                "description": "逆变器控制参数",
                "base_address": 40000,
                "length": 66,
                "fields": {
                    "ID": {"offset": 0, "type": "uint16", "scale": 1, "unit": "", "description": "表格ID", "access": "r"},
                    "L": {"offset": 1, "type": "uint16", "scale": 1, "unit": "", "description": "表格长度", "access": "r"},
                    "Control": {"offset": 2, "type": "uint16", "scale": 1, "unit": "", "description": "控制模式", "access": "rw"},
                    "ConnWinTms": {"offset": 3, "type": "uint16", "scale": 1, "unit": "Secs", "description": "连接窗口时间", "access": "rw"},
                    "ConnRvrtTms": {"offset": 4, "type": "uint16", "scale": 1, "unit": "Secs", "description": "连接恢复时间", "access": "rw"},
                    "Conn": {"offset": 5, "type": "uint16", "scale": 1, "unit": "", "description": "连接状态", "access": "rw"},
                    "WMaxLimPct": {"offset": 6, "type": "uint16", "scale": 0.01, "unit": "%", "description": "最大功率限制百分比", "access": "rw"},
                    "WMaxLimPct_WinTms": {"offset": 7, "type": "uint16", "scale": 1, "unit": "Secs", "description": "最大功率限制窗口时间", "access": "rw"},
                    "WMaxLimPct_RvrtTms": {"offset": 8, "type": "uint16", "scale": 1, "unit": "Secs", "description": "最大功率限制恢复时间", "access": "rw"},
                    "WMaxLimPct_RmpTms": {"offset": 9, "type": "uint16", "scale": 1, "unit": "Secs", "description": "最大功率限制渐变时间", "access": "rw"},
                    "WMaxLimEna": {"offset": 10, "type": "uint16", "scale": 1, "unit": "", "description": "最大功率限制使能", "access": "rw"},
                    "OutPFSet": {"offset": 11, "type": "int16", "scale": 0.001, "unit": "PF", "description": "输出功率因数设置", "access": "rw"},
                    "OutPFSet_WinTms": {"offset": 12, "type": "uint16", "scale": 1, "unit": "Secs", "description": "输出功率因数窗口时间", "access": "rw"},
                    "OutPFSet_RvrtTms": {"offset": 13, "type": "uint16", "scale": 1, "unit": "Secs", "description": "输出功率因数恢复时间", "access": "rw"},
                    "OutPFSet_RmpTms": {"offset": 14, "type": "uint16", "scale": 1, "unit": "Secs", "description": "输出功率因数渐变时间", "access": "rw"},
                    "OutPFSet_Ena": {"offset": 15, "type": "uint16", "scale": 1, "unit": "", "description": "输出功率因数使能", "access": "rw"},
                    "VArMaxPct": {"offset": 16, "type": "uint16", "scale": 0.01, "unit": "%", "description": "最大无功功率百分比", "access": "rw"},
                    "VArMaxPct_WinTms": {"offset": 17, "type": "uint16", "scale": 1, "unit": "Secs", "description": "最大无功功率窗口时间", "access": "rw"},
                    "VArMaxPct_RvrtTms": {"offset": 18, "type": "uint16", "scale": 1, "unit": "Secs", "description": "最大无功功率恢复时间", "access": "rw"},
                    "VArMaxPct_RmpTms": {"offset": 19, "type": "uint16", "scale": 1, "unit": "Secs", "description": "最大无功功率渐变时间", "access": "rw"},
                    "VArMaxPct_Ena": {"offset": 20, "type": "uint16", "scale": 1, "unit": "", "description": "最大无功功率使能", "access": "rw"},
                    "VArAvalPct": {"offset": 21, "type": "uint16", "scale": 0.01, "unit": "%", "description": "可用无功功率百分比", "access": "rw"},
                    "VArAvalPct_WinTms": {"offset": 22, "type": "uint16", "scale": 1, "unit": "Secs", "description": "可用无功功率窗口时间", "access": "rw"},
                    "VArAvalPct_RvrtTms": {"offset": 23, "type": "uint16", "scale": 1, "unit": "Secs", "description": "可用无功功率恢复时间", "access": "rw"},
                    "VArAvalPct_RmpTms": {"offset": 24, "type": "uint16", "scale": 1, "unit": "Secs", "description": "可用无功功率渐变时间", "access": "rw"},
                    "VArAvalPct_Ena": {"offset": 25, "type": "uint16", "scale": 1, "unit": "", "description": "可用无功功率使能", "access": "rw"},
                    "WGra": {"offset": 26, "type": "uint16", "scale": 0.01, "unit": "%/Sec", "description": "功率渐变率", "access": "rw"},
                    "WGra_WinTms": {"offset": 27, "type": "uint16", "scale": 1, "unit": "Secs", "description": "功率渐变窗口时间", "access": "rw"},
                    "WGra_RvrtTms": {"offset": 28, "type": "uint16", "scale": 1, "unit": "Secs", "description": "功率渐变恢复时间", "access": "rw"},
                    "WGra_RmpTms": {"offset": 29, "type": "uint16", "scale": 1, "unit": "Secs", "description": "功率渐变渐变时间", "access": "rw"},
                    "WGra_Ena": {"offset": 30, "type": "uint16", "scale": 1, "unit": "", "description": "功率渐变使能", "access": "rw"},
                    "PFMin": {"offset": 31, "type": "uint16", "scale": 0.001, "unit": "PF", "description": "最小功率因数", "access": "rw"},
                    "PFMin_WinTms": {"offset": 32, "type": "uint16", "scale": 1, "unit": "Secs", "description": "最小功率因数窗口时间", "access": "rw"},
                    "PFMin_RvrtTms": {"offset": 33, "type": "uint16", "scale": 1, "unit": "Secs", "description": "最小功率因数恢复时间", "access": "rw"},
                    "PFMin_RmpTms": {"offset": 34, "type": "uint16", "scale": 1, "unit": "Secs", "description": "最小功率因数渐变时间", "access": "rw"},
                    "PFMin_Ena": {"offset": 35, "type": "uint16", "scale": 1, "unit": "", "description": "最小功率因数使能", "access": "rw"},
                    "PFMax": {"offset": 36, "type": "uint16", "scale": 0.001, "unit": "PF", "description": "最大功率因数", "access": "rw"},
                    "PFMax_WinTms": {"offset": 37, "type": "uint16", "scale": 1, "unit": "Secs", "description": "最大功率因数窗口时间", "access": "rw"},
                    "PFMax_RvrtTms": {"offset": 38, "type": "uint16", "scale": 1, "unit": "Secs", "description": "最大功率因数恢复时间", "access": "rw"},
                    "PFMax_RmpTms": {"offset": 39, "type": "uint16", "scale": 1, "unit": "Secs", "description": "最大功率因数渐变时间", "access": "rw"},
                    "PFMax_Ena": {"offset": 40, "type": "uint16", "scale": 1, "unit": "", "description": "最大功率因数使能", "access": "rw"},
                    "VArGra": {"offset": 41, "type": "uint16", "scale": 0.01, "unit": "%/Sec", "description": "无功功率渐变率", "access": "rw"},
                    "VArGra_WinTms": {"offset": 42, "type": "uint16", "scale": 1, "unit": "Secs", "description": "无功功率渐变窗口时间", "access": "rw"},
                    "VArGra_RvrtTms": {"offset": 43, "type": "uint16", "scale": 1, "unit": "Secs", "description": "无功功率渐变恢复时间", "access": "rw"},
                    "VArGra_RmpTms": {"offset": 44, "type": "uint16", "scale": 1, "unit": "Secs", "description": "无功功率渐变渐变时间", "access": "rw"},
                    "VArGra_Ena": {"offset": 45, "type": "uint16", "scale": 1, "unit": "", "description": "无功功率渐变使能", "access": "rw"},
                    "WMaxLimPct_SF": {"offset": 46, "type": "int16", "scale": 1, "unit": "", "description": "最大功率限制比例因子", "access": "r"},
                    "OutPFSet_SF": {"offset": 47, "type": "int16", "scale": 1, "unit": "", "description": "输出功率因数比例因子", "access": "r"},
                    "VArMaxPct_SF": {"offset": 48, "type": "int16", "scale": 1, "unit": "", "description": "最大无功功率比例因子", "access": "r"},
                    "VArAvalPct_SF": {"offset": 49, "type": "int16", "scale": 1, "unit": "", "description": "可用无功功率比例因子", "access": "r"},
                    "WGra_SF": {"offset": 50, "type": "int16", "scale": 1, "unit": "", "description": "功率渐变比例因子", "access": "r"},
                    "PFMin_SF": {"offset": 51, "type": "int16", "scale": 1, "unit": "", "description": "最小功率因数比例因子", "access": "r"},
                    "PFMax_SF": {"offset": 52, "type": "int16", "scale": 1, "unit": "", "description": "最大功率因数比例因子", "access": "r"},
                    "VArGra_SF": {"offset": 53, "type": "int16", "scale": 1, "unit": "", "description": "无功功率渐变比例因子", "access": "r"},
                    "Pad": {"offset": 54, "type": "uint16", "scale": 1, "unit": "", "description": "填充", "access": "r"}
                }
            },
            "805": {
                "name": "Inverter Controls Extended",
                "description": "逆变器控制扩展参数",
                "base_address": 40066,
                "length": 66,
                "fields": {
                    "ID": {"offset": 0, "type": "uint16", "scale": 1, "unit": "", "description": "表格ID", "access": "r"},
                    "L": {"offset": 1, "type": "uint16", "scale": 1, "unit": "", "description": "表格长度", "access": "r"},
                    "WMaxLimPct_RmpUpRte": {"offset": 2, "type": "uint16", "scale": 0.01, "unit": "%/Sec", "description": "最大功率限制上升率", "access": "rw"},
                    "WMaxLimPct_RmpDnRte": {"offset": 3, "type": "uint16", "scale": 0.01, "unit": "%/Sec", "description": "最大功率限制下降率", "access": "rw"},
                    "WMaxLimPct_SF": {"offset": 4, "type": "int16", "scale": 1, "unit": "", "description": "最大功率限制比例因子", "access": "r"},
                    "OutPFSet_RmpUpRte": {"offset": 5, "type": "uint16", "scale": 0.001, "unit": "PF/Sec", "description": "输出功率因数上升率", "access": "rw"},
                    "OutPFSet_RmpDnRte": {"offset": 6, "type": "uint16", "scale": 0.001, "unit": "PF/Sec", "description": "输出功率因数下降率", "access": "rw"},
                    "OutPFSet_SF": {"offset": 7, "type": "int16", "scale": 1, "unit": "", "description": "输出功率因数比例因子", "access": "r"},
                    "VArMaxPct_RmpUpRte": {"offset": 8, "type": "uint16", "scale": 0.01, "unit": "%/Sec", "description": "最大无功功率上升率", "access": "rw"},
                    "VArMaxPct_RmpDnRte": {"offset": 9, "type": "uint16", "scale": 0.01, "unit": "%/Sec", "description": "最大无功功率下降率", "access": "rw"},
                    "VArMaxPct_SF": {"offset": 10, "type": "int16", "scale": 1, "unit": "", "description": "最大无功功率比例因子", "access": "r"},
                    "VArAvalPct_RmpUpRte": {"offset": 11, "type": "uint16", "scale": 0.01, "unit": "%/Sec", "description": "可用无功功率上升率", "access": "rw"},
                    "VArAvalPct_RmpDnRte": {"offset": 12, "type": "uint16", "scale": 0.01, "unit": "%/Sec", "description": "可用无功功率下降率", "access": "rw"},
                    "VArAvalPct_SF": {"offset": 13, "type": "int16", "scale": 1, "unit": "", "description": "可用无功功率比例因子", "access": "r"},
                    "WGra_RmpUpRte": {"offset": 14, "type": "uint16", "scale": 0.01, "unit": "%/Sec", "description": "功率渐变上升率", "access": "rw"},
                    "WGra_RmpDnRte": {"offset": 15, "type": "uint16", "scale": 0.01, "unit": "%/Sec", "description": "功率渐变下降率", "access": "rw"},
                    "WGra_SF": {"offset": 16, "type": "int16", "scale": 1, "unit": "", "description": "功率渐变比例因子", "access": "r"},
                    "PFMin_RmpUpRte": {"offset": 17, "type": "uint16", "scale": 0.001, "unit": "PF/Sec", "description": "最小功率因数上升率", "access": "rw"},
                    "PFMin_RmpDnRte": {"offset": 18, "type": "uint16", "scale": 0.001, "unit": "PF/Sec", "description": "最小功率因数下降率", "access": "rw"},
                    "PFMin_SF": {"offset": 19, "type": "int16", "scale": 1, "unit": "", "description": "最小功率因数比例因子", "access": "r"},
                    "PFMax_RmpUpRte": {"offset": 20, "type": "uint16", "scale": 0.001, "unit": "PF/Sec", "description": "最大功率因数上升率", "access": "rw"},
                    "PFMax_RmpDnRte": {"offset": 21, "type": "uint16", "scale": 0.001, "unit": "PF/Sec", "description": "最大功率因数下降率", "access": "rw"},
                    "PFMax_SF": {"offset": 22, "type": "int16", "scale": 1, "unit": "", "description": "最大功率因数比例因子", "access": "r"},
                    "VArGra_RmpUpRte": {"offset": 23, "type": "uint16", "scale": 0.01, "unit": "%/Sec", "description": "无功功率渐变上升率", "access": "rw"},
                    "VArGra_RmpDnRte": {"offset": 24, "type": "uint16", "scale": 0.01, "unit": "%/Sec", "description": "无功功率渐变下降率", "access": "rw"},
                    "VArGra_SF": {"offset": 25, "type": "int16", "scale": 1, "unit": "", "description": "无功功率渐变比例因子", "access": "r"},
                    "Pad": {"offset": 26, "type": "uint16", "scale": 1, "unit": "", "description": "填充", "access": "r"}
                }
            },
            "899": {
                "name": "Inverter Controls Extended 2",
                "description": "逆变器控制扩展参数2",
                "base_address": 40132,
                "length": 66,
                "fields": {
                    "ID": {"offset": 0, "type": "uint16", "scale": 1, "unit": "", "description": "表格ID", "access": "r"},
                    "L": {"offset": 1, "type": "uint16", "scale": 1, "unit": "", "description": "表格长度", "access": "r"},
                    "WMaxLimPct_RmpUpRte": {"offset": 2, "type": "uint16", "scale": 0.01, "unit": "%/Sec", "description": "最大功率限制上升率", "access": "rw"},
                    "WMaxLimPct_RmpDnRte": {"offset": 3, "type": "uint16", "scale": 0.01, "unit": "%/Sec", "description": "最大功率限制下降率", "access": "rw"},
                    "WMaxLimPct_SF": {"offset": 4, "type": "int16", "scale": 1, "unit": "", "description": "最大功率限制比例因子", "access": "r"},
                    "OutPFSet_RmpUpRte": {"offset": 5, "type": "uint16", "scale": 0.001, "unit": "PF/Sec", "description": "输出功率因数上升率", "access": "rw"},
                    "OutPFSet_RmpDnRte": {"offset": 6, "type": "uint16", "scale": 0.001, "unit": "PF/Sec", "description": "输出功率因数下降率", "access": "rw"},
                    "OutPFSet_SF": {"offset": 7, "type": "int16", "scale": 1, "unit": "", "description": "输出功率因数比例因子", "access": "r"},
                    "VArMaxPct_RmpUpRte": {"offset": 8, "type": "uint16", "scale": 0.01, "unit": "%/Sec", "description": "最大无功功率上升率", "access": "rw"},
                    "VArMaxPct_RmpDnRte": {"offset": 9, "type": "uint16", "scale": 0.01, "unit": "%/Sec", "description": "最大无功功率下降率", "access": "rw"},
                    "VArMaxPct_SF": {"offset": 10, "type": "int16", "scale": 1, "unit": "", "description": "最大无功功率比例因子", "access": "r"},
                    "VArAvalPct_RmpUpRte": {"offset": 11, "type": "uint16", "scale": 0.01, "unit": "%/Sec", "description": "可用无功功率上升率", "access": "rw"},
                    "VArAvalPct_RmpDnRte": {"offset": 12, "type": "uint16", "scale": 0.01, "unit": "%/Sec", "description": "可用无功功率下降率", "access": "rw"},
                    "VArAvalPct_SF": {"offset": 13, "type": "int16", "scale": 1, "unit": "", "description": "可用无功功率比例因子", "access": "r"},
                    "WGra_RmpUpRte": {"offset": 14, "type": "uint16", "scale": 0.01, "unit": "%/Sec", "description": "功率渐变上升率", "access": "rw"},
                    "WGra_RmpDnRte": {"offset": 15, "type": "uint16", "scale": 0.01, "unit": "%/Sec", "description": "功率渐变下降率", "access": "rw"},
                    "WGra_SF": {"offset": 16, "type": "int16", "scale": 1, "unit": "", "description": "功率渐变比例因子", "access": "r"},
                    "PFMin_RmpUpRte": {"offset": 17, "type": "uint16", "scale": 0.001, "unit": "PF/Sec", "description": "最小功率因数上升率", "access": "rw"},
                    "PFMin_RmpDnRte": {"offset": 18, "type": "uint16", "scale": 0.001, "unit": "PF/Sec", "description": "最小功率因数下降率", "access": "rw"},
                    "PFMin_SF": {"offset": 19, "type": "int16", "scale": 1, "unit": "", "description": "最小功率因数比例因子", "access": "r"},
                    "PFMax_RmpUpRte": {"offset": 20, "type": "uint16", "scale": 0.001, "unit": "PF/Sec", "description": "最大功率因数上升率", "access": "rw"},
                    "PFMax_RmpDnRte": {"offset": 21, "type": "uint16", "scale": 0.001, "unit": "PF/Sec", "description": "最大功率因数下降率", "access": "rw"},
                    "PFMax_SF": {"offset": 22, "type": "int16", "scale": 1, "unit": "", "description": "最大功率因数比例因子", "access": "r"},
                    "VArGra_RmpUpRte": {"offset": 23, "type": "uint16", "scale": 0.01, "unit": "%/Sec", "description": "无功功率渐变上升率", "access": "rw"},
                    "VArGra_RmpDnRte": {"offset": 24, "type": "uint16", "scale": 0.01, "unit": "%/Sec", "description": "无功功率渐变下降率", "access": "rw"},
                    "VArGra_SF": {"offset": 25, "type": "int16", "scale": 1, "unit": "", "description": "无功功率渐变比例因子", "access": "r"},
                    "Pad": {"offset": 26, "type": "uint16", "scale": 1, "unit": "", "description": "填充", "access": "r"}
                }
            }
        }
    
    def parse_table_data(self, table_id, data):
        """解析表格数据"""
        table_id_str = str(table_id)
        if table_id_str not in self.sunspec_tables:
            return None
        
        table_info = self.sunspec_tables[table_id_str]
        parsed_data = {}
        
        for field_name, field_info in table_info['fields'].items():
            offset = field_info['offset']
            if offset < len(data):
                raw_value = data[offset]
                scale = field_info['scale']
                field_type = field_info['type']
                
                # 根据数据类型处理
                if field_type == 'int16':
                    # 处理有符号16位整数
                    if raw_value > 32767:
                        raw_value = raw_value - 65536
                    value = raw_value * scale
                else:
                    value = raw_value * scale
                
                parsed_data[field_name] = {
                    'value': value,
                    'raw': raw_value,
                    'unit': field_info['unit'],
                    'type': field_type,
                    'description': field_info.get('description', ''),
                    'access': field_info.get('access', 'r')
                }
        
        return parsed_data
    
    def get_table_info(self, table_id):
        """获取表格信息"""
        table_id_str = str(table_id)
        return self.sunspec_tables.get(table_id_str, None)
    
    def get_available_tables(self):
        """获取可用的表格列表"""
        return list(self.sunspec_tables.keys()) 