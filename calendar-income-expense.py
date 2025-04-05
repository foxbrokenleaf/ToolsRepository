import tkinter as tk
from tkinter import messagebox
import calendar
from datetime import datetime


class CalendarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("收入支出日历")
        self.current_year = datetime.now().year
        self.current_month = datetime.now().month
        self.income_entries = {}
        self.fixed_expense = tk.StringVar()
        self.fixed_expense.set("0")

        # 导航栏
        self.prev_button = tk.Button(root, text="上月", command=self.prev_month)
        self.prev_button.pack(side=tk.LEFT)
        self.next_button = tk.Button(root, text="下月", command=self.next_month)
        self.next_button.pack(side=tk.LEFT)
        self.month_label = tk.Label(root, text=f"{calendar.month_name[self.current_month]} {self.current_year}")
        self.month_label.pack(side=tk.LEFT)

        # 日历框架
        self.calendar_frame = tk.Frame(root)
        self.calendar_frame.pack()

        # 显示日历
        self.show_calendar()

        # 固定支出输入框
        self.expense_frame = tk.Frame(root)
        self.expense_frame.pack()
        tk.Label(self.expense_frame, text="每日固定支出:").pack(side=tk.LEFT)
        tk.Entry(self.expense_frame, textvariable=self.fixed_expense).pack(side=tk.LEFT)
        tk.Button(self.expense_frame, text="更新", command=self.update_remaining).pack(side=tk.LEFT)

    def show_calendar(self):
        # 清除之前的日历
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        # 显示星期名称
        days = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        for i, day in enumerate(days):
            tk.Label(self.calendar_frame, text=day).grid(row=0, column=i)

        # 获取当前月的日历
        cal = calendar.monthcalendar(self.current_year, self.current_month)

        for week_num, week in enumerate(cal):
            for day_num, day in enumerate(week):
                if day != 0:
                    day_frame = tk.Frame(self.calendar_frame)
                    day_frame.grid(row=week_num + 1, column=day_num)
                    tk.Label(day_frame, text=day).pack()
                    income_entry = tk.Entry(day_frame)
                    income_entry.pack()
                    income_entry.bind("<FocusOut>", lambda event, d=day: self.update_remaining())
                    self.income_entries[day] = income_entry
                    remaining_label = tk.Label(day_frame, text="剩余: 0")
                    remaining_label.pack()

    def prev_month(self):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.month_label.config(text=f"{calendar.month_name[self.current_month]} {self.current_year}")
        self.show_calendar()

    def next_month(self):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.month_label.config(text=f"{calendar.month_name[self.current_month]} {self.current_year}")
        self.show_calendar()

    def update_remaining(self):
        try:
            fixed_expense = float(self.fixed_expense.get())
            remaining = 0
            for day in sorted(self.income_entries.keys()):
                entry = self.income_entries[day]
                try:
                    income = float(entry.get())
                except ValueError:
                    income = 0
                remaining = remaining + income - fixed_expense
                remaining_label = entry.master.winfo_children()[2]
                remaining_label.config(text=f"剩余: {remaining:.2f}")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")


if __name__ == "__main__":
    root = tk.Tk()
    app = CalendarApp(root)
    root.mainloop()
    