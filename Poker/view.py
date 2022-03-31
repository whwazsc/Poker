from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from . import game, rsa, aes
import re, json, threading
from django.views.decorators.csrf import csrf_exempt

def readfile(file):
    f = open(file)
    t = f.read()
    f.close()
    return t

PUBLIC_KEY = readfile("./static/key/publickey.txt")
PRIVATE_KEY = readfile("./static/key/privatekey.txt")

G = game.Game()
RSA = rsa.GameRSA(PUBLIC_KEY, PRIVATE_KEY)

PUBLIC_KEY = PUBLIC_KEY.replace("\n", "\\\n")

def login(request):
    return render(request, "login.html", {"public_key": PUBLIC_KEY})

@csrf_exempt
def home(request):
    if "username" not in request.POST or "enkey" not in request.POST or "sign" not in request.POST:
        return HttpResponse("访问出错或登陆超时！")
    name = request.POST["username"]
    key = request.POST["enkey"]
    key = RSA.rsa_decrpt(key)
    sign = request.POST["sign"]
    success, info = G.createplayer(name, key, sign)
    if not success:
        return HttpResponse(info)
    AES = aes.GameAES(key)
    id = AES.text_encrypt(str(info.id))
    dic = {}
    dic["id"] = id
    #以id作签名，攻击者会通过统计攻击猜出id的值，从而伪造数据
    sign = RSA.rsa_sign(id)
    dic["sign"] = sign
    return render(request, "home.html", dic)

def illegal(request):
    return HttpResponse("访问出错或登陆超时！")

def createroom(request):
    dic = {}
    if request.GET:
        id = request.GET["id"]
        username = request.GET["username"]
        pwd = request.GET["roompwd"]
        money = request.GET["money"]
        sign = request.GET["sign"]
        bet = request.GET["bet"]
        id = RSA.rsa_decrpt(id)
        username = RSA.rsa_decrpt(username)
        pwd = RSA.rsa_decrpt(pwd)
        money = RSA.rsa_decrpt(money)
        bet = RSA.rsa_decrpt(bet)
        success, info = G.createroom(id, username, pwd, money, bet, sign)
        if success:
            dic["sign"] = RSA.rsa_sign(info)
            dic["success"] = True
            dic["info"] = info
        else:
            dic["sign"] = ""
            dic["success"] = False
    else:
        dic["sign"] = ""
        dic["success"] = False
    return  JsonResponse(dic)

@csrf_exempt
def room(request, pwd):
    if "userid" not in request.POST or "username" not in request.POST or "sign" not in request.POST:
        return redirect("/illegal/")
    userid = request.POST["userid"]
    username = request.POST["username"]
    sign = request.POST["sign"]
    text = userid + username + pwd
    userid = RSA.rsa_decrpt(userid)
    username = RSA.rsa_decrpt(username)
    try:
        id = int(userid)
    except:
        return redirect("/illegal/")
    player = G.findplayer(id, username)
    if not player:
        return redirect("/illegal/")
    success = player.verify(text, sign)
    if not success:
        return redirect("/illegal/")
    croom = G.findroom(pwd)
    if not croom:
        return redirect("/illegal/")
    success = croom.findplayer(player)
    if not success:
        return redirect("/illegal/")
    return render(request, "room.html", {"money": croom.money})

def gotoroom(request):
    dic = {}
    if request.GET:
        id = request.GET["id"]
        username = request.GET["username"]
        sign = request.GET["sign"]
        pwd = request.GET["roompwd"]
        id = RSA.rsa_decrpt(id)
        pwd = RSA.rsa_decrpt(pwd)
        username = RSA.rsa_decrpt(username)
        success, info = G.gotoroom(id, username, pwd, sign)
        if success:
            dic["sign"] = RSA.rsa_sign(info)
            dic["success"] = True
            dic["info"] = info
        else:
            dic["sign"] = ""
            dic["success"] = False
    else:
        dic["sign"] = ""
        dic["success"] = False
    return JsonResponse(dic)

