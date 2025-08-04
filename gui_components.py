#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI组件模块
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time

class DataTableFrame(ttk.Frame):
    """数据表格框架"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.setup_table()
    
    def setup_table(self):
        """设置数据表格"""
        # 创建表格
        columns = ('字段名', '值', '原始值', '单位', '类型', '描述', '访问权限')
        self.tree = ttk.Treeview(self, columns=columns, show='headings', height=20)
        
        # 设置列标题和宽度
        column_widths = {
            '字段名': 120,
            '值': 100,
            '原始值': 80,
            '单位': 60,
            '类型': 80,
            '描述': 200,
            '访问权限': 80
        }
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 100))
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def display_data(self, data):
        """显示数据"""
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 添加新数据
        for field_name, field_data in data.items():
            value = field_data['value']
            raw_value = field_data['raw']
            unit = field_data['unit']
            field_type = field_data['type']
            description = field_data.get('description', '')
            access = field_data.get('access', 'r')
            
            # 格式化显示
            if isinstance(value, float):
                value_str = f"{value:.6f}"
            else:
                value_str = str(value)
            
            self.tree.insert('', 'end', values=(
                field_name, value_str, raw_value, unit, field_type, description, access
            ))
    
    def clear_data(self):
        """清空数据"""
        for item in self.tree.get_children():
            self.tree.delete(item)

class ConnectionFrame(ttk.LabelFrame):
    """连接设置框架"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, text="连接设置", padding=10, **kwargs)
        self.setup_connection_controls()
    
    def setup_connection_controls(self):
        """设置连接控件"""
        # TCP连接设置
        tcp_frame = ttk.Frame(self)
        tcp_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(tcp_frame, text="TCP连接:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.tcp_host_var = tk.StringVar(value="192.168.1.100")
        ttk.Entry(tcp_frame, textvariable=self.tcp_host_var, width=15).grid(row=0, column=1, padx=(0, 5))
        
        ttk.Label(tcp_frame, text="端口:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.tcp_port_var = tk.StringVar(value="502")
        ttk.Entry(tcp_frame, textvariable=self.tcp_port_var, width=8).grid(row=0, column=3, padx=(0, 10))
        
        self.connect_tcp_btn = ttk.Button(tcp_frame, text="连接TCP")
        self.connect_tcp_btn.grid(row=0, column=4, padx=(0, 5))
        
        self.disconnect_btn = ttk.Button(tcp_frame, text="断开")
        self.disconnect_btn.grid(row=0, column=5)
        
        # RTU连接设置
        rtu_frame = ttk.Frame(self)
        rtu_frame.pack(fill=tk.X)
        
        ttk.Label(rtu_frame, text="RTU连接:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.rtu_port_var = tk.StringVar(value="COM1")
        ttk.Entry(rtu_frame, textvariable=self.rtu_port_var, width=8).grid(row=0, column=1, padx=(0, 5))
        
        ttk.Label(rtu_frame, text="波特率:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.baudrate_var = tk.StringVar(value="9600")
        ttk.Combobox(rtu_frame, textvariable=self.baudrate_var, 
                     values=["9600", "19200", "38400", "57600", "115200"], 
                     width=8).grid(row=0, column=3, padx=(0, 10))
        
        self.connect_rtu_btn = ttk.Button(rtu_frame, text="连接RTU")
        self.connect_rtu_btn.grid(row=0, column=4, padx=(0, 5))

class TableControlFrame(ttk.LabelFrame):
    """表格控制框架"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, text="表格选择", padding=10, **kwargs)
        self.setup_table_controls()
    
    def setup_table_controls(self):
        """设置表格控制控件"""
        ttk.Label(self, text="选择表格:").pack(side=tk.LEFT, padx=(0, 5))
        self.table_var = tk.IntVar(value=802)
        table_combo = ttk.Combobox(self, textvariable=self.table_var, 
                                   values=[802, 805, 899], state="readonly", width=10)
        table_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(self, text="起始地址:").pack(side=tk.LEFT, padx=(0, 5))
        self.start_address_var = tk.StringVar(value="40000")
        ttk.Entry(self, textvariable=self.start_address_var, width=10).pack(side=tk.LEFT, padx=(0, 10))
        
        self.read_btn = ttk.Button(self, text="读取数据")
        self.read_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.write_btn = ttk.Button(self, text="写入数据")
        self.write_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # 自动刷新设置
        self.auto_refresh_var = tk.BooleanVar()
        ttk.Checkbutton(self, text="自动刷新", variable=self.auto_refresh_var).pack(side=tk.LEFT, padx=(20, 0))
        
        ttk.Label(self, text="刷新间隔(秒):").pack(side=tk.LEFT, padx=(10, 5))
        self.refresh_interval_var = tk.StringVar(value="5")
        ttk.Entry(self, textvariable=self.refresh_interval_var, width=5).pack(side=tk.LEFT) 