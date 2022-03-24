import datetime
import time
import threading
from . import aes, poke
import hashlib
class Player:
    def __init__(self, name, id, key, g):
        self.g = g
        self.name = name
        self.id = id
        self.key = key
        self.time = datetime.datetime.now()
        self.cipher = aes.GameAES(key)
        self.room = []

    def verify(self, text, sign):
        result = self.cipher.text_decrypt(sign)
        return text == result

    def set_time(self):
        self.time = datetime.datetime.now()

    def delself(self):
        for eachroom in self.room:
            eachroom.delete(self)
            if len(eachroom.players) == 0:
                self.g.rooms.remove(eachroom)
                #print(eachroom.pwd, "delete")
                del eachroom

class Room:
    def __init__(self, pwd, money, player, bet):
        self.pwd = pwd
        self.money = money
        self.players = [player]
        self.bet = bet
        self.sitlist = [[None, None], [None, None], [None, None], [None, None],
                        [None, None], [None, None], [None, None], [None, None]]
        self.usermoney = {player: money}
        self.situser = [None] * 8
        self.status = 0
        self.poke = poke.Poke()
        self.banker = None
        self.banker2 = None
        self.pool = 0
        self.betting = 0
        self.isgame = []
        self.userbetlist = []
        self.public_cards = []
        self.isfirst = True
        self.usercards = [[None, None], [None, None], [None, None], [None, None],
                          [None, None], [None, None], [None, None], [None, None]]
        self.ischange = {}
        self.isfirstsoha = False

    def findplayer(self, player):
        for each in self.players:
            if each.id == player.id and each.name == player.name:
                return True
        return False

    def sit(self, id, username, n, player):
        if self.sitlist[n][1]:
            return False
        if self.status == 33:
            self.status = 0
        if self.status != 0:
            return False
        for i in range(8):
            each = self.sitlist[i]
            if each[0] == id:
                each[0] = None
                each[1] = None
                self.situser[i] = None
                break
        self.sitlist[n][0] = id
        self.sitlist[n][1] = username
        self.situser[n] = player
        for each in self.ischange:
            self.ischange[each] = True
        self.ischange[player] = True
        return True

    def getSitStatus(self):
        dic = {}
        for i in range(1, 9):
            if self.sitlist[i - 1][1]:
                dic["sit" + str(i)] = self.sitlist[i - 1]
            if self.situser[i - 1]:
                dic["money" + str(i)] = self.usermoney[self.situser[i - 1]]
        return dic

    def getStatus(self, player):
        dic = {}
        #if not self.ischange[player]:
        #    return False
        while player in self.ischange and self.ischange[player] == False:
            time.sleep(0.5)
        if player not in self.ischange:
            return False
        self.ischange[player] = False
        if self.status == 0:
            for i in range(1, 9):
                dic["sit" + str(i)] = self.sitlist[i - 1]
                dic["money" + str(i)] = self.usermoney.get(self.situser[i - 1], None)
            dic["begin"] = (player.id != self.players[0].id)
        elif self.status == 1:
            for i in range(8):
                if self.situser[i]:
                    if player.id == self.situser[i].id:
                        dic["card%d1" % (i + 1)] = self.usercards[i][0]
                        dic["card%d2" % (i + 1)] = self.usercards[i][1]
                    elif self.isgame[i] == 3:
                        dic["card%d1" % (i + 1)] = self.usercards[i][0]
                        dic["card%d2" % (i + 1)] = self.usercards[i][1]
                    else:
                        dic["card%d1" % (i + 1)] = "back"
                        dic["card%d2" % (i + 1)] = "back"
                else:
                    dic["card%d1" % (i + 1)] = None
                    dic["card%d2" % (i + 1)] = None
                dic["money" + str(i + 1)] = self.usermoney.get(self.situser[i], None)
            dic["banker"] = self.banker + 1
            dic["op"] = (self.banker + self.status) % 8 + 1
            dic["pool"] = self.pool
            dic["betting"] = self.betting
            dic["count"] = self.userbetlist[self.situser.index(player)]
            for i in range(1, 6):
                dic["public" + str(i)] = None
        elif self.status > 1 and self.status <= 8:
            for i in range(8):
                if self.situser[i]:
                    if player.id == self.situser[i].id:
                        dic["card%d1" % (i + 1)] = self.usercards[i][0]
                        dic["card%d2" % (i + 1)] = self.usercards[i][1]
                    elif self.isgame[i] == 3:
                        dic["card%d1" % (i + 1)] = self.usercards[i][0]
                        dic["card%d2" % (i + 1)] = self.usercards[i][1]
                    else:
                        dic["card%d1" % (i + 1)] = "back"
                        dic["card%d2" % (i + 1)] = "back"
                else:
                    dic["card%d1" % (i + 1)] = None
                    dic["card%d2" % (i + 1)] = None
                dic["money" + str(i + 1)] = self.usermoney.get(self.situser[i], None)
            dic["banker"] = self.banker + 1
            dic["op"] = (self.banker + self.status) % 8 + 1
            dic["pool"] = self.pool
            dic["betting"] = self.betting
            dic["count"] = self.userbetlist[self.situser.index(player)]
            for i in range(1, 6):
                dic["public" + str(i)] = None
        elif self.status > 8 and self.status <= 16:
            for i in range(8):
                if self.isgame[i] == 3:
                    dic["card%d1" % (i + 1)] = self.usercards[i][0]
                    dic["card%d2" % (i + 1)] = self.usercards[i][1]
                dic["money" + str(i + 1)] = self.usermoney.get(self.situser[i], None)
            dic["op"] = (self.banker + self.status) % 8 + 1
            dic["pool"] = self.pool
            dic["betting"] = self.betting
            dic["count"] = self.userbetlist[self.situser.index(player)]
            dic["public1"] = self.public_cards[0]
            dic["public2"] = self.public_cards[1]
            dic["public3"] = self.public_cards[2]
        elif self.status > 16 and self.status <= 24:
            for i in range(8):
                if self.isgame[i] == 3:
                    dic["card%d1" % (i + 1)] = self.usercards[i][0]
                    dic["card%d2" % (i + 1)] = self.usercards[i][1]
                dic["money" + str(i + 1)] = self.usermoney.get(self.situser[i], None)
            dic["op"] = (self.banker + self.status) % 8 + 1
            dic["pool"] = self.pool
            dic["betting"] = self.betting
            dic["count"] = self.userbetlist[self.situser.index(player)]
            dic["public4"] = self.public_cards[3]
        elif self.status > 24 and self.status <= 32:
            for i in range(8):
                if self.isgame[i] == 3:
                    dic["card%d1" % (i + 1)] = self.usercards[i][0]
                    dic["card%d2" % (i + 1)] = self.usercards[i][1]
                dic["money" + str(i + 1)] = self.usermoney.get(self.situser[i], None)
            dic["op"] = (self.banker + self.status) % 8 + 1
            dic["pool"] = self.pool
            dic["betting"] = self.betting
            dic["count"] = self.userbetlist[self.situser.index(player)]
            dic["public5"] = self.public_cards[4]
        elif self.status == 33:
            for i in range(8):
                if self.situser[i]:
                    dic["card%d1" % (i + 1)] = self.usercards[i][0]
                    dic["card%d2" % (i + 1)] = self.usercards[i][1]
                dic["money" + str(i + 1)] = self.usermoney.get(self.situser[i], None)
            i = 0
            for each in self.public_cards:
                dic["public%d" % (i + 1)] = each
                i += 1
            for i in range(1, 9):
                dic["sit" + str(i)] = self.sitlist[i - 1]
                dic["money" + str(i)] = self.usermoney.get(self.situser[i - 1], None)
            dic["begin"] = (player.id != self.players[0].id)
        return dic

    def begingame(self, player):
        if self.status > 0 and self.status < 33:
            return True
        if player.id != self.players[0].id:
            return False
        if self.situser.count(None) > 6:
            return False
        if 8 - self.situser.count(None) != len(self.players):
            return False
        self.getbanker()
        self.getbanker2()
        self.status = 0
        self.pool = 0
        self.betting = 0
        self.betlist = [0] * 8
        self.userbetlist = [0] * 8
        self.public_cards.clear()
        self.isfirstsoha = False
        self.isfirst = True
        self.isgame.clear()#0:无人,1:正常,2:梭哈,3:弃牌
        self.usercards.clear()
        for i in range(8):
            if self.situser[i]:
                self.isgame.append(1)
            else:
                self.isgame.append(0)
            self.usercards.append([None, None])
        success, info = self.userbet(self.situser[self.banker2], self.bet // 2, False, True)
        if not success:
            return False
        success, info = self.userbet(self.situser[self.banker], self.bet, False)
        if not success:
            return False
        self.nextstatus()
        self.poke.shuffle()
        for i in range(8):
            if self.situser[i]:
                for j in range(2):
                    self.usercards[i][j] = self.poke.game_poke.pop()
        for each in self.ischange:
            self.ischange[each] = True
        return True

    def getbanker(self):
        if self.banker == None:
            self.banker = self.situser.index(self.players[0])
        else:
            self.banker = (self.banker + 1) % 8
            while not self.situser[self.banker]:
                self.banker = (self.banker + 1) % 8

    def getbanker2(self):
        self.banker2 = self.banker
        self.banker2 -= 1
        if self.banker2 < 0:
            self.banker2 = 7
        while not self.situser[self.banker2]:
            self.banker2 -= 1
            if self.banker2 < 0:
                self.banker2 = 7

    def userbet(self, player, num, verify = True, posi = False):
        if not posi:
            p = (self.banker + self.status) % 8
        else:
            p = self.situser.index(player)
        if verify:
            if self.status == 0 or self.status == 33:
                return False, "还未开始游戏！"
            if not self.situser[p]:
                return False, "访问错误！"
            if self.situser[p].id != player.id:
                return False, "还未轮到您！"
        if num > self.usermoney[player]:
            return False, "金额不足！"
        if num + self.userbetlist[p] < self.betting:
            if num != self.usermoney[player]:
                return False, "金额错误！"
        self.usermoney[player] -= num
        if self.usermoney[player] == 0:
            self.isgame[p] = 2
        self.userbetlist[p] += num
        self.pool += num
        self.betting = max(self.userbetlist)
        if verify:
            self.nextstatus()
        for each in self.ischange:
            self.ischange[each] = True
        return True, ""

    def nextstatus(self):
        p = (self.banker + self.status + 1) % 8
        #if self.status >= 0 and self.status <= 7:
        if self.status != 8 and self.status != 16 and self.status != 24 and self.status != 32:
            self.status += 1
            if self.isgame[p] != 1:
                self.nextstatus()
            elif self.status == 8 and self.isfirst:
                self.isfirst = False
            elif self.userbetlist[p] == self.betting and self.betting != 0:
                self.nextstatus()
            elif self.isgame.count(1) < 2:
                if self.isfirstsoha:
                    self.nextstatus()
                else:
                    self.isfirstsoha = True
        elif self.status == 8:
            for i in range(8):
                if self.isgame[i] == 1 and self.userbetlist[i] != self.betting:
                    break
            else:
                self.status += 1
                self.userbetlist = [0] * 8
                self.betting = 0
                for _ in range(3):
                    self.public_cards.append(self.poke.game_poke.pop())
                if self.isgame[p] != 1:
                    self.nextstatus()
                elif self.isgame.count(1) < 2:
                    if self.isfirstsoha:
                        self.nextstatus()
                    else:
                        self.isfirstsoha = True
                return
            self.status = 1
            if self.isgame[p] != 1:
                self.nextstatus()
            elif self.isgame.count(1) < 2:
                if self.isfirstsoha:
                    self.nextstatus()
                else:
                    self.isfirstsoha = True
        elif self.status == 16 or self.status == 24:
            for i in range(8):
                if self.isgame[i] == 1 and self.userbetlist[i] != self.betting:
                    break
            else:
                self.status += 1
                self.userbetlist = [0] * 8
                self.betting = 0
                self.public_cards.append(self.poke.game_poke.pop())
                if self.isgame[p] != 1:
                    self.nextstatus()
                elif self.isgame.count(1) < 2:
                    if self.isfirstsoha:
                        self.nextstatus()
                    else:
                        self.isfirstsoha = True
                return
            self.status -= 7
            if self.isgame[p] != 1:
                self.nextstatus()
            elif self.isgame.count(1) < 2:
                if self.isfirstsoha:
                    self.nextstatus()
                else:
                    self.isfirstsoha = True
        elif self.status == 32:
            for i in range(8):
                if self.isgame[i] == 1 and self.userbetlist[i] != self.betting:
                    break
            else:
                self.status += 1
                self.end()
                return
            self.status -= 7
            if self.isgame[p] != 1:
                self.nextstatus()
            elif self.isgame.count(1) < 2:
                if self.isfirstsoha:
                    self.nextstatus()
                else:
                    self.isfirstsoha = True

    def call(self, player):
        if self.status == 0 or self.status == 33:
            return False, "还未开始游戏！"
        p = (self.banker + self.status) % 8
        return self.userbet(player, self.betting - self.userbetlist[p])

    def check(self, player):
        if self.status == 0 or self.status == 33:
            return False, "还未开始游戏！"
        p = (self.banker + self.status) % 8
        if not self.situser[p]:
            return False, "访问错误！"
        if self.situser[p].id != player.id:
            return False, "还未轮到您！"
        if self.betting != self.userbetlist[p]:
            self.isgame[p] = 3
            i = 0
            for each in self.isgame:
                if each == 1 or each == 2:
                    i += 1
            if i == 1:
                self.end()
                for each in self.ischange:
                    self.ischange[each] = True
                return True, ""
        self.nextstatus()
        for each in self.ischange:
            self.ischange[each] = True
        return True, ""

    def end(self):
        if self.status != 33:
            try:
                p = self.isgame.index(1)
            except:
                p = self.isgame.index(2)
            player = self.situser[p]
            self.usermoney[player] += self.pool
            self.status = 33
        else:
            winner = []
            m = 0
            for i in range(8):
                if self.isgame[i] == 0 or self.isgame[i] == 3:
                    continue
                player = self.situser[i]
                if player:
                    hc = self.public_cards.copy()
                    hc.extend(self.usercards[i])
                    s = self.poke.score(hc)
                    if s > m:
                        m = s
                        winner.clear()
                        winner.append(player)
                    elif s == m:
                        winner.append(player)
            for each in winner:
                self.usermoney[each] += (self.pool // len(winner))

    def delete(self, player):
        try:
            self.players.remove(player)
        except:
            #print(player.id, "not in the room", self.players)
            pass
        try:
            posi = self.situser.index(player)
            self.sitlist[posi] = [None, None]
            self.situser[posi] = None
            self.usermoney.pop(player)
            self.ischange.pop(player)
            player.room.remove(self)
        except Exception as s:
            #print(player.id, "exiterror!")
            #print(s)
            pass
        #print(player.id, "exit!")
        for each in self.ischange:
            self.ischange[each] = True
        return True





class Game:
    def __init__(self):
        self.players = []
        self.rooms = []
        self.playersLock = threading.Lock()
        #print("正在启动游戏！")
        self.deleteThread = threading.Thread(target = self.deleteplayer)
        self.deleteThread.start()
        #print("启动游戏成功！")

    def createplayer(self, name, key, sign):
        if len(self.players) > 40:
            return False, "游戏人数超过上线！"
        i = 0
        self.playersLock.acquire()
        for eachplayer in self.players:
            if eachplayer.id != i:
                player = Player(name, i, key, self)
                self.players.insert(i, player)
                break
            i += 1
        else:
            player = Player(name, i, key, self)
            self.players.append(player)
        v = player.verify(name, sign)
        if not v:
            self.players.remove(player)
        self.playersLock.release()
        if v:
            return True, player
        else:
            return False, "访问出错或连接超时！"

    def deleteplayer(self):
        std = datetime.timedelta(minutes = 10)
        #std = datetime.timedelta(seconds = 40)
        while True:
            self.playersLock.acquire()
            for eachplayer in self.players.copy():
                if datetime.datetime.now() - eachplayer.time > std:
                    self.players.remove(eachplayer)
                    #print("delete:", eachplayer.id, eachplayer.name)
                    eachplayer.delself()
            self.playersLock.release()
            time.sleep(300)

    def findplayer(self, id, username):
        for player in self.players:
            if id == player.id and username == player.name:
                return player
        return False

    def findroom(self, pwd):
        for room in self.rooms:
            if pwd == room.pwd:
                return room
        return False

    def createroom(self, id, username, pwd, money, bet, sign):
        try:
            intid = int(id)
            intmoney = int(money)
            intbet = int(bet)
        except:
            return False, "访问异常"
        if len(self.rooms) > 4:
            return False, "房间数达到上限"
        player = self.findplayer(intid, username)
        if not player:
            return False, "访问异常"
        if not player.verify(id + username + pwd + money + bet, sign):
            return False, "访问异常"
        player.set_time()
        pwd = hashlib.md5(pwd.encode("utf-8")).hexdigest()
        if self.findroom(pwd):
            return False, "房间已被创建"
        room = Room(pwd, intmoney, player, intbet)
        self.rooms.append(room)
        player.room.append(room)
        return True, player.cipher.text_encrypt(pwd)

    def gotoroom(self, id, username, pwd, sign):
        try:
            intid = int(id)
        except:
            return False, "访问异常"
        player = self.findplayer(intid, username)
        if not player:
            return False, "访问异常"
        if not player.verify(id + username + pwd, sign):
            return False, "访问异常"
        player.set_time()
        pwd = hashlib.md5(pwd.encode("utf-8")).hexdigest()
        croom = self.findroom(pwd)
        if not croom:
            return False, "房间未创建！"
        croom.players.append(player)
        croom.usermoney[player] = croom.money
        player.room.append(croom)
        return True, player.cipher.text_encrypt(pwd)







