#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modbus客户端模块
"""

from pymodbus.client import ModbusTcpClient, ModbusSerialClient
from pymodbus.exceptions import ModbusException
import time

class ModbusClient:
    """Modbus客户端类"""
    
    def __init__(self):
        self.client = None
        self.connected = False
        self.connection_type = None
        self.timeout = 10
        self.retries = 3
        
    def connect_tcp(self, host, port=502, timeout=10):
        """连接TCP Modbus"""
        try:
            self.timeout = timeout
            self.client = ModbusTcpClient(host, port, timeout=timeout)
            self.connected = self.client.connect()
            self.connection_type = 'TCP'
            return self.connected
        except Exception as e:
            print(f"TCP连接失败: {e}")
            return False
    
    def connect_rtu(self, port, baudrate=9600, parity='N', stopbits=1, bytesize=8, timeout=10):
        """连接RTU Modbus"""
        try:
            self.timeout = timeout
            self.client = ModbusSerialClient(
                port=port,
                baudrate=baudrate,
                parity=parity,
                stopbits=stopbits,
                bytesize=bytesize,
                timeout=timeout
            )
            self.connected = self.client.connect()
            self.connection_type = 'RTU'
            return self.connected
        except Exception as e:
            print(f"RTU连接失败: {e}")
            return False
    
    def disconnect(self):
        """断开连接"""
        if self.client:
            self.client.close()
            self.connected = False
            self.connection_type = None
    
    def is_connected(self):
        """检查连接状态"""
        return self.connected and self.client and self.client.is_socket_open()
    
    def read_holding_registers(self, address, count, slave=1):
        """读取保持寄存器"""
        if not self.is_connected():
            return None
        
        for attempt in range(self.retries):
            try:
                result = self.client.read_holding_registers(address, count, slave=slave)
                if result.isError():
                    print(f"读取寄存器错误: {result}")
                    continue
                return result.registers
            except Exception as e:
                print(f"读取寄存器失败 (尝试 {attempt + 1}/{self.retries}): {e}")
                if attempt < self.retries - 1:
                    time.sleep(0.1)
        
        return None
    
    def write_holding_register(self, address, value, slave=1):
        """写入单个保持寄存器"""
        if not self.is_connected():
            return False
        
        for attempt in range(self.retries):
            try:
                result = self.client.write_register(address, value, slave=slave)
                if result.isError():
                    print(f"写入寄存器错误: {result}")
                    continue
                return True
            except Exception as e:
                print(f"写入寄存器失败 (尝试 {attempt + 1}/{self.retries}): {e}")
                if attempt < self.retries - 1:
                    time.sleep(0.1)
        
        return False
    
    def write_holding_registers(self, address, values, slave=1):
        """写入多个保持寄存器"""
        if not self.is_connected():
            return False
        
        for attempt in range(self.retries):
            try:
                result = self.client.write_registers(address, values, slave=slave)
                if result.isError():
                    print(f"写入寄存器错误: {result}")
                    continue
                return True
            except Exception as e:
                print(f"写入寄存器失败 (尝试 {attempt + 1}/{self.retries}): {e}")
                if attempt < self.retries - 1:
                    time.sleep(0.1)
        
        return False
    
    def read_input_registers(self, address, count, slave=1):
        """读取输入寄存器"""
        if not self.is_connected():
            return None
        
        for attempt in range(self.retries):
            try:
                result = self.client.read_input_registers(address, count, slave=slave)
                if result.isError():
                    print(f"读取输入寄存器错误: {result}")
                    continue
                return result.registers
            except Exception as e:
                print(f"读取输入寄存器失败 (尝试 {attempt + 1}/{self.retries}): {e}")
                if attempt < self.retries - 1:
                    time.sleep(0.1)
        
        return None
    
    def get_connection_info(self):
        """获取连接信息"""
        if not self.connected:
            return "未连接"
        
        if self.connection_type == 'TCP':
            return f"TCP: {self.client.host}:{self.client.port}"
        elif self.connection_type == 'RTU':
            return f"RTU: {self.client.port}"
        else:
            return "未知连接类型" 