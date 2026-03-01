#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
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


class CalendarWidget(ttk.Frame):
    def __init__(self, parent, callback=None, toggle_callback=None):
        super().__init__(parent)
        self.callback = callback
        self.toggle_callback = toggle_callback
        
        self.current_date = datetime.now()
        self.selected_date = None
        
        self.setup_ui()
        
    def setup_ui(self):
        nav_frame = ttk.Frame(self)
        nav_frame.pack(pady=5, fill="x")
        
        ttk.Button(nav_frame, text="◀", width=3, command=self.prev_month).pack(side="left")
        
        self.month_label = ttk.Label(nav_frame, text="", font=("Microsoft YaHei", 11, "bold"))
        self.month_label.pack(side="left", expand=True)
        
        ttk.Button(nav_frame, text="▶", width=3, command=self.next_month).pack(side="right")
        
        days_frame = ttk.Frame(self)
        days_frame.pack(pady=5, fill="x")
        
        days = ["日", "一", "二", "三", "四", "五", "六"]
        for i, day in enumerate(days):
            lbl = ttk.Label(days_frame, text=day, width=4, anchor="center")
            lbl.grid(row=0, column=i, padx=2, pady=2)
        
        self.calendar_frame = ttk.Frame(self)
        self.calendar_frame.pack(pady=5, fill="both", expand=True)
        
        self.update_calendar()
        
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=5, fill="x")
        
        ttk.Button(button_frame, text="今天", command=self.select_today).pack(side="left", padx=2)
        ttk.Button(button_frame, text="昨天", command=self.select_yesterday).pack(side="left", padx=2)
        ttk.Button(button_frame, text="收起", command=self.collapse).pack(side="right", padx=2)
        
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
        if self.callback:
            self.callback(date_str)
        self.collapse()
    
    def select_today(self):
        self.selected_date = datetime.now().strftime("%Y-%m-%d")
        if self.callback:
            self.callback(self.selected_date)
        self.collapse()
    
    def select_yesterday(self):
        yesterday = datetime.now() - timedelta(days=1)
        self.selected_date = yesterday.strftime("%Y-%m-%d")
        if self.callback:
            self.callback(self.selected_date)
        self.collapse()
    
    def collapse(self):
        self.pack_forget()
        if self.toggle_callback:
            self.toggle_callback()
    
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


class TextRedirector:
    def __init__(self, widget):
        self.widget = widget

    def write(self, text):
        try:
            self.widget.insert(tk.END, text)
            self.widget.see(tk.END)
            self.widget.update_idletasks()
        except:
            pass

    def flush(self):
        pass


class PeopleDailyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("人民日报每日版面爬取与PDF合并工具")
        self.root.geometry("750x700")
        
        self.root.minsize(600, 550)
        
        self.center_window()
        
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass
        
        self.crawler = PeopleDailyCrawler()
        self.is_running = False
        self.calendar_visible = False
        
        self.setup_ui()
        
    def get_recent_dates(self):
        dates = []
        today = datetime.now()
        for i in range(30):
            date = today - timedelta(days=i)
            dates.append(date.strftime("%Y-%m-%d"))
        return dates
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        title_label = ttk.Label(main_frame, text="人民日报每日版面爬取与PDF合并工具", 
                                 font=("Microsoft YaHei", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        ttk.Label(main_frame, text="日期:", font=("Microsoft YaHei", 10)).grid(row=1, column=0, sticky=tk.W, pady=5)
        
        date_frame = ttk.Frame(main_frame)
        date_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        recent_dates = self.get_recent_dates()
        
        date_entry_frame = ttk.Frame(date_frame)
        date_entry_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        self.date_combobox = ttk.Combobox(date_entry_frame, textvariable=self.date_var, 
                                           values=recent_dates, width=20, state="readonly", font=("Microsoft YaHei", 10))
        self.date_combobox.pack(side=tk.LEFT)
        
        self.toggle_calendar_btn = ttk.Button(date_entry_frame, text="📅 选择日期", command=self.toggle_calendar)
        self.toggle_calendar_btn.pack(side=tk.LEFT, padx=5)
        
        quick_dates_frame = ttk.Frame(date_frame)
        quick_dates_frame.pack(side=tk.LEFT, padx=10)
        
        ttk.Button(quick_dates_frame, text="今天", command=lambda: self.set_quick_date(0)).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_dates_frame, text="昨天", command=lambda: self.set_quick_date(1)).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_dates_frame, text="前天", command=lambda: self.set_quick_date(2)).pack(side=tk.LEFT, padx=2)
        
        self.calendar_container = ttk.Frame(main_frame)
        self.calendar_container.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        self.calendar_container.grid_remove()
        
        self.calendar_widget = CalendarWidget(self.calendar_container, self.set_date, self._hide_calendar)
        
        ttk.Label(main_frame, text="输出路径:", font=("Microsoft YaHei", 10)).grid(row=3, column=0, sticky=tk.W, pady=5)
        
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        output_frame.columnconfigure(0, weight=1)
        
        self.output_var = tk.StringVar(value=DEFAULT_OUTPUT_PATH)
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_var, font=("Microsoft YaHei", 10))
        self.output_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(output_frame, text="浏览...", command=self.browse_output).grid(row=0, column=1)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        self.start_button = ttk.Button(button_frame, text="开始爬取", command=self.start_crawling, width=20)
        self.start_button.pack()
        
        ttk.Label(main_frame, text="日志输出:", font=("Microsoft YaHei", 10)).grid(row=5, column=0, sticky=tk.W, pady=(10, 5))
        
        self.log_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=20, font=("Consolas", 9))
        self.log_text.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        main_frame.rowconfigure(6, weight=1)
        
        self.stdout_redirector = TextRedirector(self.log_text)
        
        print("GUI初始化完成！请设置日期和输出路径，然后点击开始爬取。")
        
    def toggle_calendar(self):
        if self.calendar_visible:
            self._hide_calendar()
        else:
            self._show_calendar()
    
    def _show_calendar(self):
        self.calendar_container.grid()
        self.calendar_widget.pack(fill="x", padx=10, pady=5)
        self.toggle_calendar_btn.config(text="📅 收起日历")
        self.calendar_visible = True
    
    def _hide_calendar(self):
        self.calendar_widget.pack_forget()
        self.calendar_container.grid_remove()
        self.toggle_calendar_btn.config(text="📅 选择日期")
        self.calendar_visible = False
        
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
            messagebox.showwarning("警告", "任务正在运行中，请稍候...")
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
        self.start_button.config(state="disabled", text="爬取中...")
        self.log_text.delete(1.0, tk.END)
        
        thread = threading.Thread(target=self.run_crawling, args=(date_str, output_path))
        thread.daemon = True
        thread.start()
        
    def run_crawling(self, date_str, output_path):
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        
        try:
            sys.stdout = self.stdout_redirector
            sys.stderr = self.stdout_redirector
            
            success = self.crawler.run(date_str, output_path)
            
            self.root.after(0, lambda: self.on_finished(success))
        except Exception as e:
            print(f"\n发生错误: {e}")
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
        self.start_button.config(state="normal", text="开始爬取")
        
        if success:
            messagebox.showinfo("成功", f"爬取完成！\n文件已保存到:\n{self.output_var.get()}")
        else:
            messagebox.showerror("失败", "爬取失败，请查看日志获取详细信息")


def main():
    print("正在启动GUI...")
    root = tk.Tk()
    
    try:
        root.iconbitmap(default="")
    except:
        pass
    
    app = PeopleDailyGUI(root)
    
    print("GUI已启动！")
    root.mainloop()


if __name__ == "__main__":
    main()