def sit(request, pwd):
    dic = {"success": False}
    if request.GET:
        eid = request.GET["id"]
        eusername = request.GET["username"]
        usit = request.GET["sit"]
        sign = request.GET["sign"]
        id = RSA.rsa_decrpt(eid)
        username = RSA.rsa_decrpt(eusername)
        usit = RSA.rsa_decrpt(usit)
        if len(usit) != 4 or not re.match(r"sit[1-8]", usit):
            return JsonResponse(dic)
        n = int(usit[-1]) - 1
        try:
            id = int(id)
        except:
            return JsonResponse(dic)
        room = G.findroom(pwd)
        if not room:
            return JsonResponse(dic)
        player = G.findplayer(id, username)
        if not player:
            return JsonResponse(dic)
        success = room.findplayer(player)
        if not success:
            return JsonResponse(dic)
        success = player.verify(str(id) + username + usit, sign)
        if not success:
            return JsonResponse(dic)
        success = room.sit(id, username, n, player)
        if not success:
            return JsonResponse(dic)
        dic["success"] = True
        player.set_time()
        return JsonResponse(dic)

def getsit(request, pwd):
    dic = {"success": False}
    if request.GET:
        eid = request.GET["id"]
        eusername = request.GET["username"]
        sign = request.GET["sign"]
        id = RSA.rsa_decrpt(eid)
        username = RSA.rsa_decrpt(eusername)
        try:
            id = int(id)
        except:
            return JsonResponse(dic)
        player = G.findplayer(id, username)
        if not player:
            return JsonResponse(dic)
        room = G.findroom(pwd)
        if not room:
            return JsonResponse(dic)
        success = room.findplayer(player)
        if not success:
            return JsonResponse(dic)
        success = player.verify(str(id) + username, sign)
        if not success:
            return JsonResponse(dic)
        result = room.getSitStatus()
        if player.id == room.players[0].id:
            result["begin"] = False
        else:
            result["begin"] = True
        result = json.dumps(result)
        sign = RSA.rsa_sign(result)
        result = player.cipher.text_encrypt(result)
        dic["success"] = True
        dic["result"] = result
        dic["sign"] = sign
        return JsonResponse(dic)

def getstatus_thread(request, pwd, dic):
    if request.GET:
        eid = request.GET["id"]
        eusername = request.GET["username"]
        sign = request.GET["sign"]
        id = RSA.rsa_decrpt(eid)
        username = RSA.rsa_decrpt(eusername)
        try:
            id = int(id)
        except:
            return
        player = G.findplayer(id, username)
        if not player:
            return
        room = G.findroom(pwd)
        if not room:
            return
        success = room.findplayer(player)
        if not success:
            return
        success = player.verify(str(id) + username, sign)
        if not success:
            return
        result = room.getStatus(player)
        if not result:
            return
        result = json.dumps(result)
        sign = RSA.rsa_sign(result)
        result = player.cipher.text_encrypt(result)
        dic["success"] = True
        dic["result"] = result
        dic["sign"] = sign
        return

def begingame(request, pwd):
    dic = {"success": False}
    if request.GET:
        eid = request.GET["id"]
        eusername = request.GET["username"]
        sign = request.GET["sign"]
        id = RSA.rsa_decrpt(eid)
        username = RSA.rsa_decrpt(eusername)
        try:
            id = int(id)
        except:
            return JsonResponse(dic)
        player = G.findplayer(id, username)
        if not player:
            return JsonResponse(dic)
        room = G.findroom(pwd)
        if not room:
            return JsonResponse(dic)
        success = room.findplayer(player)
        if not success:
            return JsonResponse(dic)
        success = player.verify(str(id) + username, sign)
        if not success:
            return JsonResponse(dic)
        result = room.begingame(player)
        if result:
            dic["success"] = True
        player.set_time()
        return JsonResponse(dic)

def userbet(request, pwd):
    dic = {"success": False}
    if request.GET:
        eid = request.GET["id"]
        eusername = request.GET["username"]
        bet = request.GET["bet"]
        sign = request.GET["sign"]
        id = RSA.rsa_decrpt(eid)
        username = RSA.rsa_decrpt(eusername)
        bet = RSA.rsa_decrpt(bet)
        try:
            id = int(id)
            bet = int(bet)
        except:
            return JsonResponse(dic)
        player = G.findplayer(id, username)
        if not player:
            return JsonResponse(dic)
        room = G.findroom(pwd)
        if not room:
            return JsonResponse(dic)
        success = room.findplayer(player)
        if not success:
            return JsonResponse(dic)
        success = player.verify(str(id) + username + str(bet), sign)
        if not success:
            return JsonResponse(dic)
        success, info = room.userbet(player, bet)
        if not success:
            dic["info"] = player.cipher.text_encrypt(info)
            dic["sign"] = RSA.rsa_sign(info)
        else:
            dic["success"] = True
        player.set_time()
        return JsonResponse(dic)

