#!/usr/bin/env python3
"""
使用Python的PDF库读取PDF文件的脚本
"""
import os
import sys

# 尝试导入PDF库
try:
    import PyPDF2
except ImportError:
    print("PyPDF2未安装，正在安装...")
    import subprocess
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "PyPDF2"], check=True)
        import PyPDF2
        print("PyPDF2安装成功！")
    except subprocess.SubprocessError as e:
        print(f"安装PyPDF2失败: {str(e)}")
        sys.exit(1)

# 读取PDF文件
def read_pdf(pdf_file):
    """读取PDF文件内容"""
    print(f"正在读取PDF文件: {pdf_file}")
    
    if not os.path.exists(pdf_file):
        print(f"错误: 文件不存在 - {pdf_file}")
        return
    
    try:
        with open(pdf_file, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            num_pages = len(reader.pages)
            print(f"PDF文件页数: {num_pages}")
            
            text_content = []
            for page_num in range(num_pages):
                print(f"\n=== 第 {page_num + 1} 页 ===")
                page = reader.pages[page_num]
                text = page.extract_text()
                print(text)
                text_content.append(text)
            
            return text_content
    except Exception as e:
        print(f"读取PDF文件时出错: {str(e)}")
        return None

# 保存文本内容到文件
def save_text_to_file(text_content, output_file):
    """保存文本内容到文件"""
    print(f"正在保存文本内容到文件: {output_file}")
    
    try:
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write('\n\n'.join(text_content))
        print(f"文本内容保存成功: {output_file}")
    except Exception as e:
        print(f"保存文本内容时出错: {str(e)}")

# 测试读取PDF文件
if __name__ == "__main__":
    # PDF文件列表
    pdf_files = [
        "docs/广东省梅州市梅县梅西田福刘氏乾正公族谱世系.pdf",
        "docs/梅西田福刘氏族谱世系.pdf"
    ]
    
    # 读取每个PDF文件
    for pdf_file in pdf_files:
        if os.path.exists(pdf_file):
            print(f"\n" + "="*80)
            print(f"处理PDF文件: {pdf_file}")
            print("="*80)
            
            text_content = read_pdf(pdf_file)
            if text_content:
                output_file = os.path.splitext(pdf_file)[0] + ".txt"
                save_text_to_file(text_content, output_file)
        else:
            print(f"错误: PDF文件不存在 - {pdf_file}")
