### 用来获取动态加载网页纯文本内容的工具
### 需下载浏览器驱动器并替换，目前适用于edge

from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from tqdm import tqdm

def get_webpage_text(url, output_file="webpage_text.txt"):
    print("阶段 1: 初始化浏览器...")
    # 设置无头浏览器选项
    edge_options = Options()
    edge_options.add_argument("--headless")  # 无头模式
    edge_options.add_argument("--disable-gpu")
    edge_options.add_argument("--no-sandbox")
    
    # 明确指定 EdgeDriver 路径
    edgedriver_path = "D:\Apps\EdgeDriver\msedgedriver.exe"  # 请替换为您的 EdgeDriver 路径
    service = Service(edgedriver_path)
    
    # 初始化 WebDriver
    try:
        driver = webdriver.Edge(service=service, options=edge_options)
    except Exception as e:
        print(f"初始化浏览器失败: {str(e)}")
        print("请确保 EdgeDriver 路径正确且与 Microsoft Edge 浏览器版本匹配。")
        return None
    
    try:
        print("阶段 2: 加载网页...")
        # 打开网页
        driver.get(url)
        
        # 等待页面主要内容加载（最多等待10秒）
        print("等待页面内容加载...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # 额外等待2秒，确保动态内容加载完成
        print("阶段 3: 等待动态内容加载...")
        for _ in tqdm(range(2), desc="等待动态内容", unit="秒"):
            time.sleep(1)
        
        print("阶段 4: 提取文本内容...")
        # 获取所有可见元素的文本
        elements = driver.find_elements(By.XPATH, "//*[not(self::script) and not(self::style)]")
        text_content = []
        
        # 使用进度条显示文本提取进度
        for element in tqdm(elements, desc="提取可见文本", unit="元素"):
            # 只获取可见元素的文本
            if element.is_displayed():
                text = element.text.strip()
                if text:  # 忽略空文本
                    text_content.append(text)
        
        # 将文本内容合并，保留换行
        full_text = "\n".join(text_content)
        
        print("阶段 5: 保存文本到文件...")
        # 保存到文件
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(full_text)
        
        print(f"完成！文本已保存到 {output_file}")
        return full_text
    
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return None
    
    finally:
        print("阶段 6: 清理并关闭浏览器...")
        driver.quit()

if __name__ == "__main__":
    # 示例用法
    target_url = input("请输入要提取文本的网页URL: ")

    get_webpage_text(target_url)
