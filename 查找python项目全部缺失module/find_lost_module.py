import ast
import pkgutil
import sys
import os
from pathlib import Path

def get_imported_modules(file_path):
    """解析 Python 文件，获取所有导入的模块名"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            tree = ast.parse(file.read(), filename=file_path)
        
        modules = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    modules.add(name.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    modules.add(node.module.split('.')[0])
        
        return modules
    except SyntaxError as e:
        print(f"解析文件 {file_path} 时出现语法错误: {e}")
        return set()
    except Exception as e:
        print(f"解析文件 {file_path} 时出现错误: {e}")
        return set()

def get_all_python_files(directory, exclude_dirs=None):
    """获取目录下所有 Python 文件的路径，排除指定目录"""
    if exclude_dirs is None:
        exclude_dirs = ['.vscode', 'node_modules', '__pycache__']
    
    python_files = []
    for root, dirs, files in os.walk(directory):
        # 排除指定的目录
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files

def get_project_modules_and_packages(directory, exclude_dirs=None):
    """获取项目内部模块名（基于 .py 文件）和包名（基于包含 __init__.py 的目录）"""
    python_files = get_all_python_files(directory, exclude_dirs)
    project_modules = set()
    project_packages = set()

    # 收集 .py 文件的模块名
    for file_path in python_files:
        module_name = Path(file_path).stem
        if module_name != '__init__':  # 排除 __init__.py 本身
            project_modules.add(module_name)

    # 收集包含 __init__.py 的目录作为包
    for root, dirs, _ in os.walk(directory):
        if exclude_dirs:
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for dir_name in dirs:
            init_path = os.path.join(root, dir_name, '__init__.py')
            if os.path.isfile(init_path):
                project_packages.add(dir_name)

    return project_modules, project_packages

def check_installed_modules():
    """获取所有已安装的模块"""
    return {name for _, name, _ in pkgutil.iter_modules()}

def find_missing_modules(directory, exclude_dirs=None):
    """查找项目中缺失的外部模块，排除内部模块和包"""
    # 获取所有 Python 文件
    python_files = get_all_python_files(directory, exclude_dirs)
    if not python_files:
        print("目录中未找到 Python 文件。")
        return

    print(f"找到 {len(python_files)} 个 Python 文件。")
    
    # 获取项目内部模块和包
    project_modules, project_packages = get_project_modules_and_packages(directory, exclude_dirs)
    print(f"找到 {len(project_modules)} 个项目内部模块：{', '.join(sorted(project_modules))}")
    print(f"找到 {len(project_packages)} 个项目内部包：{', '.join(sorted(project_packages))}")

    # 收集所有导入的模块
    all_modules = set()
    for file_path in python_files:
        print(f"正在解析: {file_path}")
        modules = get_imported_modules(file_path)
        all_modules.update(modules)

    # 获取已安装的模块
    installed_modules = check_installed_modules()

    # 查找缺失的模块（排除内置模块、项目内部模块和包）
    missing_modules = all_modules - installed_modules - set(sys.builtin_module_names) - project_modules - project_packages

    # 输出结果
    if missing_modules:
        print("\n缺失的外部模块：")
        for module in sorted(missing_modules):
            print(f"  - {module}")
        print("\n可以使用以下命令安装缺失的模块：")
        print(f"pip install {' '.join(sorted(missing_modules))}")
    else:
        print("\n所有外部模块都已安装。")

if __name__ == "__main__":
    # 默认检查当前目录
    project_dir = input("请输入项目目录路径（按回车使用当前目录）：").strip() or "."
    
    if not os.path.isdir(project_dir):
        print(f"错误：'{project_dir}' 不是有效的目录。")
        sys.exit(1)
    
    # 允许用户指定要排除的目录
    exclude_input = input("请输入要排除的目录（多个目录用逗号分隔，留空使用默认排除 .vscode,node_modules,__pycache__）：").strip()
    exclude_dirs = exclude_input.split(',') if exclude_input else None
    
    print(f"\n正在扫描目录：{project_dir}")
    find_missing_modules(project_dir, exclude_dirs)
