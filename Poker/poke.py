import random
class Poke:
    def __init__(self):
        num = ["02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14"]
        color = ["h", "s", "c", "d"]#红黑梅方
        self.p = [i + j for i in num for j in color]
        self.funclist = [self.isstraightflush,
                         self.isshijo,
                         self.isgroud,
                         self.isstraight,
                         self.isflush,
                         self.issanjo,
                         self.istwojo]

    def shuffle(self):
        self.game_poke = self.p.copy()
        random.shuffle(self.game_poke)

    def score_5(self, hc):
        l = [(int(i[:2]) - 1, i[2]) for i in hc]
        l.sort(key = lambda x: x[0])
        #用一个13位的14进制数对5张牌的大小进行量化
        score = [-1] * 13
        for i in range(8, 13):
            score[i] = l[7 - i][0]
        for i in range(7):
            if score[i] > 0:
                break
            elif score[i] == -1:
                result = self.funclist[i](l, score)
                if result:
                    break
        for j in range(i + 1, 8):
            if score[i] == -1:
                score[i] = 0
        s = 0
        for i in range(13):
            s += score[i] * 14 **(12 - i)
        #print(score)
        return s

    def isstraightflush(self, l, score):
        """判断是否为同花顺"""
        if self.isstraight(l, score) and self.isflush(l, score):
            score[0] = l[-1][0]
            return True
        score[0] = 0
        return False

    def isshijo(self, l, score):
        """判断是否为四条"""
        t = [i[0] for i in l]
        for i in range(2):
            if t.count(t[i]) == 4:
                score[1] = t[i]
                return True
        score[1] = 0
        return False

    def isgroud(self, l, score):
        """判断是否为葫芦"""
        if self.issanjo(l, score) and self.istwojo(l, score):
            score[2] = score[5]
            return True
        score[2] = 0
        return False
        
    def isstraight(self, l, score):
        """判断是否为同花"""
        t = l[0][1]
        for i, j in l:
            if t != j:
                score[3] = 0
                return False
        else:
            score[3] = i
            return True

    def isflush(self, l, score):
        """判断是否为顺子"""
        if l[0][0] == 1 and l[1][0] == 2 and l[2][0] == 3 and l[3][0] == 4 and l[4][0] == 13:
            score[4] = 4
            return True
        t = l[0][0]
        for i, j in l:
            if t != i:
                score[4] = 0
                return False
            t += 1
        else:
            score[4] = i
            return True

    def issanjo(self, l, score):
        """判断是否为三条"""
        t = [i[0] for i in l]
        for i in range(3):
            if t.count(t[i]) == 3:
                score[5] = t[i]
                return True
        score[5] = 0
        return False

    def istwojo(self, l, score):
        """判断是否为一对或两对"""
        t = [i[0] for i in l]
        for i in range(4):
            if t.count(t[i]) == 2:
                m = t[i]
                t.remove(t[i])
                t.remove(t[i])
                for i in range(2):
                    if t.count(t[i]) == 2:
                        score[6] = max(m, t[i])
                        score[7] = min(m, t[i])
                        return True
                score[6] = 0
                score[7] = m
                return True
        score[6] = 0
        score[7] = 0
        return False

    def score(self, hc):
        """"7张牌的最大牌行的值"""
        m = 0
        for i in range(6):
            for j in range(i, 6):#先排i，再排j，也可以是i+1～7，下面要写成j-1
                l = hc.copy()
                l.pop(i)
                l.pop(j)
                m = max(m, self.score_5(l))
        return m

if __name__ == "__main__":
    P = Poke()
    for _ in range(10):
        P.shuffle()
        print(P.game_poke[:7])
        print(P.score(P.game_poke[:7]))
        
