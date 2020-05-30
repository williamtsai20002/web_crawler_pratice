# -*- coding: utf-8 -*-
import time, re
import os
import pdfkit
import requests
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from django.utils.text import get_valid_filename
from opencc import OpenCC

def make_query_list():
    query_list = []
    max_page_list = []
    user_query, max_page_ = get_user_input()
    query_list.append(user_query)
    max_page_list.append(max_page_)
    
    while len(user_query) != 0:
        user_query, max_page_ = get_user_input()
        if len(user_query) == 0:
            break
        query_list.append(user_query)
        max_page_list.append(max_page_)
    return query_list, max_page_list

def get_content(wd, query, max_page = 10): # per query
    query_dir_path = search_string_parser(query)
#     print("query_dir_path : ", query_dir_path)
    if not os.path.exists(query_dir_path): # make the file if not exist
        os.makedirs(query_dir_path)
            
    for i in range(max_page):
        href_elements = wd.find_elements_by_xpath("//div[@class='rc']/div[@class='r']/a")
        title_elements = wd.find_elements_by_xpath("//div[@class='rc']/div[@class='r']/a/h3")
        next_page_element = wd.find_element_by_xpath("//td[@aria-level='3'][@role='heading']/a")
        
        content_href = [ele.get_attribute("href") for ele in href_elements]
        title = [ele.text for ele in title_elements]
        next_page_href = next_page_element.get_attribute("href")
        
        page_dir_path = query_dir_path + "\\" + "page" + str(i + 1)
        if not os.path.exists(page_dir_path): # make the file if not exist
            os.makedirs(page_dir_path)
        
        for url, t in zip(content_href, title):
            cc = OpenCC('s2tw')
            t = cc.convert(t)
            t = get_valid_filename(t)
            html_file_name = t + ".html"
            pdf_file_name = t + ".pdf"
#             print("html_file_name : ", html_file_name)
#             print("pdf_file_name : ", pdf_file_name)
            
            save_html(url, page_dir_path + "\\" + html_file_name)
            save_pdf(url, page_dir_path + "\\" + pdf_file_name)
        
        
        
        wd.get(next_page_href)

def get_user_input():
    user_query = input("Search : ")
    if len(user_query) == 0:
        return "", 0
    max_page = -1
    while max_page <= 0:
        try:
            max_page = int(input("Max page ( > 0 ) : "))
        except:
            print("Only input positive integer !!!")
    return user_query, max_page

def search_string_parser(search_string):
    word_list = search_string.split(" ")
    word_list = [ele for ele in word_list if len(ele) > 0]
    query = "_".join(word_list)
    return query

def save_html(url, file_name):
    headers = {'User-Agent': 'User-Agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'}
    response_content = requests.get(url, headers=headers)
    html_content = response_content.text
    with open (file_name, "w", encoding="utf-8") as file:
        file.write(html_content)
    print("end save_html")

def save_pdf(url ,file_name):
    try:
        pdfkit.from_url(url, file_name, configuration=config, options={'javascript-delay':'5000'})
    except Exception as e:
        print("url : ", url)
        print("file_name : ", file_name)
        print(e)
    print("end save_pdf")

if __name__ == "__main__":
    path_wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

    search_url = "https://www.google.com/search?"
    chrome_path = r"C:\Users\Administrator\Desktop\chromedriver_win32\chromedriver"
    wd = webdriver.Chrome(chrome_path)

    query_list, max_page_list = make_query_list()

    for user_query, max_page in zip(query_list, max_page_list):
        wd.get("https://www.google.com")
        search_input = wd.find_element_by_xpath("//input[@aria-label='搜尋'][@type='text']")
        search_input.send_keys(user_query)
        search_input.send_keys(Keys.RETURN)
        time.sleep(5)
        get_content(wd, user_query, max_page)