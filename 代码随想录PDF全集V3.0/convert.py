import pymupdf4llm
import os

def pdf_to_markdown_simple(pdf_path, output_md_path=None):
    """
    使用 pymupdf4llm 将 PDF 转换为 Markdown
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"文件不存在: {pdf_path}")
    
    print(f"正在转换: {pdf_path} ...")
    
    # 核心转换函数
    md_text = pymupdf4llm.to_markdown(pdf_path)
    
    # 确定输出路径
    if output_md_path is None:
        output_md_path = os.path.splitext(pdf_path)[0] + ".md"
    
    # 写入文件
    with open(output_md_path, "w", encoding="utf-8") as f:
        f.write(md_text)
    
    print(f"转换成功！文件已保存至: {output_md_path}")
    return output_md_path

if __name__ == "__main__":
    # 示例用法
    input_file = "1.《代码随想录》数组（V3.0）.pdf"  # 请替换为你的 PDF 文件名
    try:
        # 如果没有真实文件，这段代码会报错，请确保目录下有 PDF 文件
        pdf_to_markdown_simple(input_file)
        # print("请将 'example.pdf' 替换为您实际的文件路径运行。")
    except Exception as e:
        print(f"发生错误: {e}")