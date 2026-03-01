#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime, timedelta
import calendar
import os
import threading
import sys
from main import PeopleDailyCrawler

try:
    from config import DEFAULT_OUTPUT_PATH, FILENAME_TEMPLATE
except ImportError:
    DEFAULT_OUTPUT_PATH = os.getcwd()
    FILENAME_TEMPLATE = "人民日报_{date}.pdf"


class CalendarPopup(tk.Toplevel):
    def __init__(self, parent, callback=None):
        super().__init__(parent)
        self.callback = callback
        self.title("选择日期")
        self.geometry("300x350")
        self.resizable(False, False)
        
        self.current_date = datetime.now()
        self.selected_date = None
        
        self.setup_ui()
        
    def setup_ui(self):
        nav_frame = ttk.Frame(self)
        nav_frame.pack(pady=10, fill="x", padx=10)
        
        ttk.Button(nav_frame, text="◀", width=3, command=self.prev_month).pack(side="left")
        
        self.month_label = ttk.Label(nav_frame, text="", font=("SimHei", 12, "bold"))
        self.month_label.pack(side="left", expand=True)
        
        ttk.Button(nav_frame, text="▶", width=3, command=self.next_month).pack(side="right")
        
        days_frame = ttk.Frame(self)
        days_frame.pack(pady=5, fill="x", padx=10)
        
        days = ["日", "一", "二", "三", "四", "五", "六"]
        for i, day in enumerate(days):
            lbl = ttk.Label(days_frame, text=day, width=4, anchor="center")
            lbl.grid(row=0, column=i)
        
        self.calendar_frame = ttk.Frame(self)
        self.calendar_frame.pack(pady=5, fill="both", expand=True, padx=10)
        
        self.update_calendar()
        
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10, fill="x", padx=10)
        
        ttk.Button(button_frame, text="今天", command=self.select_today).pack(side="left", padx=5)
        ttk.Button(button_frame, text="昨天", command=self.select_yesterday).pack(side="left", padx=5)
        ttk.Button(button_frame, text="确定", command=self.confirm).pack(side="right", padx=5)
        
    def update_calendar(self):
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()
        
        year = self.current_date.year
        month = self.current_date.month
        
        self.month_label.config(text=f"{year}年{month}月")
        
        cal = calendar.monthcalendar(year, month)
        today = datetime.now().date()
        
        for week_idx, week in enumerate(cal):
            for day_idx, day in enumerate(week):
                if day == 0:
                    lbl = ttk.Label(self.calendar_frame, text="", width=4)
                else:
                    date_str = f"{year}-{month:02d}-{day:02d}"
                    btn = ttk.Button(self.calendar_frame, text=str(day), 
                                    width=4, command=lambda d=date_str: self.select_date(d))
                    
                    current_cal_date = datetime(year, month, day).date()
                    if current_cal_date == today:
                        btn.config(style="Today.TButton")
                    elif current_cal_date > today:
                        btn.state(["disabled"])
                    
                    btn.grid(row=week_idx, column=day_idx, padx=2, pady=2)
    
    def select_date(self, date_str):
        self.selected_date = date_str
        for widget in self.calendar_frame.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.state(["!pressed"])
    
    def select_today(self):
        self.selected_date = datetime.now().strftime("%Y-%m-%d")
        self.confirm()
    
    def select_yesterday(self):
        yesterday = datetime.now() - timedelta(days=1)
        self.selected_date = yesterday.strftime("%Y-%m-%d")
        self.confirm()
    
    def prev_month(self):
        if self.current_date.month == 1:
            self.current_date = self.current_date.replace(year=self.current_date.year - 1, month=12)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month - 1)
        self.update_calendar()
    
    def next_month(self):
        if self.current_date.month == 12:
            self.current_date = self.current_date.replace(year=self.current_date.year + 1, month=1)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month + 1)
        self.update_calendar()
    
    def confirm(self):
        if self.selected_date and self.callback:
            self.callback(self.selected_date)
        self.destroy()


class SimpleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("人民日报爬取工具")
        self.root.geometry("680x600")
        
        self.center_window()
        
        self.crawler = PeopleDailyCrawler()
        self.is_running = False
        
        self.setup_ui()
        
    def get_recent_dates(self):
        dates = []
        today = datetime.now()
        for i in range(30):
            date = today - timedelta(days=i)
            dates.append(date.strftime("%Y-%m-%d"))
        return dates
        
    def setup_ui(self):
        tk.Label(self.root, text="人民日报每日版面爬取与PDF合并工具", 
                font=("SimHei", 14, "bold")).pack(pady=10)
        
        frame1 = tk.Frame(self.root)
        frame1.pack(pady=10, padx=20, fill="x")
        
        tk.Label(frame1, text="日期:", font=("SimHei", 10)).pack(side="left")
        
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        recent_dates = self.get_recent_dates()
        
        date_entry_frame = tk.Frame(frame1)
        date_entry_frame.pack(side="left", padx=10)
        
        self.date_combobox = ttk.Combobox(date_entry_frame, textvariable=self.date_var, 
                                          values=recent_dates, width=15, state="readonly")
        self.date_combobox.pack(side="left")
        
        tk.Button(date_entry_frame, text="📅 选择日期", command=self.show_calendar, 
                 font=("SimHei", 9)).pack(side="left", padx=5)
        
        quick_dates_frame = tk.Frame(frame1)
        quick_dates_frame.pack(side="left", padx=10)
        
        tk.Button(quick_dates_frame, text="今天", command=lambda: self.set_quick_date(0), 
                 font=("SimHei", 9)).pack(side="left", padx=2)
        tk.Button(quick_dates_frame, text="昨天", command=lambda: self.set_quick_date(1), 
                 font=("SimHei", 9)).pack(side="left", padx=2)
        tk.Button(quick_dates_frame, text="前天", command=lambda: self.set_quick_date(2), 
                 font=("SimHei", 9)).pack(side="left", padx=2)
        
        frame2 = tk.Frame(self.root)
        frame2.pack(pady=10, padx=20, fill="x")
        
        tk.Label(frame2, text="输出路径:", font=("SimHei", 10)).pack(side="left")
        
        self.output_var = tk.StringVar(value=DEFAULT_OUTPUT_PATH)
        self.output_entry = tk.Entry(frame2, textvariable=self.output_var, width=40)
        self.output_entry.pack(side="left", padx=10)
        
        tk.Button(frame2, text="浏览", command=self.browse_output).pack(side="left")
        
        self.start_button = tk.Button(self.root, text="开始爬取", command=self.start_crawling, 
                                      font=("SimHei", 12), width=20, bg="#4CAF50", fg="white")
        self.start_button.pack(pady=20)
        
        tk.Label(self.root, text="日志输出:", font=("SimHei", 10)).pack(pady=(10, 0), anchor="w", padx=20)
        
        self.log_text = tk.Text(self.root, height=15, font=("Consolas", 9))
        self.log_text.pack(pady=5, padx=20, fill="both", expand=True)
        
        self.log_text.insert("end", "程序已启动！请设置参数后点击开始爬取。\n")
        
    def show_calendar(self):
        calendar_popup = CalendarPopup(self.root, self.set_date)
        calendar_popup.transient(self.root)
        calendar_popup.grab_set()
        self.root.wait_window(calendar_popup)
        
    def set_date(self, date_str):
        self.date_var.set(date_str)
        
    def set_quick_date(self, days_ago):
        date = datetime.now() - timedelta(days=days_ago)
        self.date_var.set(date.strftime("%Y-%m-%d"))
        
    def browse_output(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF文件", "*.pdf"), ("所有文件", "*.*")],
            initialfile=os.path.basename(self.output_var.get()) if os.path.basename(self.output_var.get()) else "人民日报.pdf",
            initialdir=os.path.dirname(self.output_var.get()) if os.path.dirname(self.output_var.get()) else os.getcwd()
        )
        if filename:
            self.output_var.set(filename)
            
    def log(self, message):
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.root.update()
        
    def validate_output_path(self, output_path, date_str=None):
        if not output_path:
            return None
        
        if os.path.isdir(output_path):
            if date_str:
                filename = FILENAME_TEMPLATE.replace("{date}", date_str)
                filename = filename.replace("{paper_name}", "人民日报")
                output_path = os.path.join(output_path, filename)
            else:
                output_path = os.path.join(output_path, "人民日报.pdf")
        elif not output_path.lower().endswith(".pdf"):
            output_path = output_path + ".pdf"
        
        return output_path
        
    def start_crawling(self):
        if self.is_running:
            messagebox.showwarning("提示", "任务正在运行中...")
            return
            
        date_str = self.date_var.get().strip()
        output_path = self.output_var.get().strip()
        
        if not date_str:
            messagebox.showerror("错误", "请输入日期")
            return
            
        if not output_path:
            messagebox.showerror("错误", "请选择输出路径")
            return
            
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("错误", "日期格式不正确，请使用 YYYY-MM-DD 格式")
            return
            
        output_path = self.validate_output_path(output_path, date_str)
        if not output_path:
            messagebox.showerror("错误", "输出路径无效")
            return
            
        self.output_var.set(output_path)
            
        self.is_running = True
        self.start_button.config(state="disabled", text="爬取中...", bg="#ccc")
        self.log_text.delete(1.0, "end")
        
        thread = threading.Thread(target=self.run_task, args=(date_str, output_path))
        thread.daemon = True
        thread.start()
        
    def run_task(self, date_str, output_path):
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        
        class LogRedirector:
            def __init__(self, gui):
                self.gui = gui
            def write(self, text):
                self.gui.log_text.insert("end", text)
                self.gui.log_text.see("end")
                self.gui.root.update()
            def flush(self):
                pass
        
        try:
            sys.stdout = LogRedirector(self)
            sys.stderr = LogRedirector(self)
            
            print(f"开始爬取 {date_str} 的人民日报...")
            print(f"输出路径: {output_path}")
            
            success = self.crawler.run(date_str, output_path)
            
            self.root.after(0, lambda: self.on_finished(success))
        except Exception as e:
            print(f"\n错误: {e}")
            import traceback
            print(traceback.format_exc())
            self.root.after(0, lambda: self.on_finished(False))
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def on_finished(self, success):
        self.is_running = False
        self.start_button.config(state="normal", text="开始爬取", bg="#4CAF50")
        
        if success:
            messagebox.showinfo("成功", f"爬取完成！\n文件已保存到:\n{self.output_var.get()}")
        else:
            messagebox.showerror("失败", "爬取失败，请查看日志")


def main():
    root = tk.Tk()
    app = SimpleGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
