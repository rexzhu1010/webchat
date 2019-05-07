from django.shortcuts import render,HttpResponse,redirect
from bs4 import  BeautifulSoup

# Create your views here.
import requests
import time
import re,json

CTIME =  None
QCODE = None
TIP = 1
USER_KEY_DICT = {}
ALL_COOKIES_DICT = {}
USER_INT_DICT = {}
def login(request):
    global CTIME
    global QCODE
    CTIME = time.time()
    response = requests.get(
        url="https://login.wx.qq.com/jslogin?appid=wx782c26e4c19acffb&fun=new&lang=zh_CN&_=%s"%CTIME
    )
    print(response.text)
    a=re.search('uuid = "(.*)";',response.text)
    code=a.group(1)
    QCODE = code
    return render(request,"login.html",{"code":code})


def aa(request):
    return  render(request,"login.html")


def check_login(request):
     global TIP
     import json
     ret = {"code":408,"data":None}
     # time.sleep(5)
     url = "https://login.wx.qq.com/cgi-bin/mmwebwx-bin/login?loginicon=true&uuid=%s&tip=%s&r=-1659065892&_=%s" % (QCODE,TIP, CTIME)
     r1=requests.get(
         url=url
     )
     print(url)
     print(r1.text)
     r_status = re.search("window.code=(\d{3})",r1.text)
     scan_status = r_status.group(1)
     if scan_status == "408":
         print("无人扫码！！！！！！！！！")
         return HttpResponse(json.dumps(ret))
     elif scan_status == "201":
         r2=re.search("window.userAvatar = '(.*)'",r1.text)
         ret["code"]=201
         ret["data"]= r2.group(1)
         TIP = 0
         return HttpResponse(json.dumps(ret))


     elif scan_status == "200":
         data = re.findall('window.redirect_uri="(.*)"',r1.text)[0]
         ret["code"]=200
         ret["data"]=data

         print(r1.text)
         #window.code = 200;
         #window.redirect_uri = "https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxnewloginpage?ticket=ARhYXYdaUOfhKGrvI_mQfoYg@qrticket_0&uuid=wdy5bOQCrQ==&lang=zh_CN&scan=1556442611";
         #请求redirect_uri,返加一些key，保存好
         r2=requests.get(
             url=data +"&fun=new&version=v2&lang=zh_CN"
         )

         c1 =  r2.cookies.get_dict()
         ALL_COOKIES_DICT.update(c1)


         print(r2.text)
         soup = BeautifulSoup(r2.text,features="html.parser")
         er = soup.find("error")
         global USER_KEY_DICT
         #把key 找出来，保存到全局变量
         for i in er:
             USER_KEY_DICT[i.name]=i.string

         return HttpResponse(json.dumps(ret))

def user(request):


         #获取首页
         url="https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxinit?r=-1833994964&lang=zh_CN&pass_ticket=%s"%(USER_KEY_DICT['pass_ticket'])

         # post
         get_user_info_data = {
            "BaseRequest":{
                 "DeviceID": "e224120922822483",
                 "Skey":USER_KEY_DICT['skey'],
                 "Uin": USER_KEY_DICT['wxuin'],
                 "Skey": USER_KEY_DICT['skey'],
             }
         }

         r3=requests.post(
             url=url,
             json=get_user_info_data,
             cookies=ALL_COOKIES_DICT
         )
         print("I am here ...................................................")
         r3.encoding= r3.apparent_encoding
         print(url)
         # print(r3.text)
         with open('kk.txt', 'w') as f:
             f.write(r3.text)
         r4 = json.loads(r3.text)


         #保存登入帐号信息
         # for k,v in r4["User"].items():
         #     USER_INFO[k] = v
         # global USER_INFO
         USER_INT_DICT.update(r4)
         #
         # for i in r4["MPSubscribeMsgList"]:
         #     print(i["NickName"])
         #return HttpResponse(json.dumps(ret))
         #return redirect("/user.html")
         return render(request,"user.html",{'user':r4})




