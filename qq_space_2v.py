from selenium import webdriver
import time
import requests
import json
import re
import pandas as pd
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import os

#模拟自动登录qq空间
def login():
    d = DesiredCapabilities.CHROME
    d['loggingPrefs'] = {'performance': 'ALL'}
    browser=webdriver.Chrome('C:/Users/Lenovo/AppData/Local/Google/Chrome/Application/chromedriver.exe',desired_capabilities=d)
    browser.get('https://qzone.qq.com/')
    # time.sleep(2)
    browser.switch_to.frame('login_frame')
    time.sleep(2)
    browser.find_element_by_id('switcher_plogin').click()
    user=input('请输入qq账号：').strip()
    pwd=input('请输入qq密码：').strip()
    browser.find_element_by_id('u').send_keys(user)
    browser.find_element_by_id('p').send_keys(pwd)
    browser.find_element_by_id('login_button').click()
    # time.sleep(10)
    input('请在浏览器上查看是否需要验证，按回车继续>>')
    cookies={}
    for cookie in browser.get_cookies():
        cookies[cookie['name']]=cookie['value']
    # print(cookies)
    log_str = str(browser.get_log('performance'))
    # print(log_str)
    qzonetoken=re.findall(r'qzonetoken=(\w*?)\"',log_str)[-1]
    g_tk = re.findall(r'g_tk=(\d*?)\"',log_str)[-1]
    argvs_dict={'host_id':user,'cookies':cookies,'qzonetoken':qzonetoken,'g_tk':g_tk}
    argvs_json=json.dumps(argvs_dict)
    with open('login_argvs.json','w') as f:
        f.write(argvs_json)
    # browser.close()
    print('登录成功！')

#检查登录参数是否失效，如果失效则模拟自动登录qq空间
def is_login():
        url = 'https://user.qzone.qq.com/proxy/domain/taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6'
        data = {
            'uin': host_id,
            'inCharset': 'utf-8',
            'outCharset': 'utf-8',
            'hostUin': host_id,
            'notice': '0',
            'sort': '0',
            'pos': 0,
            'num': '20',
            'cgi_host': 'https://user.qzone.qq.com/proxy/domain/taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6',
            'code_version': '1',
            'format': 'jsonp',
            'need_private_comment': '1',
            'g_tk': g_tk,
            'qzonetoken': qzonetoken,
            'g_tk': g_tk
        }
        res = requests.get(url=url, params=data, cookies=cookies)
        html = res.text
        # print(html)
        if '请先登录空间' in html:
            print('登录参数已失效，开始模拟自动登录')
            login()
        else:
            print('登录参数有效')

#爬取单页好友说说数据
def get_say(pos,data_dict):
    url='https://user.qzone.qq.com/proxy/domain/taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6'
    data={
        'uin':uid,
        'inCharset':'utf-8',
        'outCharset':'utf-8',
        'hostUin':host_id,
        'notice':'0',
        'sort':'0',
        'pos':pos,
        'num':'20',
        'cgi_host':'https://user.qzone.qq.com/proxy/domain/taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6',
        'code_version':'1',
        'format':'jsonp',
        'need_private_comment':'1',
        'g_tk':g_tk,
        'qzonetoken':qzonetoken,
        'g_tk':g_tk
    }
    res=requests.get(url=url,params=data,cookies=cookies)
    html=res.text
    html=re.findall(r'_Callback\((.*)\)',html)[0]
    html=json.loads(html)
    # print(html)
    msglist=html['msglist']
    # print(msglist)
    name=html['usrinfo']['name']   # 用户名称
    for msg in msglist:
        mark_name1 = msg.get('name', '')  #好友备注
        try:
            content=msg.get('conlist')[0].get('con')
        except:
            content=''    #说说内容
        createTime = msg.get('createTime','')  # 发表日期
        cmtnum=msg.get('cmtnum','')   #评论数
        fwdnum=msg.get('fwdnum','')   #转发数
        source_name=msg.get('source_name','')   #设备名称
        print(content)
        # print(createTime)
        # print(cmtnum)
        # print(fwdnum)
        # print(source_name)
        data_dict['用户名称'].append(name)
        data_dict['好友备注'].append(mark_name1)
        data_dict['说说内容'].append(content)
        data_dict['发表日期'].append(createTime)
        data_dict['评论数'].append(cmtnum)
        data_dict['转发数'].append(fwdnum)
        data_dict['设备名称'].append(source_name)
    global mark_name
    mark_name = mark_name1

