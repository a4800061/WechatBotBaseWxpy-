#coding:utf-8
'''
@JDS 2019/10/25 编写
@毕业设计作品：基于微信WEB协议的机器人

'''
import requests,thread,time,json,re,os,platform,socket,wmi,psutil,pynvml,subprocess,base64
from pyecharts import WordCloud
from cv2 import cv2
from wxpy import *
def Get_HardWareInfo():#获取电脑的基本信息 预加载否则等待消息响应会造成堵塞
    HardWareInfo = {}#用来返回的硬件信息集合
    TotalDisk_Size = 0#硬盘总大小
    HardWare = wmi.WMI()#WMI模块来进行互殴
    Hardware_Cpu_Processor = HardWare.Win32_Processor()#CPU信息集合
    HardWare_BaseBoard = HardWare.Win32_BaseBoard()#主板信息集合
    HardWare_DiskInfo = HardWare.Win32_DiskDrive()#硬盘信息集合
    for Cpu_Info in Hardware_Cpu_Processor:#获取CPU信息
        HardWareInfo["Processor_Name"] = Cpu_Info.Name#获取CPU名称
        HardWareInfo["Processor_Socket"] = Cpu_Info.SocketDesignation#获取CPU接口 
    for Base_Board in HardWare_BaseBoard:#获取主板信息
        HardWareInfo["BaseBoard_Company"] = Base_Board.Manufacturer#获取主板制造商
        HardWareInfo["BaseBoard_Product"] = Base_Board.Product#获取主板型号
    for Disk_Info in HardWare_DiskInfo:#获取硬盘信息
        Disk_Size = Disk_Info.Size
        if Disk_Size == None:
            pass
        else:
            Disk_Size = int(Disk_Size)/pow(1024,3)#把硬盘从Byte转换为GB单位
            TotalDisk_Size+=Disk_Size#计算总的硬盘大小
            HardWareInfo["TotalDisk_Size"] = TotalDisk_Size#硬盘总大小
    return HardWareInfo#函数返回
HardWare_Info = Get_HardWareInfo()#让字典信息成为全局变量便于访问
def Make_Picture_Dir():#检测是否存在Wechapic文件夹
    global Path#定义全局变量Path因为其他函数还需要调用
    global Now_Work_Path#定义全局变量Now_Work_Path因为其他函数还需要调用
    Now_Work_Path = os.getcwd()#检测当前所在目录
    Path = Now_Work_Path + r"\Wechat_Pic"#这个是要保存进图片/不存在目录时需要创建的名称
    Path = Path.decode("gbk")
    IsPath_In = os.path.exists(Path)#检测文件夹是否存在
    if IsPath_In:#如果存在则略过 否则创建一个文件夹
        pass
    else:
        os.mkdir(Path)#创建文件夹
Make_Picture_Dir()#调用检测文件夹函数
def CheckNodeJs():#检测Nodejs环境
    try:#利用subprocess的Popen,运行node但是不会返回控制台输出
        IsHaveNode_Js = subprocess.Popen(["node"],stdout=subprocess.PIPE)#运行node不抛出异常就是存在nodejs环境
        return True#返回True
    except:
        return False#不存在nodejs环境
def Check_Node_Port():#检测localhost的3000端口是否开放
    Connect_Localhost = socket.socket(socket.AF_INET,socket.SOCK_STREAM)#创建socket对象
    Connect_Localhost.settimeout(1)#设置超时时间
    try:#连接localhost:3000如果不抛出异常证明开启成功
        Connect_Localhost.connect(("localhost",3000))#连接本地3000端口
        return True#返回
    except:#否则就是没有开启成功
        return False
def Start_NetEase_Server():#启动nodejs网易云API
    Api_Path = Now_Work_Path + r"\NetEaseApi\app.js"#定义Api的路径
    IsNodeJs_In = CheckNodeJs()#需要做两件事情，01.检查NODEJS环境 02.判断端口是否开启
    IsPort_Open = Check_Node_Port()
    if IsPort_Open == True:#存在且NODEJS端口开启
        print u"端口被占用"
        sys.exit()
    elif IsNodeJs_In == False:#没有Nodejs环境
        print u"请前往:https://nodejs.org/zh-cn\t下载安装Nodejs"
        sys.exit()#暂时用退出方法
    elif IsNodeJs_In == True:#如果存在NODEJS
        if IsPort_Open == False:#但是端口没有开启
            subprocess.Popen(["node",Api_Path],stdout=subprocess.PIPE)#直接node运行path里面的app.js启动服务
            print u"端口开启成功"
Start_NetEase_Server()#程序运行的时候就准备启动
def Login_callback():#微信登陆成功以后输出的提示信息
    print "Welcome to use WechatBot."
def Loginout_callback():#微信登出以后输出的提示信息
    print "Thanks for use."
