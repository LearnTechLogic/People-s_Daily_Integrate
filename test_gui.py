#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from datetime import datetime, timedelta

print("Python版本:", sys.version)
print("正在导入tkinter...")

try:
    import tkinter as tk
    from tkinter import ttk, messagebox
    print("tkinter导入成功！")
    
    print("\n正在创建测试窗口...")
    root = tk.Tk()
    root.title("测试窗口 - 日期选择")
    root.geometry("500x400")
    
    label = ttk.Label(root, text="如果您能看到这个窗口，说明tkinter工作正常！", font=("Arial", 12))
    label.pack(pady=20)
    
    def get_recent_dates():
        dates = []
        today = datetime.now()
        for i in range(30):
            date = today - timedelta(days=i)
            dates.append(date.strftime("%Y-%m-%d"))
        return dates
    
    date_frame = ttk.Frame(root)
    date_frame.pack(pady=20)
    
    ttk.Label(date_frame, text="选择日期:").pack(side="left", padx=5)
    
    date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
    recent_dates = get_recent_dates()
    
    date_combobox = ttk.Combobox(date_frame, textvariable=date_var, 
                                   values=recent_dates, width=15, state="normal")
    date_combobox.pack(side="left", padx=5)
    
    ttk.Label(date_frame, text="(可下拉选择或手动输入)", foreground="gray").pack(side="left", padx=5)
    
    def on_click():
        selected_date = date_var.get()
        messagebox.showinfo("测试", f"您选择的日期是: {selected_date}")
    
    button = ttk.Button(root, text="测试日期选择", command=on_click)
    button.pack(pady=30)
    
    info_label = ttk.Label(root, text="功能说明:\n1. 点击下拉箭头查看最近30天\n2. 也可以直接手动输入日期\n3. 格式: YYYY-MM-DD", 
                           justify="center", font=("Arial", 10))
    info_label.pack(pady=20)
    
    print("测试窗口已创建，正在显示...")
    print("如果窗口没有显示，请检查是否被最小化或隐藏。")
    print("\n按 Ctrl+C 可以在终端中断程序。")
    
    root.mainloop()
    
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保您的Python安装包含tkinter。")
except Exception as e:
    print(f"发生错误: {e}")
    import traceback
    traceback.print_exc()
