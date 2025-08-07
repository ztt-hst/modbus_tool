#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SunSpec Modbus协议上位机主程序
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import json
import os
from functools import partial
import sys
from sunspec_protocol import SunSpecProtocol
from modbus_client import ModbusClient
from gui_components import ConnectionFrame, DataTableFrame
from language_manager import LanguageManager

def get_resource_path(filename):
        """
        获取资源文件路径，兼容开发环境和PyInstaller打包后的环境
        """
        if getattr(sys, 'frozen', False):
            # PyInstaller打包后的exe
            base_path = sys._MEIPASS
        else:
            # 源码运行
            base_path = os.path.abspath(".")
        return os.path.join(base_path, filename)

class SunSpecGUI:
    """SunSpec协议GUI界面"""
    
    def __init__(self, language_manager=None):
        self.root = tk.Tk()
        
        # 使用传入的语言管理器或创建新的
        if language_manager is None:
            self.language_manager = LanguageManager()
        else:
            self.language_manager = language_manager
        
        # 设置窗口标题
        self.root.title(self.language_manager.get_text("window_title"))
        self.root.geometry("1400x900")
        
        # 设置窗口图标
        self.set_window_icon()
        
        self.modbus_client = ModbusClient()
        self.sunspec_protocol = SunSpecProtocol()
        self.current_table = 802
        self.auto_refresh = False
        self.refresh_thread = None
        
        # 新增：日志文件相关
        self.log_file_path = self.get_default_log_file()
        self.log_file_var = None  # 将在setup_gui中设置
        
        self.setup_gui()
        self.bind_events()
    def set_window_icon(self):
        """设置窗口图标"""
        try:
            # 获取图标文件路径
            icon_path = get_resource_path('BQC.ico')        
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
            else:
                print(f"图标文件不存在: {icon_path}")
        except Exception as e:
            print(f"设置窗口图标失败: {e}")

    def setup_gui(self):
        """设置GUI界面"""
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 语言切换按钮
        lang_frame = ttk.Frame(main_frame)
        lang_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(lang_frame, text="Language:").pack(side=tk.LEFT)
        lang_var = tk.StringVar(value=self.language_manager.get_current_language())
        lang_combo = ttk.Combobox(lang_frame, textvariable=lang_var, 
                                 values=self.language_manager.get_available_languages(),
                                 state="readonly", width=10)
        lang_combo.pack(side=tk.LEFT, padx=(5, 0))
        lang_combo.bind('<<ComboboxSelected>>', lambda e: self.change_language(lang_var.get()))

        # 连接设置
        self.connection_frame = ConnectionFrame(main_frame, self.language_manager)
        self.connection_frame.pack(fill=tk.X, pady=(0, 10))

        # 扫描基地址和模型地址按钮及显示
        scan_frame = ttk.Frame(main_frame)
        scan_frame.pack(fill=tk.X, pady=(0, 5))
        
        # 保存按钮引用以便更新文本
        self.scan_base_btn = ttk.Button(scan_frame, text=self.language_manager.get_text("scan_base_address"), 
                                   command=self.scan_base_address)
        self.scan_base_btn.pack(side=tk.LEFT)
        
        self.current_base_addr_label = ttk.Label(scan_frame, text=self.language_manager.get_text("current_base_address"))
        self.current_base_addr_label.pack(side=tk.LEFT, padx=(10, 2))
        
        self.base_addr_var = tk.StringVar(value=self.language_manager.get_text("not_scanned"))
        base_addr_entry = ttk.Entry(scan_frame, textvariable=self.base_addr_var, width=10, state="readonly")
        base_addr_entry.pack(side=tk.LEFT, padx=(0, 10))

        # 扫描模型地址按钮和显示
        self.scan_model_btn = ttk.Button(scan_frame, text=self.language_manager.get_text("scan_model_address"), 
                  command=self.scan_models)
        self.scan_model_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        self.model_802_label = ttk.Label(scan_frame, text="802:")
        self.model_802_label.pack(side=tk.LEFT)
        self.model_802_addr_var = tk.StringVar(value="-")
        ttk.Entry(scan_frame, textvariable=self.model_802_addr_var, width=8, state="readonly").pack(side=tk.LEFT)
        
        self.model_805_label = ttk.Label(scan_frame, text="805:")
        self.model_805_label.pack(side=tk.LEFT)
        self.model_805_addr_var = tk.StringVar(value="-")
        ttk.Entry(scan_frame, textvariable=self.model_805_addr_var, width=8, state="readonly").pack(side=tk.LEFT)
        
        self.model_899_label = ttk.Label(scan_frame, text="899:")
        self.model_899_label.pack(side=tk.LEFT)
        self.model_899_addr_var = tk.StringVar(value="-")
        ttk.Entry(scan_frame, textvariable=self.model_899_addr_var, width=8, state="readonly").pack(side=tk.LEFT)

        # 总控按钮（只保留读取全部）
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        self.read_all_tables_btn = ttk.Button(btn_frame, text=self.language_manager.get_text("read_all_tables"), 
                                 command=self.read_all_tables)
        self.read_all_tables_btn.pack(side=tk.LEFT)

        # 新增：自动读取全部表格勾选框
        self.auto_read_all_var = tk.BooleanVar(value=False)
        self.auto_read_all_check = ttk.Checkbutton(
            btn_frame, text="自动读取全部表格", variable=self.auto_read_all_var, command=self.on_auto_read_all_changed
        )
        self.auto_read_all_check.pack(side=tk.LEFT, padx=(10, 0))

        # 创建标签页容器
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 数据显示区 - 使用标签页
        self.data_tables = {}
        self.table_frames = {}
        self.read_all_btns = {}  # 保存每个表格的读全部按钮

        for table_id in [802, 805, 899]:
            # 创建标签页
            tab_frame = ttk.Frame(self.notebook)
            self.notebook.add(tab_frame, text=f"{self.language_manager.get_text('table')}{table_id}")
            self.table_frames[table_id] = tab_frame

            # 按钮区（只保留读全部）
            btn_frame = ttk.Frame(tab_frame)
            btn_frame.pack(fill=tk.X, anchor="w", pady=(5, 0))
            read_all_btn = ttk.Button(btn_frame, text=self.language_manager.get_text("read_all"), 
                                 command=lambda tid=table_id: self.read_table(tid))
            read_all_btn.pack(side=tk.LEFT)
            self.read_all_btns[table_id] = read_all_btn  # 保存按钮引用

            # 内容区+滚动条
            content_frame = ttk.Frame(tab_frame)
            content_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

            canvas = tk.Canvas(content_frame)
            scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)

            canvas_window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

            scrollable_frame.bind(
                "<Configure>",
                lambda e, c=canvas: c.configure(scrollregion=c.bbox("all"))
            )
            
            def on_canvas_configure(event, canvas=canvas, window_id=canvas_window_id, sf=scrollable_frame):
                canvas.itemconfig(window_id, width=event.width)
                sf.configure(width=event.width)
                canvas.configure(scrollregion=canvas.bbox("all"))
            
            canvas.bind('<Configure>', on_canvas_configure)
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            dt = DataTableFrame(scrollable_frame, table_id, self.sunspec_protocol, 
                              self.modbus_client, main_window=self, language_manager=self.language_manager)
            dt.pack(fill=tk.BOTH, expand=True)
            self.data_tables[table_id] = dt

        # 日志框
        self.log_frame = ttk.LabelFrame(main_frame, text=self.language_manager.get_text("log"), padding=5)
        self.log_frame.pack(fill=tk.BOTH, expand=False, pady=(5, 0))
        
        self.log_text = scrolledtext.ScrolledText(self.log_frame, height=8, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 日志控制按钮
        log_btn_frame = ttk.Frame(self.log_frame)
        log_btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.clear_log_btn = ttk.Button(log_btn_frame, text=self.language_manager.get_text("clear_log"), 
                                   command=self.clear_log)
        self.clear_log_btn.pack(side=tk.LEFT)
        
        # 自动保存日志勾选框 - 默认不勾选
        self.auto_save_log_var = tk.BooleanVar(value=False)
        self.auto_save_check = ttk.Checkbutton(log_btn_frame, text=self.language_manager.get_text("auto_save_log"), 
                                          variable=self.auto_save_log_var, command=self.on_auto_save_changed)
        self.auto_save_check.pack(side=tk.LEFT, padx=(10, 0))
        
        # 隐藏文件路径相关变量
        self.log_file_path = None
        self.log_file_var = tk.StringVar(value="未选择文件")

        # 状态栏
        self.status_var = tk.StringVar(value=self.language_manager.get_text("ready"))
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def change_language(self, language):
        """切换语言"""
        if self.language_manager.set_language(language):
            # 只更新界面文本，不重建窗口
            self.update_interface_text()

    def update_interface_text(self):
        """更新界面文本"""
        # 更新窗口标题
        self.root.title(self.language_manager.get_text("window_title"))
        
        # 更新状态栏
        self.status_var.set(self.language_manager.get_text("ready"))
        
        # 更新连接设置框架
        self.update_connection_frame_text()
        
        # 更新扫描按钮文本
        self.update_scan_buttons_text()
        
        # 更新表格标题
        self.update_table_titles()
        
        # 更新日志区域文本
        self.update_log_area_text()
        
        # 更新数据表格文本
        self.update_data_tables_text()

    def update_connection_frame_text(self):
        """更新连接设置框架的文本"""
        # 更新连接框架的语言
        self.connection_frame.update_language(self.language_manager)
        
        # 更新按钮文本
        self.connection_frame.connect_rtu_btn.configure(text=self.language_manager.get_text("connect_rtu"))
        self.connection_frame.disconnect_btn.configure(text=self.language_manager.get_text("disconnect"))

    def update_scan_buttons_text(self):
        """更新扫描按钮的文本"""
        if hasattr(self, 'scan_base_btn'):
            self.scan_base_btn.configure(text=self.language_manager.get_text("scan_base_address"))
        if hasattr(self, 'scan_model_btn'):
            self.scan_model_btn.configure(text=self.language_manager.get_text("scan_model_address"))
        if hasattr(self, 'current_base_addr_label'):
            self.current_base_addr_label.configure(text=self.language_manager.get_text("current_base_address"))
        if hasattr(self, 'read_all_tables_btn'):
            self.read_all_tables_btn.configure(text=self.language_manager.get_text("read_all_tables"))
    
        # 更新基地址变量的默认值
        if hasattr(self, 'base_addr_var'):
            if self.base_addr_var.get() == "未扫描" or self.base_addr_var.get() == "Not Scanned":
                self.base_addr_var.set(self.language_manager.get_text("not_scanned"))

    def update_table_titles(self):
        """更新表格标题"""
        for i, table_id in enumerate([802, 805, 899]):
            self.notebook.tab(i, text=f"{self.language_manager.get_text('table')}{table_id}")

    def update_log_area_text(self):
        """更新日志区域的文本"""
        # 更新日志框架标题
        if hasattr(self, 'log_frame'):
            self.log_frame.configure(text=self.language_manager.get_text("log"))
        
        # 更新按钮文本
        if hasattr(self, 'clear_log_btn'):
            self.clear_log_btn.configure(text=self.language_manager.get_text("clear_log"))
        if hasattr(self, 'auto_save_check'):
            self.auto_save_check.configure(text=self.language_manager.get_text("auto_save_log"))
        if hasattr(self, 'auto_read_all_check'):
            self.auto_read_all_check.configure(text=self.language_manager.get_text("auto_read_all_tables"))

    def update_data_tables_text(self):
        """更新数据表格的文本"""
        # 更新每个表格的读全部按钮
        for table_id, read_all_btn in self.read_all_btns.items():
            read_all_btn.configure(text=self.language_manager.get_text("read_all"))
        
        # 更新数据表格的语言
        for table_id, data_table in self.data_tables.items():
            data_table.update_language(self.language_manager)

    def bind_events(self):
        """绑定事件"""
        # 绑定连接框架的按钮事件
        self.connection_frame.connect_rtu_btn.config(command=self.connect_rtu)
        self.connection_frame.disconnect_btn.config(command=self.disconnect)
        
        # 初始化按钮状态
        self.update_connection_buttons_state()

    def update_connection_buttons_state(self):
        """更新连接按钮状态"""
        is_connected = self.modbus_client.is_connected()
        
        # 更新连接框架的按钮状态
        self.connection_frame.update_buttons_state(is_connected)

    def get_default_log_file(self):
        """获取默认日志文件路径"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"SunSpec_Log_{timestamp}.txt"

    def on_auto_save_changed(self):
        """自动保存日志勾选框状态改变时的处理"""
        if self.auto_save_log_var.get():
            # 勾选时，直接弹出文件选择对话框
            self.select_log_file()
        else:
            # 取消勾选时，清除文件路径
            self.log_file_path = None
            self.log_file_var.set("未选择文件" if self.language_manager.get_current_language() == "zh_CN" else "No file selected")

    def select_log_file(self):
        """选择日志文件"""
        from tkinter import filedialog
        import time
        import os
        
        # 生成默认文件名
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        default_filename = f"SunSpec_Log_{timestamp}.txt"
        
        # 获取用户文档目录作为默认保存位置
        try:
            import os.path
            default_dir = os.path.expanduser("~/Documents")
            if not os.path.exists(default_dir):
                default_dir = os.getcwd()  # 如果文档目录不存在，使用当前目录
        except:
            default_dir = os.getcwd()
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="选择日志文件" if self.language_manager.get_current_language() == "zh_CN" else "Select Log File",
            initialdir=default_dir,
            initialfile=default_filename
        )
        if filename:
            self.log_file_path = filename
            self.log_file_var.set(filename)
            # 立即创建文件
            try:
                with open(self.log_file_path, 'w', encoding='utf-8') as f:
                    f.write(f"# SunSpec Modbus Log File\n")
                    f.write(f"# Created: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"# Language: {self.language_manager.get_current_language()}\n")
                    f.write(f"# File: {os.path.basename(filename)}\n\n")
            except Exception as e:
                messagebox.showerror("错误", f"创建日志文件失败: {str(e)}")
                # 如果创建失败，取消勾选
                self.auto_save_log_var.set(False)
        else:
            # 如果用户取消选择，取消勾选
            self.auto_save_log_var.set(False)

    def log_message(self, message):
        """添加日志消息"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        # 显示在GUI中
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
        # 如果开启了自动保存且有有效的文件路径，则写入文件
        if (hasattr(self, 'auto_save_log_var') and self.auto_save_log_var.get() and 
            hasattr(self, 'log_file_path') and self.log_file_path):
            try:
                with open(self.log_file_path, 'a', encoding='utf-8') as f:
                    f.write(log_entry)
            except Exception as e:
                # 如果写入失败，在GUI中显示错误
                error_msg = f"日志文件写入失败: {str(e)}\n"
                self.log_text.insert(tk.END, error_msg)
                self.log_text.see(tk.END)

    def clear_log(self):
        """清空日志显示区域（不清空文件）"""
        self.log_text.delete(1.0, tk.END)
        
        # 如果开启了自动保存，在日志文件中添加分隔线，但不清空文件内容
        if (hasattr(self, 'auto_save_log_var') and self.auto_save_log_var.get() and 
            hasattr(self, 'log_file_path') and self.log_file_path):
            try:
                import time
                separator = f"\n# ====== 界面日志清空时间: {time.strftime('%Y-%m-%d %H:%M:%S')} ======\n\n"
                with open(self.log_file_path, 'a', encoding='utf-8') as f:
                    f.write(separator)
            except Exception as e:
                # 如果写入分隔线失败，只在界面显示错误，不影响文件内容
                error_msg = f"添加日志分隔线失败: {str(e)}\n"
                self.log_text.insert(tk.END, error_msg)

    def connect_rtu(self):
        """连接RTU Modbus"""
        port = self.connection_frame.rtu_port_var.get()
        baudrate = int(self.connection_frame.baudrate_var.get())
        slave_id = int(self.connection_frame.slave_id_var.get())
        timeout = int(self.connection_frame.timeout_var.get())
        
        if self.modbus_client.connect_rtu(port, baudrate, timeout=timeout):
            # 设置全局slave_id
            self.modbus_client.slave_id = slave_id
            
            self.modbus_client.set_log_callback(self.log_message)
            self.status_var.set(f"RTU连接成功: {port}, 从站ID: {slave_id}")
            self.log_message(f"RTU连接成功: {port}, 从站ID: {slave_id}")
            messagebox.showinfo(self.language_manager.get_text("connection_success"), f"已连接到 {port}, 从站ID: {slave_id}")
            
            # 更新按钮状态
            self.update_connection_buttons_state()
        else:
            self.status_var.set("RTU连接失败")
            self.log_message(f"RTU连接失败: {port}")
            messagebox.showerror(self.language_manager.get_text("connection_failed"), f"无法连接到 {port}")

    def disconnect(self):
        """断开连接"""
        self.modbus_client.disconnect()
        self.status_var.set(self.language_manager.get_text("disconnected"))
        self.log_message(self.language_manager.get_text("disconnected"))
        
        # 更新按钮状态
        self.update_connection_buttons_state()

    def read_all_tables(self):
        if not self.modbus_client.is_connected():
            messagebox.showwarning(self.language_manager.get_text("warning"), 
                                 self.language_manager.get_text("please_connect_first"))
            return
        self.log_message(self.language_manager.get_text("start_reading_all"))
        for table_id in [802, 805, 899]:
            self.read_table(table_id)
        self.log_message(self.language_manager.get_text("all_tables_read_complete"))

    def read_table(self, table_id):
        # 检查是否已连接
        if not self.modbus_client.is_connected():
            messagebox.showwarning(self.language_manager.get_text("warning"), 
                                 self.language_manager.get_text("please_connect_first"))
            return
        
        # 使用扫描到的模型地址
        if hasattr(self, 'model_base_addrs') and table_id in self.model_base_addrs:
            base_addr = self.model_base_addrs[table_id]
            self.log_message(f"读取表格{table_id}，使用扫描地址: {base_addr}")
        else:
            # 如果没有扫描到，使用默认基地址
            base_addr = self.sunspec_protocol.base_address
            self.log_message(f"读取表格{table_id}，使用默认基地址: {base_addr}")
        
        table_info = self.sunspec_protocol.get_table_info(table_id)
        length = table_info["length"]
        data = self.modbus_client.read_holding_registers(base_addr, length)
        if data:
            parsed = self.sunspec_protocol.parse_table_data(table_id, data)
            self.data_tables[table_id].display_data(parsed)
            self.log_message(f"表格{table_id}读取成功")
        else:
            self.log_message(f"表格{table_id}读取失败")

    def scan_base_address(self):
        """扫描SunSpec协议基地址"""
        if not self.modbus_client.is_connected():
            messagebox.showwarning(self.language_manager.get_text("warning"), 
                                 self.language_manager.get_text("please_connect_first"))
            return
        self.log_message(self.language_manager.get_text("start_scanning_base"))
        candidate_addrs = [0, 40000, 50000]
        found = False
        for addr in candidate_addrs:
            data = self.modbus_client.read_holding_registers(addr, 2)
            if data and len(data) == 2:
                bytes_data = (data[0] & 0xFF).to_bytes(1, 'big') + ((data[0] >> 8) & 0xFF).to_bytes(1, 'big') + \
                           (data[1] & 0xFF).to_bytes(1, 'big') + ((data[1] >> 8) & 0xFF).to_bytes(1, 'big')
                try:
                    ascii_str = bytes_data.decode('ascii')
                    hex_str = ' '.join([f"{b:02X}" for b in bytes_data])
                    self.log_message(f"地址{addr}内容: {ascii_str} (hex: {hex_str})")
                    if ascii_str == "SunS":
                        self.sunspec_protocol.base_address = addr
                        self.base_addr_var.set(str(addr))
                        self.log_message(f"发现SunSpec基地址: {addr}")
                        messagebox.showinfo(self.language_manager.get_text("scan_success"), 
                                          f"{self.language_manager.get_text('found_sunspec_base')}: {addr}")
                        found = True
                        break
                except Exception as e:
                    self.log_message(f"地址{addr}解析失败: {e}")
        if not found:
            self.base_addr_var.set(self.language_manager.get_text("not_scanned"))
            self.log_message(self.language_manager.get_text("not_found_sunspec_base"))
            messagebox.showerror(self.language_manager.get_text("scan_failed"), 
                               self.language_manager.get_text("not_found_sunspec_base"))

    def scan_models(self):
        """扫描所有SunSpec模型，找到802/805/899的起始地址"""
        if not self.modbus_client.is_connected():
            messagebox.showwarning(self.language_manager.get_text("warning"), 
                                 self.language_manager.get_text("please_connect_first"))
            return

        base_addr = self.sunspec_protocol.base_address
        addr = base_addr + 2  # Skip "SunS" (ID and Length of SunSpec Common Model)
        model_map = {}
        self.log_message(f"{self.language_manager.get_text('start_scanning_models')}，基地址: {base_addr}")

        while True:
            regs = self.modbus_client.read_holding_registers(addr, 2)
            if not regs or len(regs) < 2:
                self.log_message(f"读取模型ID/LEN失败，地址: {addr}")
                break
            model_id, model_len = regs[0], regs[1]
            self.log_message(f"模型ID: {model_id} LEN: {model_len} @ {addr}")

            if model_id == 0xFFFF and model_len == 0:
                self.log_message("模型链表结束")
                break

            if model_id in [802, 805, 899]:
                model_map[model_id] = addr
                self.sunspec_protocol.set_model_base_address(model_id, addr)

            addr = addr + 2 + model_len

        # 更新GUI显示
        self.model_802_addr_var.set(str(model_map.get(802, "-")))
        self.model_805_addr_var.set(str(model_map.get(805, "-")))
        self.model_899_addr_var.set(str(model_map.get(899, "-")))

        self.model_base_addrs = model_map
        self.log_message(f"{self.language_manager.get_text('scan_complete')}，找到模型: {list(model_map.keys())}")

    def on_auto_read_all_changed(self):
        """自动读取全部表格勾选框状态改变时的处理"""
        if self.auto_read_all_var.get():
            self.start_auto_read_all()
        else:
            self.stop_auto_read_all()

    def start_auto_read_all(self):
        """启动自动读取全部表格"""
        self._auto_read_all_running = True
        self.schedule_auto_read_all()

    def stop_auto_read_all(self):
        """停止自动读取全部表格"""
        self._auto_read_all_running = False

    def schedule_auto_read_all(self):
        """调度自动读取全部表格"""
        if getattr(self, "_auto_read_all_running", False):
            self.read_all_tables()
            # 5秒后再次调用
            self.root.after(5000, self.schedule_auto_read_all)

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        self.stop_auto_read_all()
        self.modbus_client.disconnect()
        self.root.destroy()

def main():
    app = SunSpecGUI()
    app.run()

if __name__ == "__main__":
    main()