#循环爬取指定页数的说说数据并保存到excel
def save_say(page_num):
    data_dict={'用户名称':[],'好友备注':[],'说说内容':[],'发表日期':[],'评论数':[],'转发数':[],'设备名称':[]}
    for p in range(0,page_num):
        try:
            pos=p*20
            get_say(pos=pos,data_dict=data_dict)
        except Exception as e:
            print(e)
    df_data=pd.DataFrame(data_dict)
    df_data.to_excel(mark_name+'的说说.xlsx',index=False)
    # return df_data


#获取全部好友的qq号
def get_friend_qq_number():
    qq_number_list=[]
    headers={
        'referer':'https://mail.qq.com/',
        'cookie':'0.8440450815589364; pgv_pvi=2142509056; pgv_pvid=626657216; RK=8vb8BJSwGh; ptcz=7f28cb713b8b382a12674975a829fdaa36cf374831535010316075c43b08f74b; tvfe_boss_uuid=68ce0f4a9c99126a; o_cookie=1104599577; LW_uid=S1M5G4v40884a5x375Y0U3F694; LW_sid=u1R5h514Q054o1O5A4T5c72206; eas_sid=21Y587Q3E3e83698G8U4D1I0R6; ptisp=ctc; pgv_info=ssid=s7894354869; p_uin=o1104599577; wimrefreshrun=0&; qm_logintype=qq; qm_antisky=1104599577&49a477bc4263286c8c624e9068ad35c1d866caa108603bd0e801e0f89f785875; qm_flag=0; qqmail_alias=1104599577@qq.com; qm_domain=https://mail.qq.com; foxacc=1104599577&0; edition=mail.qq.com; __guid=103811228.551819255506474600.1575206066269.7986; CCSHOW=000001; webp=1; pgv_si=s6499487744; qm_authimgs_id=3; qm_verifyimagesession=h019e369b2c1b4b142c69328a7b1d0a34dd60bb640977b0446a45b2221fa2c9e17a74d4ca828b2edaa5; ptui_loginuin=1104599577; uin=o1104599577; skey=@CwAR37qyu; pt4_token=eSQiJdvFybqPBqyWsONgqjyMoQ8OvpuaKfh3e1YAdzQ_; p_skey=8UQ8bBdB1KhYGoDteZo6kghpApdRKaDPNTpSds659*4_; sid=1104599577&a98ef7c3f5ed1b9cf14a8b95f1cc2fc4,cy-6wPp9BIz8.; qm_username=1104599577; qm_ptsk=1104599577&@CwAR37qyu; ssl_edition=sail.qq.com; qm_loginfrom=1104599577&wpt; username=1104599577&1104599577; monitor_count=6; new_mail_num=1104599577&232',
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
    }
    data={
        'sid':'s6pEqXPNu22OMHEs',
        'operate':'view',
        't':'contact',
        'view':'qq',
        'groupid':'1000000'
    }
    res=requests.get(url='https://mail.qq.com/cgi-bin/laddr_list',headers=headers,params=data)
    html=res.text
    # print(html)
    qqs=re.findall(r'(\d{6,13})@qq\.com',html)
    print(qqs)


if __name__=='__main__':
    # if not os.path.exists('login_argvs.json'):
    #     login()
    # with open('login_argvs.json','r') as f:
    #     argvs_dict=json.loads(f.read())
    #     host_id=argvs_dict['host_id']
    #     cookies=argvs_dict['cookies']
    #     qzonetoken=argvs_dict['qzonetoken']
    #     g_tk = argvs_dict['g_tk']
    # is_login()
    # uid = input('请输入好友QQ号：').strip()
    # page_num=int(input('请输入爬取的页数(每页20条说说)：'))
    # save_say(page_num=page_num)

    get_friend_qq_number()