def contact(request):

    #
    # https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxgetcontact?pass_ticket=4xsNlFu5XUiGIZ8t21mew3XvBui1k4Fue7pQiFA0kJFqa6JeWHHGB0NuzFZdejJw&r=1557026591973&seq=0&skey=@crypt_6d855dd_b7cfb36d11a0554398f68d0d83a82445

    # POST
    # BaseResponse: {Ret: 0, ErrMsg: ""}
    # MemberCount: 265
    # MemberList: [{Uin: 0, UserName: "weixin", NickName: "å¾®ä¿¡å›¢é˜Ÿ",…}, …]
    # Seq: 0

    a=int(time.time() * 1000)
    url="https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxgetcontact?pass_ticket=%s&r=%s&seq=0&skey=%s"%(USER_KEY_DICT['pass_ticket'],a,USER_KEY_DICT['skey'])


    # get_user_info_data = {
    #     "BaseRequest": {
    #         "DeviceID": "e224120922822483",
    #         "Skey": USER_KEY_DICT['skey'],
    #         "Uin": USER_KEY_DICT['wxuin'],
    #         "Skey": USER_KEY_DICT['skey'],
    #     }
    # }

    r5 = requests.get(
        url=url,
        cookies=ALL_COOKIES_DICT
    )

    r5.encoding = "utf-8"
    contact = json.loads(r5.text)

    for k,v in contact.items():
        print(k,v)



    return render(request, "contact.html",{"contact":contact})







#window_userAvatar = 'data:img/jpg;base64,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';



def  senMsg(request):

    toUser = request.GET.get("toUser")
    msg = request.GET.get("msg")

    a = int(time.time() * 10000000)
    data ={
        "BaseRequest": {
            "DeviceID": "e224120922822483",
            "Skey": USER_KEY_DICT['skey'],
            "Uin": USER_KEY_DICT['wxuin'],
            "Skey": USER_KEY_DICT['skey'],
        },

        "Msg": {
            "ClientMsgId": a,
            "Content": msg,
            "FromUserName": USER_INT_DICT["User"]["UserName"],
            "LocalID": a,
            "ToUserName": toUser,
            "Type": 1,
            'Scene': 0,
        },
        "Sence":0

    }

    print(data)

    url="https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxsendmsg?lang=zh_CN&pass_ticket=%s"
    url= url % USER_KEY_DICT['pass_ticket']
    response = requests.post(
        url = url,
        data = bytes(json.dumps(data,ensure_ascii=False),encoding='utf-8'),#
        cookies = ALL_COOKIES_DICT
    )

    print(response.text)


    return HttpResponse("200")



def  get_msg(request):

    # 1 检查是否有消息到来，synckey 初始化信息中获取
    # 2 如果 response  中 windows.synccheck={retode:"0",selector:"2"} 有消息到来

    time.sleep(1)

    synckey = USER_INT_DICT['SyncKey']['List']

    a=int(time.time()*1000)

    url="https://webpush.wx.qq.com/cgi-bin/mmwebwx-bin/synccheck?r=%s&skey=%s&sid=%s&uin=%s&deviceid=e992903356200358&synckey=%s"
    sync_list = []
    print(synckey)
    for  item in  synckey:
        temp = "%s_%s"%(item["Key"],item["Val"])
        sync_list.append(temp)
    sn = "|".join(sync_list)
    print(sn)

    params1 = {
        "r": a,
        "skey": USER_KEY_DICT['skey'],
        "sid": USER_KEY_DICT['wxsid'],
        "uin": USER_KEY_DICT['wxuin'],
        "deviceid": "e992903356200358",
        "synckey": sn,
    }

    r1 = requests.get(
       url = "https://webpush.wx.qq.com/cgi-bin/mmwebwx-bin/synccheck",
       params=params1,
       cookies = ALL_COOKIES_DICT
    )

    #print(r1.text)

    data ={
        "BaseRequest": {
            "DeviceID": "e224120922822483",
            "Sid": USER_KEY_DICT['wxsid'],
            "Uin": USER_KEY_DICT['wxuin'],
            "Skey": USER_KEY_DICT['skey'],
        },

        "SyncKey": USER_INT_DICT['SyncKey'],


        "rr": 1,
    }

    if 'retcode:"0",selector:"2"' in r1.text:

        print("有消息。。。。。。。。。。。。。。。。。。。。")
        r2 =  requests.post(
            url="https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxsync",
            params={
                'skey':USER_KEY_DICT['skey'],
                'sid':USER_KEY_DICT['wxsid'],
                'pass_ticket':USER_KEY_DICT['pass_ticket'],
                'lang':'zh_CN',
            },
            data = json.dumps(data),
            cookies = ALL_COOKIES_DICT
        )

        r2.encoding="utf-8"
        msg_dict =  json.loads(r2.text)

        for msg_info in msg_dict['AddMsgList']:
            print("新消息：",msg_info['Content'])

        USER_INT_DICT['SyncKey'] = msg_dict['SyncKey']




        print("打印消息。。。。。。。。。。。。。。。。。。。。。")



    return HttpResponse("200")