#-*- coding:utf-8 -*-

"""
爬取新浪微博的用户信息
功能：用户ID 用户名 粉丝数 关注数 微博数 微博内容

网址：www.weibo.cn 数据量更少相对于 www.weibo.cn


"""
import  time
import re
import  os
import  sys
import codecs
import shutil
import urllib
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.action_chains import ActionChains
#先调用无界面浏览的浏览器 PhantomJS 或Firefox

driver=webdriver.Firefox()
wait=ui.WebDriverWait(driver,10)


#全局变量 文件操作的读写信息
inforead=codecs.open("SinaWeibo_List.txt",'r','utf-8')
infofile=codecs.open("SinaWeibo_Info.txt",'a','utf-8')

def LoginWeibo(username,password):
    try:
        print u'准备登陆weibop.cn网站..'
        driver.get("http://login.weibo.cn/login/")
        elem_user=driver.find_element_by_name("mobile")
        elem_user.send_keys(username) #用户名
        elem_pwd=driver.find_element_by_xpath("/html/body/div[2]/form/div/input[2]")
        elem_pwd.send_keys(password) #密码
        #elem_rem=driver.find_element_by_name("remember")
        #elem_rem.click()

        #重点：暂停时间输入验证码
        time.sleep(30)

        elem_sub=driver.find_element_by_name("submit")
        elem_sub.click() # 点击登陆
        time.sleep(2)

        # 获取Coockie 推荐 http://www.cnblogs.com/fnng/p/3269450.html
        #print driver.current_url
        """
        print driver.get_cookies() #获得cookie信息dict 存储
        print u'输出cookie对应的键值信息:'
        for cookie in driver.get_cookies():
            for key in cookie:
                print key,cookie[key]
        """
        print u'登陆成功...'
    except Exception,e:
        print "Error:",e
    finally:
        print u'End loginWeibo!\n\n'

##第二步访问 个人页面 http://weibo.cn/3985356869
def VisitPersonPage(user_id):
    try:
        global  infofile
        print u'准备访问个人网站...'
        driver.get("http://weibo.cn/"+user_id)
        ##第一步直接获取用户昵称 微博数 关注数 粉丝数
        #str_name.text 是unicode 编码类型

        #用户id
        print u'个人详细信息'
        print '*****************'
        print u'用户id:'+user_id

        #昵称
        str_name=driver.find_element_by_xpath("//div[@class='ut']")
        str_t=str_name.text.split(" ")
        num_name=str_t[0]
        print u'昵称:'+num_name

        #微博数 除了个人主页外 它默认直接显示微博数 无超链接
        str_wb=driver.find_element_by_xpath("//div[@class='tip2']")
        pattern=r"\d+\.?\d*"  #正则提取"微博[0]" 但r"(\[.*?\])"总含[]
        guid=re.findall(pattern,str_wb.text,re.S|re.M)
        print str_wb.text
        for value in guid:
            num_wb=int(value)
            break
        print '微博数:'+str(num_wb)

        #关注数目
        str_gz=driver.find_element_by_xpath("//div[@class='tip2']/a[1]")
        num_gz_temp=re.findall(pattern,str_gz.text,re.S|re.M)
        num_gz=int(num_gz_temp[0])
        print '关注数目:'+str(num_gz)

        #粉丝数目
        str_fs = driver.find_element_by_xpath("//div[@class='tip2']/a[2]")
        num_fs_temp = re.findall(pattern, str_fs.text, re.S | re.M)
        num_fs = int(num_fs_temp[0])
        print '粉丝数目:' + str(num_fs)
        # ***************************************************************************
        # No.2 文件操作写入信息
        # ***************************************************************************

        infofile.write('=====================================================================\r\n')
        infofile.write(u'用户: ' + user_id + '\r\n')
        infofile.write(u'昵称: ' + num_name + '\r\n')
        infofile.write(u'微博数: ' + str(num_wb) + '\r\n')
        infofile.write(u'关注数: ' + str(num_gz) + '\r\n')
        infofile.write(u'粉丝数: ' + str(num_fs) + '\r\n')
        infofile.write(u'微博内容: ' + '\r\n\r\n')

        #获取微博内容
        #http://weibo.cn/+ user_id +?filter=0&page=1
        # 其中 filter=0 表示全部 filter=1 表示原创

        print '\n'
        print u'获取微博的内容信息'
        num=1
        while num<=5:
            url_wb='http://weibo.cn/'+user_id+"?filter=0&page="+str(num)
            driver.get(url_wb)
            info_temp="//div[@class='c'][{0}]"
            num_temp=1
            while True:
                info = driver.find_element_by_xpath(info_temp.format(num_temp)).text
                print info
                if u'设置:皮肤.图片' not in info:
                    if info.startswith(u'转发'):
                        print u'转发微博'
                        infofile.write(u'转发微博\r\n')
                    else:
                        print u'原创微博'
                        infofile.write(u'原创微博\r\n')

                    # 获取最后一个点赞数 因为转发是后有个点赞数
                    str1 = info.split(u"赞")[-1]
                    if str1:
                        val1 = re.match(r'\[(.*?)\]', str1).groups()[0]
                        print re.match(r'\[(.*?)\]', str1).groups()
                        print u'点赞数: ' + val1
                        infofile.write(u'点赞数: ' + str(val1) + '\r\n')

                    str2 = info.split(u"转发")[-1]
                    if str2:
                        val2 = re.match(r'\[(.*?)\]', str2).groups()[0]
                        print u'转发数: ' + val2
                        infofile.write(u'转发数: ' + str(val2) + '\r\n')

                    str3 = info.split(u"评论")[-1]
                    if str3:
                        val3 = re.match(r'\[(.*?)\]', str3).groups()[0]
                        print u'评论数: ' + val3
                        infofile.write(u'评论数: ' + str(val3) + '\r\n')

                    str4 = info.split(u"收藏 ")[-1]
                    flag = str4.find(u"来自")
                    print u'时间: ' + str4[:flag]
                    infofile.write(u'时间: ' + str4[:flag] + '\r\n')

                    print u'微博内容:'
                    print info[:info.rindex(u" 赞")]  # 后去最后一个赞位置
                    infofile.write(info[:info.rindex(u" 赞")] + '\r\n')
                    infofile.write('\r\n')
                    print '\n'
                else:
                    print u'跳过', '\n'
                    break

                num_temp+=1
            num+=1

    except Exception, e:
        print "Error: ", e
    finally:
        print u'VisitPersonPage!\n'
        print '**********************************************\n'

if __name__ == '__main__':

    #定义变量
    username = '124123'             #输入你的用户名
    password = '******'               #输入你的密码
    #操作函数
    LoginWeibo(username, password)      #登陆微博
    user_id=inforead.readline()
    while user_id!="":
        user_id=user_id.rstrip('\r\n')
        VisitPersonPage(user_id)
        user_id=inforead.readline()
    infofile.close()
    inforead.close()