Main_Bot = Bot(cache_path=True,login_callback=Login_callback,logout_callback=Loginout_callback)
Main_Bot.enable_puid()
#机器人初始化代码
@Main_Bot.register(Friend,except_self=False)
def Main_code(msg):
    global Send_Img_flag#发送图片标志位
    global Send_Face_flag#颜值打分flag
    Send_Type = msg.type#消息中的类型
    Send_Content = msg.text#消息内容
    Message_Sender = msg.sender.nick_name#发送给我消息的用户
    Message_Receiver = msg.receiver.nick_name#我发送消息的用户
    Main_BotSelf = Main_Bot.self.nick_name#扫描二维码之后使用者的昵称
    IsEmoji_In_Sender = bool(re.findall(r"<span.+?>",Message_Sender))#判断发送者名称中是否存在Emoji表情
    IsEmoji_In_Receiver = bool(re.findall(r"<span.+?>",Message_Receiver))#判断接受者名称中是否存在Emoji表情
    def Get_Computer_BasicInfo(A):#获取电脑的基本信息，因为获取硬件信息会无法调用函数 原因未知（预先定义了消息长度而只有Text有信息长度所以阻塞了后面的功能）
            pynvml.nvmlInit()#获取GPU进行初始化
            Public_Ip_Url = "http://ip.42.pl/raw"#获取公网的URL
            Public_Ip = requests.get(Public_Ip_Url).text#取出内容
            Computer_NetWork_Name = platform.node()#取出计算机名
            Computer_Platform = platform.platform()#操作系统平台
            Computer_Arch = platform.architecture()[0]#取出多少位系统
            Gpu_Num = pynvml.nvmlDeviceGetCount()#获取GPU数量
            if Gpu_Num == 1:#只对单块GPU用户进行统计
                global Gpu_Name#便于下面的访问
                Gpu_Handel = pynvml.nvmlDeviceGetHandleByIndex(0)#取出第一块的handel
                Gpu_Name = pynvml.nvmlDeviceGetName(Gpu_Handel)#通过handel取出名称
            else:#如果多于1块不处理
                pass
            Computer_Memory = psutil.virtual_memory()#获取电脑的内存
            Computer_Memory = (Computer_Memory.total/pow(1024,3)) + 1#同样把BYyte转为GB
            Computer_Process = HardWare_Info["Processor_Name"]#取出上面函数返回的内容
            Computer_Private_Ip = socket.gethostbyname(Computer_NetWork_Name)#通过socket中的gethostbyname获取内网IP
            Process_Socket = HardWare_Info["Processor_Socket"]#CPU接口
            Base_BoardCompany = HardWare_Info["BaseBoard_Company"]#主板制造商
            Base_BoardProduct = HardWare_Info["BaseBoard_Product"]#主板型号
            TotalDisk_Size = HardWare_Info["TotalDisk_Size"]#硬盘总大小
            if TotalDisk_Size < 1024:#对于相加小于1024证明不到1t用GB来计算
                TotalDisk_Size = TotalDisk_Size + "GB"
            else:#>=1024的情况用TB计算
                TotalDisk_Size = str(int(round(float(TotalDisk_Size)/1024))) + "TB"#为了四舍五入首先转为浮点数然后四舍五入再取整最后转成字符串和TB拼接
            Basic_Info = "计算机名称:%s\n操作系统:%s\n处理器:%s\n主板:%s\n显卡:%s\n内存:%sGB\n磁盘总大小:%s\n公网IP:%s\n内网IP:%s"%(Computer_NetWork_Name,Computer_Platform+" "+Computer_Arch,
                                                                                Computer_Process,Base_BoardCompany+" " + Base_BoardProduct,Gpu_Name,Computer_Memory,TotalDisk_Size,Public_Ip,Computer_Private_Ip,
                                                                                )
            msg.reply(Basic_Info) #返回信息
    def GetNow_time():#获取时间
        Now_Time_smap = int(time.time())#获取当前时间戳
        Now_Local_Time = time.localtime(Now_Time_smap)#时间戳转换为localtime格式
        Now_Format_Time = time.strftime("%Y-%m-%d %H:%M:%S",Now_Local_Time)#将localtime格式时间戳重新格式化为正常时间
        return Now_Format_Time#返回待调用
    def Trun_To_LocTime(Timesmap):#时间戳转本地
        Now_LocTime = time.localtime(int(Timesmap))#传入参数:timesmap 时间戳，转为Localtime类型
        Format_Time = time.strftime("%Y-%m-%d %H:%M:%S",Now_LocTime)#进行格式化
        return Format_Time#返回正常日期
    def Search_Express(Express_Num):#快递单号查询 蹭用百度接口 百度不倒闭 不改接口永久可用
        Express_Url = "https://sp0.baidu.com/9_Q4sjW91Qh3otqbppnN2DJv/pae/channel/data/asyncqury"#查询快递的接口
        Express_Parmas = {"appid":"4001","nu":Express_Num}#接口所需要的固定参数 ExpressNUm是快递号码
        Get_Baidu_Cookie = requests.get(Express_Url).cookies["BAIDUID"]#本条url需要携带固定cookie参数BAIDUID否则报错
        Send_Header = {"cookie":"BAIDUID=%s" % Get_Baidu_Cookie}#设置请求头携带Cookie参数
        try:#处理异常
            Respone_Unicode = requests.get(Express_Url,params=Express_Parmas,headers=Send_Header).text#获取原始unicode文本
            Respone_Text = json.loads(Respone_Unicode)#进行文本转换转为字典格式
            Get_Express_Error = Respone_Text["error_code"]#取出错误代码，已知错误代码:0-正常无错误 2-号码不正确 3-查询不到信息
            Get_Express_Data = Respone_Text["data"]#1
            Get_Express_Info = Get_Express_Data.get("info")#1
            Get_Express_Content = Get_Express_Info.get("context")#1对应一级关系 其中存放快递的信息文本
            Content_Length = len(Get_Express_Content)#获取列表中的项用来准备循环
            Express_List = []#信息准备存放的地方
            if (Get_Express_Data!=None) and (Get_Express_Info!=None):#如果两个都存在项目
                if Get_Express_Error == "0":#如果errorcode是0才开始进行互殴
                    for Item_Num_Content in range(Content_Length):#进行循环
                        Express_Text = Get_Express_Content[Item_Num_Content]["desc"]#每一项的文本描述
                        Express_Time = Get_Express_Content[Item_Num_Content]["time"]#每一项的时间
                        Loc_Time = Trun_To_LocTime(Express_Time)#调用函数转换为本地的时间
                        Express_Final = Loc_Time + " " + Express_Text#组合
                        Express_List.append(Express_Final)#加入list
                    Send_ExpressMessage = "\n".join(Express_List)#重新组合为一个字符串
                    return Send_ExpressMessage#返回信息
                elif Get_Express_Error == "2":#判断
                    return u"号码不合法/不正确"
                elif Get_Express_Error == "3":#判断
                    return u"没有查询到该单号信息"
                else:#发送代码
                    return u"发生其他错误,错误代码:%s" % Get_Express_Error
            else:#处理未知情况
                return u"发生未知错误"
        except:#发生异常证明程序产生错误不能继续运行
            return u"参数不合法"
    def Hitoko_Api():#一言API
        Hit_URL = "https://v1.hitokoto.cn/"
        Hit_Param = {"c":"g","encode":"text"}
        Hit_TEXT = requests.get(Hit_URL,params=Hit_Param).text
        return Hit_TEXT#返回纯文本参数
    def GetFridend_WordCloud():#生成好友词云图
        Fridens_Data = []#用于存放好友数据
        All_BotFriends = Main_Bot.friends()#定义变量全部好友的集合
        for SingleFriend in All_BotFriends:#遍历好友单个好友有fridend类的属性
            FridendsName = SingleFriend.remark_name#获取好友备注
            if FridendsName != "":#处理没有备注的情况
                Fridens_Data.append(FridendsName)#添加到list中
        Saved_Path = Path+r"\WordCould.jpeg"#定义存储文件名用来发送回去
        Make = WordCloud(width=1920,height=1080)#词云图初始化
        Make.add("JDS_Finally_Test",Fridens_Data,Fridens_Data,word_size_range=[20,50],shape="diamond")#如上
        Make.render(Saved_Path)#输出到指定目录
        return Saved_Path
    def Get_Bot_Friends():#统计好友基本信息
        Bots_FriendInfo = Main_Bot.friends().stats_text()#用wxpy.chats中的statstext方法返回统计
        return Bots_FriendInfo#返回信息准备发送
    def Get_Picture():
        Picture_path = Path + r"\Picture.jpeg"
        msg.get_file(Picture_path)#下载图片
        msg.reply_image(Picture_path)#回复图片
    def Get_Weather(City):#实况天气
        Api_Key = "填写自己的key"#和风天气API接口，此条为API授权Key
        Api_Now_Url = "https://free-api.heweather.net/s6/weather/now"#请求URL
        Api_Param = {"location":City,"key":Api_Key}#请求参数
        Api_Respone_Unicode = requests.get(Api_Now_Url,params=Api_Param).text#发送GET请求拿回原始Unicode数据
        Api_Respone_Json = json.loads(Api_Respone_Unicode)#JSON进行Unicode解析
        Api_Respone_Main = Api_Respone_Json["HeWeather6"][0]#主要JSON数据，后面依靠他取出数据
        Api_Respone_Basic = Api_Respone_Main["basic"]#基本数据
        Api_Respone_Update = Api_Respone_Main["update"]#更新时间
        Api_Respone_Status = Api_Respone_Main["status"]#接口状态
        Api_Respone_Now = Api_Respone_Main["now"]#实况天气所在位置
        City_Lat = Api_Respone_Basic["lat"]#城市经度
        City_Lon = Api_Respone_Basic["lon"]#城市纬度
        City_Admin_Area = Api_Respone_Basic["admin_area"]#城市所在地级市
        City_Parent = Api_Respone_Basic["parent_city"]#城市所在县级市
        City_Name = Api_Respone_Basic["location"]#城市名称
        Update_loc = Api_Respone_Update["loc"]#本地时间
        if Api_Respone_Status == "ok":#判断接口状态
            Send_List = []#用来进行信息汇总封装
            Weather_Key = {"fl":u"体感温度(℃)","tmp":u"温度(℃)","cond_txt":u"天气情况",
                             "wind_dir":u"风向","wind_sc":u"风力(级)","wind_spd":u"风速(m/s)",
                            "hum":u"相对湿度(%)","pcpm":u"降水量(mm)","pres":u"大气压强(kpa)",
                            "vis":u"能见度(公里)"
                        }#自己写的字典方便进行获取数据，大致思路是给其定义一个字典之后遍先便历ApiResponeNow，只是为了保证循环次数所以用了pass
                        #然后再次遍历自写的字典获取每一个键，为了防止发生重复当APIRowkey和CusKey相等时证明其发送重复值保留一个，所以开始取出WeatherKey
                        #中的各个剪纸作为中文说明然后再用APiResponeNow去取出自己键对应的值和中文说明组合，最后创建一个LIST用来将每一项加入list
                        #循环结束以后把LIST中的每一项用join组合成一整个字符串用\n作为连接符，其目的是为了方便发送微信消息的时候发送不完整或者发送次数过多
                        #对用户产生骚扰
            for Api_Row_Key in Api_Respone_Now:#保证循环次数
                pass#略过
                for Cus_Key in Weather_Key:#遍历自写字典中的值
                    if Api_Row_Key==Cus_Key:#判断相等重复的情况
                        Api_Result = Weather_Key[Cus_Key]#取出对于的中文说明
                        Finall_Result = Api_Result+":" + Api_Respone_Now[Api_Row_Key]#组合
                        Send_List.append(Finall_Result)#加入LIST
            Join_Info_Weather = "\n".join(Send_List)#重新组合
            Main_Message = "您查询的是%s天气信息,其经纬度为(%s,%s)\n以下是其天气信息:\n%s\n更新时间为:%s"%(City_Admin_Area+City_Parent+City_Name,City_Lat,City_Lon,Join_Info_Weather,Update_loc)
            return Main_Message
        else:
            return "接口存在异常"
    def Login_NetEase_Local(Phone,Password):#登陆网易云
        global Local_Api_Url#定义一个本地API地址
        global Keep_Session#用于持久会话
        global UserProfile_Id#用于登陆以后获取用户uid来进行下一步操作
        Local_Api_Url = "http://localhost:3000"#赋值
        NetEase_PhoneLogin_Url = Local_Api_Url+"/login/cellphone"#电话号码登陆接口
        NetEase_PhoneLogin_param = {"phone":Phone,"password":Password}#需要传入的参数账号和密码
        Keep_Session = requests.Session()#建立持久会话连接
        LoginNetEase_CallBack_Unicode = Keep_Session.get(NetEase_PhoneLogin_Url,params=NetEase_PhoneLogin_param).text#取出原始地址数据
        LoginNetEase_CallBack_Dict = json.loads(LoginNetEase_CallBack_Unicode)#json解析
        Login_NetEase_Code_One = LoginNetEase_CallBack_Dict["code"]#取出状态码用来告知用户错误
        if Login_NetEase_Code_One != 200:#200是登陆成功状态码，其他状态码证明出错用来返回告知用户
            return "发生未知错误%s" % str(Login_NetEase_Code_One)
        else:
            Login_NetEase_Code_Update = LoginNetEase_CallBack_Dict["code"]#
            UserProfile_Id = LoginNetEase_CallBack_Dict["account"]["id"]#取出用户uid，给global赋值，所以用户只有登陆网易云之后才能得到uid，如果没有登陆就调用了需要uid的函数就会不允许运行
            #以上代码无问题
            UserProfile_CreatTime = str(LoginNetEase_CallBack_Dict["account"]["createTime"])[:-3]#取出账号创建的时间因为原始数据是Unicode数据所以转为str然后剔除最后三位毫秒级时间戳
            FormatUserProfile_Time = Trun_To_LocTime(int(UserProfile_CreatTime))#进行函数调用得到正常时间
            UserProfile_Details = LoginNetEase_CallBack_Dict["profile"]#用户个人信息
            UserProfileDetails_NickName = UserProfile_Details["nickname"]#用户昵称
            Return_UserProfile = (UserProfile_Id,FormatUserProfile_Time,UserProfileDetails_NickName)#返回用户uid，昵称，账号创建的时间
            return Return_UserProfile
    def GetNetEase_UserDetails(UID):#获取用户详细信息
        Details_Api_Url = Local_Api_Url + "/user/detail?uid=%s" % UID#详细信息接口需要带上参数uid
        UserUnicode = Keep_Session.get(Details_Api_Url).text#获取Unicode原始数据
        UserDict = json.loads(UserUnicode)#进行解析
        User_Level = UserDict["level"]#用户等级
        User_listenSongs = UserDict["listenSongs"]#用户听歌总数
        User_Profile = UserDict["profile"]#用户个人信息
        User_fans = User_Profile["followeds"]#用户关注人数
        User_Fllow = User_Profile["follows"]#用户粉丝数量
        User_PlayList_Num = User_Profile["playlistCount"]#歌单数量
        Profile_Details = (User_Level,User_listenSongs,User_fans,User_Fllow,User_PlayList_Num)#返回用户等级，听歌总数。分析和关注的人数还有歌单数量
        return Profile_Details
    def GetNetEase_UserPlayList(UserId):#获取用户的歌单详情
        GetUserPlayList_Url = "http://localhost:3000/user/playlist?uid={}".format(UserId)#获取用户歌单详情接口需要带上参数uid
        GetUserPlayList_Unicode = requests.get(GetUserPlayList_Url).text#获取原始数据
        GetUserPlayList_Dict = json.loads(GetUserPlayList_Unicode)#解析
        UserPlayList = GetUserPlayList_Dict["playlist"][0]#默认获取用户喜欢的歌曲
        UserPlayList_Name = UserPlayList["name"]#歌单名
        UserPlayList_Id = UserPlayList["id"]#歌单id后面会用到
        UserPlayListInfo = (UserPlayList_Name,UserPlayList_Id)#返回歌单名和歌单id
        return UserPlayListInfo
    def GetNetEase_PlayListSong_Url(PlaylistID):#获取歌单歌曲url
        GetSongId_Url = "http://localhost:3000/playlist/detail?id={}".format(PlaylistID)#获取歌单详情的接口
        GetSonId_Unicode = requests.get(GetSongId_Url).text#获取原始数据
        GetSongId_Dict = json.loads(GetSonId_Unicode)#口EXO
        SongPlayList = GetSongId_Dict["playlist"]#歌单
        SongInfo_List = SongPlayList["tracks"]#歌曲
        GetLikeSonsNum = 10#默认只获取前十个
        SongAllInfo = []#数据整合
        for SongIndex in range(GetLikeSonsNum):#准备进行遍历来获取歌曲名字和作者
            SongNameEncodeIgnore = SongInfo_List[SongIndex]["name"].encode("gbk","replace")#因为Unicode空格是特殊符号?所以用encode重新解析
            SongNameReplace = SongNameEncodeIgnore.replace("?"," ")#替换特殊符号?
            SongInfo_Id = SongInfo_List[SongIndex]["id"]#获取歌曲id后面会用到
            Songer_Name = SongInfo_List[SongIndex]["ar"][0]["name"].encode("gbk","ignore")#忽略特殊字符
            SonUrl =  "https://music.163.com/song/media/outer/url?id=%s.mp3" % SongInfo_Id#传入歌曲id就是播放链接
            SongFullInfo = SongNameReplace + " by:" + Songer_Name + "\n"+SonUrl#循环取出
            SongAllInfo.append(SongFullInfo)#加入list
        SendFullInfo = "\n".join(SongAllInfo)#返回拼接好的信息
        return SendFullInfo
    def SayLove():#土味情话
        LoveUrl = "https://api.lovelive.tools/api/SweetNothings"
        LoveText = requests.get(LoveUrl).text
        return LoveText
    def GetBaidu_AccessToken():#百度api的accesstoken获取用于下面的接口
        Api_Host = "https://aip.baidubce.com/oauth/2.0/token"#
        ClientId = "填写自己的id"##
        ClientKey = "填写自己的key"#
        Api_Params = {"grant_type":"client_credentials","client_id":ClientId,"client_secret":ClientKey}#
        Json_Info = json.loads(requests.get(Api_Host,params=Api_Params).text)#
        Baidu_AccessToken = Json_Info["access_token"]#
        return Baidu_AccessToken
    def GetImageBase64Str(ImageName):#需要把图片文件转为base64编码进行传递
        with open(ImageName,"rb") as ImageFile:#读取文件
            ImageByte = ImageFile.read()#读取字节流
            BaseEncodeStr = base64.b64encode(ImageByte)#把字节流转为base64输出
        return BaseEncodeStr#返回b64信息
    def FaceCheck_Info(BaseImage):#颜值打分函数
        FaceCheck_Url = "https://aip.baidubce.com/rest/2.0/face/v3/detect"#人脸检测接口
        FaceCheckUrlParam = GetBaidu_AccessToken()#获取token，token每次都是新的不用考虑过期
        FaceFullUrl = FaceCheck_Url + "?access_token=" + FaceCheckUrlParam#完整的函数
        FaceHeader = {"Content-Type":"application/json"}#
        Image_Base = BaseImage#用上面的函数返回b64文本传入
        Image_Type = "BASE64"#定义传入方式
        Face_filed = "age,beauty,expression,face_shape,gender,glasses,landmark,landmark150,race,quality,eye_status,emotion,face_type"#需要返回的内容
        max_face_num = 1#只检测一张人脸
        Face_type = "LIVE"#默认生活照
        FacePostData = {"image":Image_Base,"image_type":Image_Type,"face_field":Face_filed,"max_face_num":max_face_num,"face_type":Face_type}#Post过去的数据
        FaceInfo_Unicode = requests.post(FaceFullUrl,data=FacePostData).text#获取
        FaceInfo_Dict = json.loads(FaceInfo_Unicode)#
        FaceErrorCode = FaceInfo_Dict["error_code"]#取出错误码
        if FaceErrorCode != 0:#不是0就是发生错误了
            return "发生未知错误%s" % FaceErrorCode#返回给用户
        else:
            FaceImg = cv2.imread("FacerRawImg.jpg")#使用opencv读取图像准备框出人脸
            FaceInfo_Result = FaceInfo_Dict["result"]#返回结果
            FaceInfo_List = FaceInfo_Result["face_list"]#人脸列表
            FaceInfoLocation = FaceInfo_List[0]["location"]#人脸的轴信息
            FaceLocation_Left = int(FaceInfoLocation["left"])#距离图片边缘左边距离
            FaceLocation_Top = int(FaceInfoLocation["top"])#距离图片上方距离，根据两个信息可以确定开始画框的点位置
            FaceLocation_Width = int(FaceInfoLocation["width"])#人脸宽度
            FaceLocation_Height = int(FaceInfoLocation["height"])#人脸高度
            FaceAge = FaceInfo_List[0]["age"]#年龄
            FaceBeauty = FaceInfo_List[0]["beauty"]#颜值分数
            FaceExpression = FaceInfo_List[0]["expression"]#表情
            ExPressionType = FaceExpression["type"]#
            FaceShape = FaceInfo_List[0]["face_shape"]#脸型
            ShapeType = FaceShape["type"]
            FaceRace = FaceInfo_List[0]["race"]["type"]#肤色
            FaceEmotion = FaceInfo_List[0]["emotion"]["type"]
            FaceLocation_LeftPos = (FaceLocation_Left,FaceLocation_Top)#这个是准备画矩形的左上角坐标位置
            FaceLocation_RightPos = (FaceLocation_Left+FaceLocation_Width,FaceLocation_Top+FaceLocation_Height)#把距离左边的距离加上宽度就可以得到右边点的x轴,加上上方距离和高度得到y轴,这样就可以框出人脸位置
            cv2.rectangle(FaceImg,FaceLocation_LeftPos,FaceLocation_RightPos,(0,0,255),3)#画一个方框在对应位置
            cv2.imwrite("CheckedFaceReturn.jpg",FaceImg)#重新写入文件
            FaceInfoMessAge = "计算结果已经得出:\n\n图片中的人物年龄是:{}\n\n脸型是:{}\n\n人种是:{}\n\n电脑检测出的情绪是:{}\n\n电脑检测出的表情是:{}\n\n电脑给出颜值分数为:{}".format(FaceAge,ShapeType,FaceRace,FaceEmotion,ExPressionType,FaceBeauty)
            return FaceInfoMessAge#返回信息
    def GetFaceImage():
        FacePath = "FacerRawImg.jpg"
        msg.get_file(FacePath)
        return FacePath#下载并返回path证明已经有文件了
    def GetAvatarRand(A):#获取头像
        AvatarUrl = "https://api.uomg.com/api/rand.avatar"#
        for AvatarNum in range(20):#下载20个头像
            ImageByte = requests.get(AvatarUrl).content
            Avatar_Path = Now_Work_Path + "\\Avatar"+"\\RandAvatar%s.jpg" % AvatarNum#进行有序写入
            with open(Avatar_Path,"wb") as AvatarFile:
                AvatarFile.write(ImageByte)
            time.sleep(3)
            msg.reply_image(Avatar_Path.decode("gbk","ignore"))#依次发送
    if IsEmoji_In_Sender:#对于存在Emoji昵称的发送者进行昵称处理
        Match_emoji_Sender = re.findall(r"<span.+?/span>",Message_Sender)#搜索emoji
        Emoji_str_Sender = Match_emoji_Sender[0]#取出list中的emoji
        Message_Sender = Message_Sender.replace(Emoji_str_Sender,"[Emoji表情]").strip()#进行替换
    elif IsEmoji_In_Receiver:#对于存在Emoji昵称的接受者进行昵称处理，以下同理
        Match_emoji_Receiver = re.findall(r"<span.+?/span>",Message_Receiver)
        Emoji_str_Receiver = Match_emoji_Receiver[0]
        Message_Receiver = Message_Receiver.replace(Emoji_str_Receiver,"[Emoji表情]").strip()
    else:
        pass 
    if Send_Type == "Text":
        Content_Lenght = len(Send_Content)#消息长度
        if Send_Content == "获取表情":
            Send_Img_flag = 1#为真则调用
            Send_Face_flag = 0
            msg.reply("请发送您的表情包")
        if Send_Content == "取消获取表情":
            Send_Img_flag = 0#为假跳过
            msg.reply("已经停止获取")
        if "天气" in Send_Content:#如果天气关键词在里面则出发
            if Content_Lenght == 2:#如果长度为2证明没有跟随地区
                msg.reply("请在天气后面添加您想要查询的城市")
            else:
                Get_CityName = Send_Content[2:]#存在以后取出消息中从“气”往后的所有字符串作为参数
                WeatherData = Get_Weather(Get_CityName)#上面取出的参数作为参数传递进函数中
                msg.reply(WeatherData)#回复天气信息
        if Send_Content == "统计好友":
            Send_Info_F = Get_Bot_Friends()#调用
            msg.reply(Send_Info_F)
        if Send_Content == "获取词云":
            Send_Info_C = GetFridend_WordCloud()
            msg.reply_image(Send_Info_C)
        if Send_Content == "获取一言":
            Send_Hit = Hitoko_Api()#调用一言
            msg.reply(Send_Hit)
        if "快递" in Send_Content:#和天气处理用同样的思路
            if Content_Lenght == 2:#如果长度是2证明无单号
                msg.reply("请输入单号")
            else:
                Express_Number = Send_Content[2:]#从di后面的都是单号用来传入
                SendExpressInfo = Search_Express(Express_Number)#调用查询快递函数
                msg.reply(SendExpressInfo)#回复信息
        if "登陆网易云" in Send_Content:#和天气一样思路
            if Content_Lenght == 5:#如果是五证明没有输入账号密码
                msg.reply("请输入账号密码用空格隔开")
            else:
                NetEaseUserName_List = Send_Content[5:].split(" ")#从5之后都是，然后用空格分辨账号和密码
                NetEaseUser_Name = int(NetEaseUserName_List[0])#第一个是账号
                NetEaseUser_PassWord = str(NetEaseUserName_List[1])#第二个是密码
                UserSendInfo = Login_NetEase_Local(NetEaseUser_Name,NetEaseUser_PassWord)#调用登陆函数
                UserSendInfo_Type = type(UserSendInfo).__name__#取出类型名字
                if UserSendInfo_Type == "str":#如果是str证明返回的报错信息因为正确信息是一个元组
                    msg.reply(UserSendInfo)
                else:#如果返回元组证明登陆上去了
                    NetEaseUser_ID = UserSendInfo[0]#取出uid
                    NetEaseUser_CreatTime = UserSendInfo[1]#创建时间
                    NetEaseUser_NickName = UserSendInfo[2]#昵称
                    UserDetails_Profile = GetNetEase_UserDetails(NetEaseUser_ID)#这一步调用接口获取更详细的信息
                    NetEaseUser_Level = UserDetails_Profile[0]#等级
                    UserDetails_ListenSongs = UserDetails_Profile[1]#听歌总数
                    UserDetails_fans = UserDetails_Profile[2]#粉丝数量
                    UserDetails_fllowed = UserDetails_Profile[3]#关注人数
                    UserDetails_PlayListNum = UserDetails_Profile[4]#歌单数量
                    Send_NetEase_Message = "登陆成功\n用户昵称:%s\n创建账号时间:%s\n用户UID:%s\n用户等级:%s\n听歌总数:%s\n粉丝:%s\n关注的人:%s\n歌单数量:%s"%(NetEaseUser_NickName,NetEaseUser_CreatTime,NetEaseUser_ID,NetEaseUser_Level,UserDetails_ListenSongs,UserDetails_fans,UserDetails_fllowed,UserDetails_PlayListNum)
                    msg.reply(Send_NetEase_Message)#回复
        if Send_Content == "获取网易云歌单":#获取歌单需要获取歌单再从歌单获取url
            try:#抛出异常回复给用户，一般用来方便调试不然console不输出信息
                SendInfo = GetNetEase_UserPlayList(UserProfile_Id)#获取歌单
                PlayListName = SendInfo[0]#第一个是歌单名字
                PlayListId = SendInfo[1]#第二个是歌单id
                SongTotalInfo = GetNetEase_PlayListSong_Url(PlayListId)#传入歌单id得到详细信息
                SongTotalInfoDecode = SongTotalInfo.decode("gbk","ignore")#把返回的结果进行二次编码防止报错
                SendReplyMessAge = "歌单名称:%s\n\n\n以下是歌单内容:\n\n\n%s" % (PlayListName,SongTotalInfoDecode)#回复
                msg.reply(SendReplyMessAge)
            except Exception as Error:
                msg.reply(Error)#出错以后回复
        if Send_Content == "获取头像":#
            msg.reply("正在获取中...")
            thread.start_new_thread(GetAvatarRand,(1,))#加入线程进行并发运行
        if Send_Content == "嗨":#
            SendLoveWord = SayLove()
            msg.reply(SendLoveWord)
        if Send_Content == "颜值打分":#得到这句话之后
            Send_Face_flag = 1#颜值打分flag为1准备接收图片
            Send_Img_flag = 0#同时关闭获取表情功能
            msg.reply("请发送带有人脸的照片/自拍照")
        if Send_Content == "退出颜值打分":#退出以后flag置0
            Send_Face_flag = 0
            msg.reply("已退出")
        if Send_Content == "获取电脑基本信息":#获取电脑信息
            msg.reply("正在获取中请稍后...")
            thread.start_new_thread(Get_Computer_BasicInfo,(1,))#比较耗时加入后台线程进行并发运行
        if Send_Content == "帮助":
            SendHelpInfo = "1.发送天气+地区获取当前天气(没有加号)\n\n2.发送快递+单号进行快递查询\n\n3.发送获取一言来获取随机句子\n\n4.发送获取头像来获取随机头像\n\n5.发送获取表情来获取微信表情包(取消获取表情来退出)\n\n6.发送颜值打分并发送一张带有人脸照片进行打分(开发不易暂时只支持一张人脸,发送退出颜值打分来退出)"\
                "\n\n7.发送获取歌单来获取网易云歌单(需要发送登陆网易云+账号 密码[中间有空格]来登陆以后才可以获取)\n\n8.发送获取电脑基本信息来获取服务器信息\n\n9.发送获取词云获取机器人好友词云图\n\n10.发送嗨获取土味情话\n\n11.发送统计好友获取机器人好友信息"
            SendOtherInfo = "这是一个基于Python的Console端机器人\n基于微信WEB协议的机器人\n这是此开发者的毕业设计作品不会常用.\nAuthor:By @JDS\nQQ:2732423664\nWeChat:jidesheng666"
            msg.reply(SendHelpInfo)
            msg.reply(SendOtherInfo)
        print "收到一条来自'%s'的消息,消息内容是:\n\n%s\n\n发送时间是:%s\n接受者:%s\n\n"%(Message_Sender,Send_Content,GetNow_time(),Message_Receiver)
    if Send_Type == "Picture":#标志位和消息类型判断
        if Send_Img_flag == 1:
            Get_Picture()#调用
        if Send_Face_flag == 1:#颜值打分flag为1进行操作
            try:
                FacePathRaw = GetFaceImage()#首先下载图片
                Base64ImageStr = GetImageBase64Str(FacePathRaw)#base64转换
                ReturnComMessAge = FaceCheck_Info(Base64ImageStr)#传入参数
                msg.reply_image("CheckedFaceReturn.jpg")#返回框好的人脸
                msg.reply(ReturnComMessAge)#返回信息
            except Exception as Error:#回馈错误
                msg.reply(Error)
    else:
        pass
