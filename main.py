#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import re
import sys
import tempfile
import shutil
from datetime import datetime
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfMerger

try:
    from config import DEFAULT_OUTPUT_PATH, FILENAME_TEMPLATE
except ImportError:
    DEFAULT_OUTPUT_PATH = os.getcwd()
    FILENAME_TEMPLATE = "人民日报_{date}.pdf"


class PeopleDailyCrawler:
    def __init__(self):
        self.base_url = "http://paper.people.com.cn"
        self.layout_base_url = "http://paper.people.com.cn/rmrb/pc/layout"
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Connection": "keep-alive"
        }
        self.session.headers.update(self.headers)

    def get_paper_date_url(self, date_str):
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            year_month = date_obj.strftime("%Y%m")
            day = date_obj.strftime("%d")
            return f"{self.layout_base_url}/{year_month}/{day}/node_01.html"
        except ValueError:
            print(f"错误: 日期格式不正确，请使用 YYYY-MM-DD 格式，例如: 2026-03-01")
            sys.exit(1)

    def get_all_pages(self, first_page_url):
        try:
            response = self.session.get(first_page_url, timeout=30)
            response.raise_for_status()
            response.encoding = "utf-8"
            
            soup = BeautifulSoup(response.text, "lxml")
            
            page_urls = []
            page_links = soup.find_all("a", href=re.compile(r"node_\d+\.html"))
            
            seen = set()
            for link in page_links:
                href = link.get("href", "")
                if href and href not in seen and "pad" not in href:
                    seen.add(href)
                    if not href.startswith("http"):
                        if href.startswith("/"):
                            full_url = f"{self.base_url}{href}"
                        else:
                            base_path = "/".join(first_page_url.split("/")[:-1])
                            full_url = f"{base_path}/{href}"
                    else:
                        full_url = href
                    if "pad" not in full_url:
                        page_urls.append(full_url)
            
            page_urls = sorted(page_urls, key=lambda x: int(re.search(r"node_(\d+)\.html", x).group(1)) if re.search(r"node_(\d+)\.html", x) else 0)
            
            if not page_urls:
                page_urls.append(first_page_url)
            
            print(f"找到 {len(page_urls)} 个版面")
            return page_urls
        except Exception as e:
            print(f"获取版面列表时出错: {e}")
            return []

    def get_pdf_url(self, page_url):
        try:
            response = self.session.get(page_url, timeout=30)
            response.raise_for_status()
            response.encoding = "utf-8"
            
            soup = BeautifulSoup(response.text, "lxml")
            
            pdf_link = soup.find("a", string="PDF下载", href=re.compile(r"\.pdf$", re.IGNORECASE))
            
            if not pdf_link:
                pdf_link = soup.find("a", href=re.compile(r"\.pdf$", re.IGNORECASE))
            
            if pdf_link:
                pdf_href = pdf_link.get("href", "")
                return urljoin(page_url, pdf_href)
            
            print(f"未在 {page_url} 中找到PDF链接")
            return None
        except Exception as e:
            print(f"获取PDF链接时出错: {e}")
            return None

    def download_pdf(self, pdf_url, save_path):
        try:
            print(f"正在下载: {pdf_url}")
            response = self.session.get(pdf_url, timeout=60, stream=True)
            response.raise_for_status()
            
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            print(f"下载完成: {save_path}")
            return True
        except Exception as e:
            print(f"下载PDF时出错: {e}")
            return False

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
        
    def merge_pdfs(self, pdf_files, output_path):
        try:
            output_path = self.validate_output_path(output_path)
            if not output_path:
                print("错误: 输出路径无效")
                return False
                
            print(f"正在合并 {len(pdf_files)} 个PDF文件...")
            merger = PdfMerger()
            
            for pdf_file in pdf_files:
                if os.path.exists(pdf_file):
                    merger.append(pdf_file)
            
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            
            merger.write(output_path)
            merger.close()
            
            print(f"合并完成: {output_path}")
            return True
        except Exception as e:
            import traceback
            print(f"合并PDF时出错: {e}")
            print(f"详细信息: {traceback.format_exc()}")
            return False

    def run(self, date_str, output_path):
        output_path = self.validate_output_path(output_path, date_str)
        if not output_path:
            print("错误: 输出路径无效")
            return False
            
        print(f"输出路径: {output_path}")
        temp_dir = tempfile.mkdtemp(prefix="peopledaily_")
        
        try:
            first_page_url = self.get_paper_date_url(date_str)
            print(f"正在访问: {first_page_url}")
            
            page_urls = self.get_all_pages(first_page_url)
            if not page_urls:
                print("错误: 未找到任何版面")
                return False
            
            pdf_files = []
            for i, page_url in enumerate(page_urls, 1):
                print(f"\n处理第 {i} 版...")
                pdf_url = self.get_pdf_url(page_url)
                
                if pdf_url:
                    pdf_filename = f"page_{i:02d}.pdf"
                    pdf_save_path = os.path.join(temp_dir, pdf_filename)
                    
                    if self.download_pdf(pdf_url, pdf_save_path):
                        pdf_files.append(pdf_save_path)
            
            if pdf_files:
                if self.merge_pdfs(pdf_files, output_path):
                    print(f"\n成功！人民日报 {date_str} 已保存到: {output_path}")
                    return True
            else:
                print("错误: 未能下载任何PDF文件")
                return False
        finally:
            self.cleanup(temp_dir)
        
        return False

    def cleanup(self, temp_dir):
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        except Exception as e:
            print(f"清理临时文件时出错: {e}")


def main():
    parser = argparse.ArgumentParser(description="人民日报每日版面爬取与PDF合并工具")
    parser.add_argument("--date", "-d", type=str, 
                        default=datetime.now().strftime("%Y-%m-%d"),
                        help="日期，格式为 YYYY-MM-DD，默认为今天")
    parser.add_argument("--output", "-o", type=str, 
                        default=DEFAULT_OUTPUT_PATH,
                        help="输出PDF文件路径或目录（如果是目录会自动生成文件名）")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("人民日报每日版面爬取与PDF合并工具")
    print("=" * 60)
    print(f"日期: {args.date}")
    print(f"输出路径: {args.output}")
    print()
    
    crawler = PeopleDailyCrawler()
    success = crawler.run(args.date, args.output)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
