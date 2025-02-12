# 名称：SkyEyeSearch
# 功能：特定路径下搜索各深度文件中是否包含特定字符并显示结果
# 作者：叁七
# 最后更新日期：2025/2/12
# 性能还是太差了
import os
import threading
from concurrent.futures import ThreadPoolExecutor
import tkinter as tk
from tkinter import ttk, filedialog
from tkinter.messagebox import showinfo
import mimetypes
from queue import Queue
import time

def is_text_file(path):
    mime_type, _ = mimetypes.guess_type(path)
    return mime_type == 'text/plain'

def search_file(path, queue, search_string, max_file_size, file_count):
    if not os.path.isfile(path):
        return

    file_count[0] += 1  # 增加文件计数

    if os.path.getsize(path) > max_file_size:
        return

    if not is_text_file(path):
        return
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as file:
            for line in file:
                if search_string in line:
                    relative_path = os.path.relpath(path, os.path.dirname(__file__))
                    queue.put(f"Found in: {relative_path}")
                    return
    except Exception as e:
        print(f"Error reading file {path}: {e}")
def search_files(root, search_string, max_file_size, max_workers, target_filename):
    queue = Queue()
    found_files = []
    file_count = [0]  # 初始化文件计数器

    def worker_done_callback(future):
        result = future.result()
        if result:
            found_files.append(result)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for dirpath, _, filenames in os.walk(root):
            for filename in filenames:
                if target_filename and filename != target_filename:  # 如果文件名不匹配，则跳过
                    continue
                file_path = os.path.join(dirpath, filename)
                if target_filename:
                    result_text.insert(tk.END, f"{file_path}\n")
                future = executor.submit(search_file, file_path, queue, search_string, max_file_size, file_count)
                future.add_done_callback(worker_done_callback)

    while not queue.empty():
        found_files.append(queue.get())

    return found_files, file_count[0]  # 返回找到的文件列表和文件计数

def start_search():
    root_dir = entry_path.get()
    search_string = entry_keyword.get()
    target_filename = entry_filename.get()  # 获取目标文件名
    try:
        max_file_size = int(entry_size.get()) * 1024
        max_workers = int(entry_workers.get())
    except ValueError:
        showinfo("输入错误", "文件大小限制和并发数必须是数字")
        return

    if not os.path.isdir(root_dir):
        showinfo("路径错误", "请输入有效的目录路径")
        return

    start_time = time.time()
    found_files, total_files = search_files(root_dir, search_string, max_file_size, max_workers, target_filename)
    end_time = time.time()

    
    for file in found_files:
        result_text.insert(tk.END, file + '\n')
    result_text.insert(tk.END, f"查找完成\n")
    result_text.insert(tk.END, f"耗时: {end_time - start_time:.2f} seconds\n")
    result_text.insert(tk.END, f"一共查找了: {total_files} 个文件\n")  # 显示一共查找了多少文件
    # 自动滚动到最底部
    result_text.yview(tk.END)
def select_directory():
    path = filedialog.askdirectory()
    entry_path.delete(0, tk.END)
    entry_path.insert(0, path)

# 创建主窗口
root = tk.Tk()
root.title("SkyEyeSearch")

# 创建变量持有默认值
default_path = tk.StringVar(value=os.path.dirname(__file__))  # 使用当前文件所在目录作为默认路径
default_keyword = tk.StringVar(value="target")
default_size = tk.StringVar(value="100")
default_workers = tk.StringVar(value="16")
default_filename = tk.StringVar(value="")  # 默认为空

# 创建和布局控件
label_path = ttk.Label(root, text="选择目录：")
entry_path = ttk.Entry(root, width=70, textvariable=default_path)
button_browse = ttk.Button(root, text="浏览", command=select_directory)

label_keyword = ttk.Label(root, text="搜索关键词：")
entry_keyword = ttk.Entry(root, width=70, textvariable=default_keyword)

label_filename = ttk.Label(root, text="目标文件名（可选）：")
entry_filename = ttk.Entry(root, width=70, textvariable=default_filename)

label_size = ttk.Label(root, text="文件大小限制（KB）：")
entry_size = ttk.Entry(root, width=10, textvariable=default_size)

label_workers = ttk.Label(root, text="并发数：")
entry_workers = ttk.Entry(root, width=10, textvariable=default_workers)

  # 添加文件名输入框

button_start = ttk.Button(root, text="开始搜索", command=start_search)

# 创建结果文本框及其滚动条
result_text = tk.Text(root, width=90, height=20)
scrollbar = ttk.Scrollbar(root, orient="vertical", command=result_text.yview)
result_text.configure(yscrollcommand=scrollbar.set)


# 布局控件
label_path.grid(row=0, column=0, padx=5, pady=5)
entry_path.grid(row=0, column=1, padx=5, pady=5)
button_browse.grid(row=0, column=2, padx=5, pady=5)

label_keyword.grid(row=1, column=0, padx=5, pady=5)
entry_keyword.grid(row=1, column=1, padx=5, pady=5)

label_size.grid(row=2, column=0, padx=5, pady=5)
entry_size.grid(row=2, column=1, padx=5, pady=5)

label_workers.grid(row=3, column=0, padx=5, pady=5)
entry_workers.grid(row=3, column=1, padx=5, pady=5)

label_filename.grid(row=4, column=0, padx=5, pady=5)  # 添加文件名标签
entry_filename.grid(row=4, column=1, padx=5, pady=5)  # 添加文件名输入框

button_start.grid(row=5, column=0, columnspan=3, pady=10)

result_text.grid(row=6, column=0, columnspan=3, padx=5, pady=5)  # 调整结果文本框的位置

# 运行主循环
root.mainloop()