Main_Bot.join()#阻塞进程实现实时在线
'''
完成时间:2019/11/5 22:50
毕业设计完成
主要功能有:
获取微信表情包  统计登陆机器人用户的好友信息 
天气查询 获取登陆机器人用户的好友昵称词云图 
随机句子获取 快递单号查询 登
陆网易云 获取登陆以后网易云歌单 
获取随机头像 土味情话获取
颜值打分 获取当前电脑的基本配置信息

大部分是API接口方式 基于函数封装各个功能
基于WEB微信协议开发 基于封装库Wxpy进行二次开发

各个函数用处不同 程序开始的时候会检查:
0x01 是否存在nodejs环境(如果没有则退出程序)
0x02 是否有指定的文件夹(如果没有则创建)
0x03 本地的3000端口是否被占用(占用退出)
0x04 直接开始获取电脑硬件信息(这是因为wmi函数会被堵塞 原因未知)

程序调用了多个库 如果在其他人电脑上面会因为文件目录不完整/库不完整/配置文件错误/python版本不同导致各类错误
已经进行局部优化:
0x01 检测文件目录是否存在需要的文件夹 不存在会创建/报错
0x02 对于用户的emoji表情 会显示"span xxx" 已经用正则进行替换为"[Emoji表情]" [函数是有的但是不知道为什么错了]
0x03 部分函数如果发送错误会回馈给用户方便排查
0x05 部分需要等待时间长的函数加入线程进行并发运行提高效率
0x06 局部函数考虑用户漏输入的问题进行长度判断并且进行提示
0x07 部分会导致程序无法运行的错误已经修复
@JDS
'''
