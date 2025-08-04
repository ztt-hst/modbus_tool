#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SunSpec Modbus协议上位机主程序
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import json
import os

from sunspec_protocol import SunSpecProtocol
from modbus_client import ModbusClient
from gui_components import ConnectionFrame, TableControlFrame, DataTableFrame

class SunSpecGUI:
    """SunSpec协议GUI界面"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SunSpec Modbus协议上位机")
        self.root.geometry("1400x900")
        
        self.modbus_client = ModbusClient()
        self.sunspec_protocol = SunSpecProtocol()
        self.current_table = 802
        self.auto_refresh = False
        self.refresh_thread = None
        
        self.setup_gui()
        self.bind_events()
        self.load_config()
    
    def setup_gui(self):
        """设置GUI界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 连接设置框架
        self.connection_frame = ConnectionFrame(main_frame)
        self.connection_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 表格选择框架
        self.table_frame = TableControlFrame(main_frame)
        self.table_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 数据显示框架
        data_frame = ttk.LabelFrame(main_frame, text="数据显示", padding=10)
        data_frame.pack(fill=tk.BOTH, expand=True)
        
        self.data_table = DataTableFrame(data_frame)
        self.data_table.pack(fill=tk.BOTH, expand=True)
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def bind_events(self):
        """绑定事件"""
        # 连接按钮事件
        self.connection_frame.connect_tcp_btn.config(command=self.connect_tcp)
        self.connection_frame.connect_rtu_btn.config(command=self.connect_rtu)
        self.connection_frame.disconnect_btn.config(command=self.disconnect)
        
        # 表格控制事件
        self.table_frame.read_btn.config(command=self.read_table_data)
        self.table_frame.write_btn.config(command=self.write_table_data)
        self.table_frame.auto_refresh_var.trace('w', self.on_auto_refresh_changed)
        
        # 表格选择事件
        table_combo = self.table_frame.winfo_children()[1]  # 获取表格选择下拉框
        table_combo.bind('<<ComboboxSelected>>', self.on_table_changed)
    
    def connect_tcp(self):
        """连接TCP Modbus"""
        host = self.connection_frame.tcp_host_var.get()
        port = int(self.connection_frame.tcp_port_var.get())
        
        if self.modbus_client.connect_tcp(host, port):
            self.status_var.set(f"TCP连接成功: {host}:{port}")
            messagebox.showinfo("连接成功", f"已连接到 {host}:{port}")
        else:
            self.status_var.set("TCP连接失败")
            messagebox.showerror("连接失败", f"无法连接到 {host}:{port}")
    
    def connect_rtu(self):
        """连接RTU Modbus"""
        port = self.connection_frame.rtu_port_var.get()
        baudrate = int(self.connection_frame.baudrate_var.get())
        
        if self.modbus_client.connect_rtu(port, baudrate):
            self.status_var.set(f"RTU连接成功: {port}")
            messagebox.showinfo("连接成功", f"已连接到 {port}")
        else:
            self.status_var.set("RTU连接失败")
            messagebox.showerror("连接失败", f"无法连接到 {port}")
    
    def disconnect(self):
        """断开连接"""
        self.modbus_client.disconnect()
        self.status_var.set("已断开连接")
        self.stop_auto_refresh()
    
    def on_table_changed(self, event=None):
        """表格选择改变事件"""
        self.current_table = self.table_frame.table_var.get()
        self.data_table.clear_data()
        self.status_var.set(f"已选择表格 {self.current_table}")
    
    def read_table_data(self):
        """读取表格数据"""
        if not self.modbus_client.is_connected():
            messagebox.showwarning("警告", "请先连接Modbus设备")
            return
        
        try:
            start_address = int(self.table_frame.start_address_var.get())
            table_info = self.sunspec_protocol.get_table_info(self.current_table)
            if not table_info:
                messagebox.showerror("错误", f"未找到表格 {self.current_table} 的定义")
                return
            
            length = table_info['length']
            
            # 读取数据
            data = self.modbus_client.read_holding_registers(start_address, length)
            if data is None:
                messagebox.showerror("错误", "读取数据失败")
                return
            
            # 解析数据
            parsed_data = self.sunspec_protocol.parse_table_data(self.current_table, data)
            if parsed_data:
                self.data_table.display_data(parsed_data)
                self.status_var.set(f"成功读取表格 {self.current_table} 数据")
            else:
                messagebox.showerror("错误", "解析数据失败")
                
        except Exception as e:
            messagebox.showerror("错误", f"读取数据时发生错误: {e}")
    
    def write_table_data(self):
        """写入表格数据"""
        if not self.modbus_client.is_connected():
            messagebox.showwarning("警告", "请先连接Modbus设备")
            return
        
        # 这里可以实现写入功能
        messagebox.showinfo("信息", "写入功能待实现")
    
    def on_auto_refresh_changed(self, *args):
        """自动刷新状态改变事件"""
        if self.table_frame.auto_refresh_var.get():
            self.start_auto_refresh()
        else:
            self.stop_auto_refresh()
    
    def start_auto_refresh(self):
        """开始自动刷新"""
        if not self.modbus_client.is_connected():
            messagebox.showwarning("警告", "请先连接Modbus设备")
            self.table_frame.auto_refresh_var.set(False)
            return
        
        self.auto_refresh = True
        self.refresh_thread = threading.Thread(target=self.auto_refresh_worker, daemon=True)
        self.refresh_thread.start()
        self.status_var.set("自动刷新已启动")
    
    def stop_auto_refresh(self):
        """停止自动刷新"""
        self.auto_refresh = False
        if self.refresh_thread:
            self.refresh_thread.join(timeout=1)
        self.status_var.set("自动刷新已停止")
    
    def auto_refresh_worker(self):
        """自动刷新工作线程"""
        while self.auto_refresh:
            try:
                interval = float(self.table_frame.refresh_interval_var.get())
                time.sleep(interval)
                
                if self.auto_refresh:
                    # 在主线程中执行GUI更新
                    self.root.after(0, self.read_table_data)
            except Exception as e:
                print(f"自动刷新错误: {e}")
                break
    
    def load_config(self):
        """加载配置"""
        try:
            if os.path.exists('config.json'):
                with open('config.json', 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                self.connection_frame.tcp_host_var.set(config.get('tcp_host', '192.168.1.100'))
                self.connection_frame.tcp_port_var.set(config.get('tcp_port', '502'))
                self.connection_frame.rtu_port_var.set(config.get('rtu_port', 'COM1'))
                self.connection_frame.baudrate_var.set(config.get('baudrate', '9600'))
                self.table_frame.start_address_var.set(config.get('start_address', '40000'))
                self.table_frame.refresh_interval_var.set(config.get('refresh_interval', '5'))
        except Exception as e:
            print(f"加载配置失败: {e}")
    
    def save_config(self):
        """保存配置"""
        try:
            config = {
                'tcp_host': self.connection_frame.tcp_host_var.get(),
                'tcp_port': self.connection_frame.tcp_port_var.get(),
                'rtu_port': self.connection_frame.rtu_port_var.get(),
                'baudrate': self.connection_frame.baudrate_var.get(),
                'start_address': self.table_frame.start_address_var.get(),
                'refresh_interval': self.table_frame.refresh_interval_var.get()
            }
            
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def run(self):
        """运行GUI"""
        # 设置关闭事件处理
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """窗口关闭事件"""
        self.stop_auto_refresh()
        self.save_config()
        self.modbus_client.disconnect()
        self.root.destroy()

def main():
    """主函数"""
    app = SunSpecGUI()
    app.run()

if __name__ == "__main__":
    main()