def call(request, pwd):
    dic = {"success": False}
    if request.GET:
        eid = request.GET["id"]
        eusername = request.GET["username"]
        sign = request.GET["sign"]
        id = RSA.rsa_decrpt(eid)
        username = RSA.rsa_decrpt(eusername)
        try:
            id = int(id)
        except:
            return JsonResponse(dic)
        player = G.findplayer(id, username)
        if not player:
            return JsonResponse(dic)
        room = G.findroom(pwd)
        if not room:
            return JsonResponse(dic)
        success = room.findplayer(player)
        if not success:
            return JsonResponse(dic)
        success = player.verify(str(id) + username, sign)
        if not success:
            return JsonResponse(dic)
        success, info = room.call(player)
        if not success:
            dic["info"] = player.cipher.text_encrypt(info)
            dic["sign"] = RSA.rsa_sign(info)
        else:
            dic["success"] = True
        player.set_time()
        return JsonResponse(dic)

def check(request, pwd):
    dic = {"success": False}
    if request.GET:
        eid = request.GET["id"]
        eusername = request.GET["username"]
        sign = request.GET["sign"]
        id = RSA.rsa_decrpt(eid)
        username = RSA.rsa_decrpt(eusername)
        try:
            id = int(id)
        except:
            return JsonResponse(dic)
        player = G.findplayer(id, username)
        if not player:
            return JsonResponse(dic)
        room = G.findroom(pwd)
        if not room:
            return JsonResponse(dic)
        success = room.findplayer(player)
        if not success:
            return JsonResponse(dic)
        success = player.verify(str(id) + username, sign)
        if not success:
            return JsonResponse(dic)
        success = room.check(player)
        if not success:
            dic["info"] = player.cipher.text_encrypt(info)
            dic["sign"] = RSA.rsa_sign(info)
        else:
            dic["success"] = True
        player.set_time()
        return JsonResponse(dic)

def delete(request, pwd):
    dic = {"success": False}
    if request.GET:
        eid = request.GET["id"]
        eusername = request.GET["username"]
        sign = request.GET["sign"]
        id = RSA.rsa_decrpt(eid)
        username = RSA.rsa_decrpt(eusername)
        try:
            id = int(id)
        except:
            return JsonResponse(dic)
        player = G.findplayer(id, username)
        if not player:
            return JsonResponse(dic)
        room = G.findroom(pwd)
        if not room:
            return JsonResponse(dic)
        success = room.findplayer(player)
        if not success:
            return JsonResponse(dic)
        success = player.verify(str(id) + username, sign)
        if not success:
            return JsonResponse(dic)
        success = room.delete(player)
        if success:
            dic["success"] = True
        if len(room.players) == 0:
            G.rooms.remove(room)
            print(room.pwd, "delete!")
            del room
        player.set_time()
        return JsonResponse(dic)

def returnhome(request):
    if request.GET:
        eid = request.GET["id"]
        eusername = request.GET["username"]
        sign = request.GET["sign"]
        id = RSA.rsa_decrpt(eid)
        username = RSA.rsa_decrpt(eusername)
        try:
            id = int(id)
        except:
            return redirect("/illegal/")
        player = G.findplayer(id, username)
        if not player:
            return redirect("/illegal/")
        success = player.verify(str(id) + username, sign)
        if not success:
            return redirect("/illegal/")
        dic = {}
        id = player.cipher.text_encrypt(str(id))
        dic["id"] = id
        # 以id作签名，攻击者会通过统计攻击猜出id的值，从而伪造数据
        sign = RSA.rsa_sign(id)
        dic["sign"] = sign
        return render(request, "home.html", dic)

def getstatus(request, pwd):
    dic = {"success": False}
    #t = threading.Thread(target = getstatus_thread, args = (request, pwd, dic))
    #t.start()
    #t.join()
    getstatus_thread(request, pwd, dic)
    return JsonResponse(dic)
