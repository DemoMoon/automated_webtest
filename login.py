# -*- coding: utf-8 -*-
# 加载webdriver模块
from selenium import webdriver
from time import sleep
import random
from math import floor
from modern import session, Users, UsersInfo
from Util import parse_config, get_redis, getsmscode, getidcard
from selenium.webdriver.support.select import Select

__author__ = 'yingxue'

# 解析配置文件
config = parse_config()
# 链接Redis数据库
redisClient = get_redis(config)
'''
注册前操作步骤:
    1.查询测试用户[mobile]是否存在[wb_users表]
    2.查询测试用户[user_id]信息是否存在[wb_users_info表]
    3.删除测试用户信息[wb_users_info表]
    4.删除测试用户[wb_users表]
'''
queryUsers = session.query(Users)
mobileNumber = config.get('user', 'mobile')
users = queryUsers.filter(Users.mobile == mobileNumber).scalar()
if users is not None:
    queryUsersInfo = session.query(UsersInfo)
    usersInfo = queryUsersInfo.filter(UsersInfo.user_id == users.id).scalar()
    if usersInfo is not None:
        session.delete(usersInfo)
        session.flush()
    session.delete(users)
    session.flush()
    session.commit()
else:
    print '开始注册......'

domain = config.get('common', 'domain')
password = config.get('user', 'password')
title = config.get('common', 'title')
provinceName = config.get('common', 'provinceName')


# 注册
def register():
    # 使用Chrome浏览器
    driver = webdriver.Chrome()
    # 测试网址
    driver.get(domain)
    assert title in driver.title
    # 从首页跳转到注册页面
    driver.find_element_by_xpath("//a[@href='" + domain + "/auth/register']").click()
    sleep(2)
    # 随机起一个昵称，e.g：test002
    driver.find_element_by_id("nickname").send_keys('test' + str(floor(random.random() * 1000)))
    nicknameMsg = driver.find_element_by_id("nicknameMsg").text
    if not nicknameMsg.strip():
        print '合法昵称......'
    else:
        print '非合法昵称......'
        # 截图功能保留到当前目录
        driver.save_screenshot("validate_error.png")
        driver.quit()
        return
    # 填写配置的手机号
    driver.find_element_by_id("mobile").send_keys(mobileNumber)
    mobileMsg = driver.find_element_by_id("mobileMsg").text
    if not mobileMsg.strip():
        print '合法手机号......'
    else:
        print '非合法手机号......'
        # 截图功能保留到当前目录
        driver.save_screenshot("validate_error.png")
        driver.quit()
        return
    # 填写登录密码
    driver.find_element_by_id("password").send_keys(password)
    # 填写确认密码
    driver.find_element_by_id("password2").send_keys(password)
    # 触发发送短信验证码单击事件
    driver.find_element_by_id("getMobileVerfiyButton").click()
    sleep(2)
    # 填写手机短信验证码
    driver.find_element_by_id("mobileVerify").send_keys(redisClient.get('sms_verify' + mobileNumber))
    # 填写推荐人
    driver.find_element_by_id("invitorMobile").send_keys("18801485734")
    sleep(1)
    # 触发注册单击事件
    driver.find_element_by_id("regButton").click()
    print '注册中......'
    sleep(0.5)
    print '注册成功......'
    sleep(0.5)
    print '登录成功......'
    sleep(0.5)
    print '正在跳转到实名认证页面......'
    sleep(3)
    # 填写真实姓名
    driver.find_element_by_id("realName").send_keys(unicode(config.get('verified', 'realName')).decode("utf-8"))
    # 填写身份证号
    idCard = getidcard()
    if idCard is None:
        # 截图功能保留到当前目录
        driver.save_screenshot("idCard_error.png")
        driver.quit()
        return
    driver.find_element_by_id("idCard").send_keys(idCard)
    # 触发立即认证单击事件
    driver.find_element_by_id("realnameCertButton").click()
    print '实名认证中......'
    idCardMsg = driver.find_element_by_id("idCardMsg").text
    if not idCardMsg.strip():
        print '实名认证成功......'
    else:
        print '实名认证失败......'
        #截图功能保留到当前目录
        driver.save_screenshot("realNameCert_error.png")
        driver.quit()
        return

    sleep(3)
    print '开始绑卡中......'
    """
     --绑卡时获取手机短验码是由新浪方发送短信验证码,我侧无法自动获取短信验证码,故暂时不做绑卡的操作,等待解决方案
    """
    # 填写储蓄卡卡号
    driver.find_element_by_id("bank_account_no").send_keys(config.get('bankCard', 'cardNumber'))
    reservedMobile = config.get('bankCard', 'reservedMobile')
    # 添加自动选择默认的某一个城市的功能
    sel = driver.find_element_by_xpath("//select[@id='province']")
    Select(sel).select_by_value(provinceName)
    sleep(1)
    # 填写银行预留手机号
    driver.find_element_by_id("phone_no").send_keys(reservedMobile)
    # 触发发送短信验证码单击事件
    driver.find_element_by_id("get_valid_code").click()
    sleep(3)
    # 获取绑卡时预留的银行卡手机短信验证码
    smsCode = getsmscode()
    if not smsCode:
        print '获取手机短信成功......'
    else:
        print '获取手机短信失败......'
        # 截图功能保留到当前目录
        driver.save_screenshot("bindCard_error.png")
        driver.quit()
        return
    sleep(1)
    # 填写短信验证码
    driver.find_element_by_id("valid_code").send_keys(smsCode)
    # 触发立即绑定单击事件
    driver.find_element_by_id("bankCardSubmitBtn").click()

    driver.quit()


# 登录
def login():
    driver = webdriver.Chrome()
    driver.get(domain)
    assert '铂诺' in driver.title
    driver.find_element_by_link_text("登录").click()
    driver.find_element_by_id('mobile').send_keys(config.get('common', 'mobile'))
    driver.find_element_by_id('password').send_keys(config.get('common', 'password'))
    driver.find_element_by_id('loginButton').click()
    assert '铂诺' in driver.title
    sleep(2)
    driver.quit()


if __name__ == '__main__':
    register()
