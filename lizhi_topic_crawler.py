#coding:utf-8
import urllib
import traceback
import xlwt
from bs4 import BeautifulSoup

CURENCODING = "utf-8"

class TopicCrawler(object):
    def __init__(self):
        self.startpage = 1
        self.endpage = 25
        self.hoturl = "http://www.lizhi.fm/hot/%s.html"

    def get_gender(self, page):
        gender = "未知"
        try:
            soup = BeautifulSoup(page,"lxml")
            userinfo = soup.find_all(class_="user-info-name")
            i = userinfo[0].find_all("i")
            gender_icon = i[0].attrs["class"]
            gender = "男" if gender_icon[0] == 'male-icon' else "女"
        except Exception:
            traceback.print_exc()
        return gender

    def get_page_num(self, page):
        pagesize = 0
        try:
            html = BeautifulSoup(page, "lxml")
            pagenode = html.find_all(class_="page right fontYaHei")
            if pagenode != None and len(pagenode) > 0:
                anodes = pagenode[0].find_all("a")
                pageurl = anodes[-2].attrs["href"]
                pagesize = pageurl.split("/")[-1]
                pagesize = int(pagesize.split(".")[0])
        except Exception:
            traceback.print_exc()
        return pagesize

    def get_homepage(self, homeurl):
        audiourl = homeurl + "/p/%s.html"
        firstpage = audiourl%(1,)
        gender = self.get_gender(urllib.urlopen(firstpage).read())
        pagesize = self.get_page_num(urllib.urlopen(firstpage).read())
        audiolist = list()
        index = -1
        for curindex in range(1, pagesize+1):
            cururl = audiourl%(curindex,)
            html = urllib.urlopen(cururl).read()
            soup = BeautifulSoup(html,"lxml")
            ul = soup.find_all(class_="audioList fontYaHei js-audio-list")
            if ul is not None and len(ul) > 0:
                linodes = ul[0].find_all("li")
                if linodes != None and len(linodes) > 0:
                    for curnode in linodes:
                        try:
                            audiolist.append(curnode.find_all("a")[0].attrs["title"])
                        except Exception:
                            traceback.print_exc()
        return [gender,audiolist]

    def save_excel(self, anchordic):
        wbk = xlwt.Workbook(encoding=CURENCODING)
        sheet = wbk.add_sheet('sheet 1',cell_overwrite_ok=True)
        headers = ["主播名", "性别", "话题"]
        for i in range(0, len(headers)):
            sheet.write(0,i+1,headers[i])
        index = 0
        for name in anchordic.keys():
            for i in range(0, len(anchordic[name]["audiolist"])):
                index = index + 1
                sheet.write(index, 1, name)
                sheet.write(index, 2, anchordic[name]["gender"])
                sheet.write(index, 3, anchordic[name]["audiolist"][i])
        wbk.save('g:/荔枝热榜主播录播话题汇总_20170213.xls'.decode(CURENCODING))

    def start(self):
        print 'start...'
        anchordic = dict()
        for i in range(self.startpage, self.endpage+1):
            print "page",i
            response = urllib.urlopen(self.hoturl%(i,)).read().strip()
            soup = BeautifulSoup(response,"lxml")
            anchor_list = soup.find_all(class_="radio_list")
            for item in anchor_list:
                alabel = item.find_all("a")
                if alabel != None and len(alabel) >= 2:
                    try:
                        name = alabel[1].text.strip()
                        print "fetch ..."
                        anchordic[name] = dict()
                        homeurl = "http:" + alabel[1].attrs["href"]
                        gender,audiolist = self.get_homepage(homeurl)
                        anchordic[name]["gender"] = gender
                        anchordic[name]["audiolist"] = audiolist
                    except Exception:
                        traceback.print_exc()
        self.save_excel(anchordic)
        print "complete!"

if __name__ == '__main__':
    topiccrawler = TopicCrawler()
    topiccrawler.start()
