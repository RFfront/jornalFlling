from sys import getsizeof
from datetime import date,datetime,timedelta
from pprint import pprint
import numpy as np
import json
import calendar
import hashlib
from calendar import monthrange
import lzma
import numpy as np

from pprint import pprint
import json
from datetime import date,datetime
import xlrd
import calendar
from xlwt.Utils import rowcol_to_cell
import xlwt
from pathlib import Path
__version__="1.5.1"
# import loguru
# import enum

module_dir = Path.cwd()/"journals/"
print("A"*40,module_dir)
module_dir.mkdir(exist_ok=True)

def saveToExcel(array,fn):
    wb = xlwt.Workbook()
    ws = wb.add_sheet("q")
    for i,li in enumerate(array):
        for g,el in enumerate(li):

            ws.write(i,g,el)
    wb.save(f'{fn}.xls')
def loadGroupFromFile():
    fi=None
    groupName=""
    groupList=[]
    try:
        with open(f"group.json","r",encoding="utf-8") as f:
            fi=json.load(f)
        groupName=fi["groupName"]
        groupList=fi["groupList"]

    except Exception:
        with open(f"group.json","w",encoding="utf-8") as f:
            f.write('{"groupName": "","groupList": []}')
    return groupName, groupList


def loadGroupToFile(groupName,groupList):
    try:
        with open("group.json",mode="w", encoding="utf-8") as f:
            json.dump({"groupName":groupName,"groupList":groupList},f, indent=4, ensure_ascii=False)
    except Exception:
        pass

class Page():

    __slots__=("discName","people","dates","arr")
    def __init__(self,discName,people,dates,arr=None):
        self.discName=discName
        self.people=tuple(people)
        if type(dates[0])==str:
            self.dates=[datetime.strptime(i,'%Y%m%d').date() for i in dates]
        else:
            self.dates = dates
        needSize=(len(people),len(dates))
        if arr == None:
            self.arr=np.zeros(shape=needSize,dtype=np.dtype("uint8"))
        elif isinstance(arr,np.ndarray):
            if arr.shape ==needSize:
                self.arr=arr
            else:
                raise ValueError(f"Different shapes,acepted={arr.shape},need to be {needSize}")
        elif isinstance(arr,bytes):
            self.arr = np.reshape(np.frombuffer(arr, dtype=np.uint8),newshape=needSize)
        else:
            arr=np.array(arr,dtype=np.dtype("uint8"))
            if arr.shape ==needSize:
                self.arr=arr
            else:
                raise ValueError(f"Different shapes,acepted={arr.shape},need to be {needSize}")

    def onlyMark(self,id:int,start=None,end=None):
        serList,_,_=self.selection(id,start,end)
        return [i for i in serList if i!=0 and i!=11]

    def average(self,id:int,start=None,end=None):
        li=self.onlyMark(id,start,end)
        try:
            return round(sum(li)/len(li),ndigits=2),(sum(li),len(li))
        except ZeroDivisionError:
            return 0,(0,0)

    def selection(self,id:int,start,end):
        "accept date obj not datetime"
        id=self.people.index(id)
        serList=None
        if start!=None and end!=None:
            a=list(
            set([(start + timedelta(days=x)) for x in range(0, (end-start).days+1)])
            &set(self.dates)
            )
            a.sort()
            if a!=[]:
                start=self.dates.index(a[0])
                end=self.dates.index(a[-1])
                for endid in range(end+1,len(self.dates)):
                    if self.dates[endid]==a[-1]:
                        end=endid
                end+=1
                serList=self.arr[[id], start:end]
            else:
                serList=np.array([[]],dtype=np.dtype("uint8"))
        else:
            serList=self.arr[[id], :]
        return serList[0],start,end

    def percent(self,id):
        serList=self.skiped(id,None,None)
        return round(len(serList)/self.arr.shape[1]*100,2)

    def skiped(self,id:int,start=None,end=None):
        serList,start,end=self.selection(id,start,end)
        return [self.dates[start:end][i] for i in np.where(serList == 11)[0]]

    def toDict(self):
        di={}
        di["discName"]=self.discName
        di["people"]=self.people
        di["dates"]=[i.strftime('%Y%m%d') for i in self.dates]
        di["arr"]=self.arr.tobytes().decode("utf-8")
        return di

    def loadFromSite(self,dates,array):
        dates=[datetime.strptime(i, '%Y-%m-%d').date() for i in dates]
        self.dates=dates
        needSize=(len(self.people),len(self.dates))
        for i,el in enumerate(array):
            for j,el2 in enumerate(el):
                array[i][j]=0 if array[i][j]==' ' else array[i][j]
                array[i][j]=0 if array[i][j]=='' else array[i][j]
                array[i][j]=11 if array[i][j]=='н' else array[i][j]
                array[i][j]=int(array[i][j])
        arr=np.array(array,dtype=np.dtype("uint8"))
        if arr.shape ==needSize:
            self.arr=arr

    def append(self,item:np.ndarray,dat = None):
        if dat == None:
            dat=[date.today()]
        if item.shape[0]==self.arr.shape[0]:
            self.arr=np.append(self.arr,item,axis=1)
            self.dates.extend(dat)
        else:
            raise AttributeError("different shapes")


class Journal:
    __slots__=("pages","groupList","groupname","bordersStyleMassive","style0","styleOnlyTNR")
    monthList=(
    "",
    "Январь",
    "Февраль",
    "Март",
    "Апрель",
    "Май",
    "Июнь",
    "Июль",
    "Август",
    "Сентябрь",
    "Октябрь",
    "Ноябрь",
    "Декабрь"
    )
    """Class represents and operates whole journal"""
    def __init__(self, pages,groupList,grname):
        self.pages = pages
        self.groupList = groupList
        self.groupname = grname

    def view(self,ind:int):
        pg=self.pages[ind]
        dates=[i.strftime("%Y-%m-%d") for i in pg.dates]
        di={}
        for i,fi in enumerate(pg.people):
            ar=pg.arr[i].tolist()
            for h in range(len(ar)):
                ar[h]='' if ar[h]==0 else ar[h]
                ar[h]='н' if ar[h]==11 else ar[h]
            di[i+1]=[
                self.groupList[fi],
                ar
            ]
        return dates,di

    def onlyMarkAll(self,month,year):
        start=date(year,month,1)
        dayInMonth=monthrange(year, month)[1]
        end=date(year,month,dayInMonth)
        pgs=[]
        for i in self.pages:
            pg=[]
            for id in range(len(self.groupList)):
                try:
                    pg+=[i.onlyMark(id,start,end)]
                except ValueError:
                    pg+=[[]]
            pgs+=[pg]
        return pgs

    def average(self,id,start=None,end=None):
        sum=0
        num=0
        for i in self.pages:
            try:
                _,(sumT,numT)=i.average(id,start,end)
            except ValueError:
                sumT,numT=0,0
            sum+=sumT
            num+=numT
        try:
            return round(sum/num,ndigits=2)
        except ZeroDivisionError:
            return 0

    def percent(self,id):
        pass

    def skiped(self,id:int,month,year):
        start=date(year,month,1)
        dayInMonth=monthrange(year, month)[1]
        end=date(year,month,dayInMonth)

        skp=[]
        for i in self.pages:
            try:
                s=i.skiped(id,start,end)
                for dat in s:
                    skp+=[[i.discName,dat.day]]
            except ValueError:
                pass

        nDates= set([i[1] for i in skp])
        dateDictNames={x:[]for x in nDates}
        for dateT in nDates:
            for i in skp:
                if i[1]==dateT:
                    dateDictNames[dateT].append(i[0])

        nByMonth=[0 for i in range(dayInMonth)]

        for dateT in nDates:
            nByMonth[dateT-1]=len(dateDictNames[dateT])
        return dateDictNames,nByMonth

    @classmethod
    def fromFile(cls,filepath):
        with lzma.open(filepath, "r") as lzf:
            dum1=lzf.read().decode('utf-8')
        k=json.loads(dum1)
        tmp=[]
        for i in k["pages"]:
            i["arr"]=i["arr"].encode("utf-8")
            tmp.append(Page(**i))
        k["pages"]=tmp
        return cls(**k,grname=filepath.stem.split(".")[0])

    @classmethod
    def fromExel(cls,pat):
        ReadedBook = xlrd.open_workbook(pat,formatting_info=True)
        ListNames=ReadedBook.sheet_names()
        sheetsWithData=[[i.row_values(rn)[1:] for rn in range(i.nrows)] for i in ReadedBook.sheets()]

        #del empty rows
        emptyRows=[]
        for i,name in enumerate(sheetsWithData):
            for g,row in enumerate(name[1:]):
                if row[0].strip()=='':
                    emptyRows.append((i,g+1))

        for i in range(len(emptyRows)-1,-1,-1):
            del sheetsWithData[emptyRows[i][0]][emptyRows[i][1]]

        def toUint8(val):
            val=0 if val==' ' else val
            val=0 if val=='' else val
            val=11 if val=='н' else val
            return int(val)
        grName,grlist=loadGroupFromFile()
        jorn=cls([],grlist,grName.upper())
        for i,el in enumerate(sheetsWithData):
            tmp=Page(
                ListNames[i],
                [jorn.groupList.index(rt[0]) for rt in el[1:]],
                [date(1,1,1)])
            for h,datej in enumerate(el[0][1:]):
                if type(datej)==float:
                    datej=xlrd.xldate_as_datetime(datej,ReadedBook.datemode).date()
                    mamm=np.array(list(map(toUint8,[k[h+1] for k in el[1:]])),dtype=np.uint8)
                    mamm=np.reshape(mamm,(-1,1))
                    tmp.append(mamm,[datej])
            jorn.pages.append(tmp)
        # jorn.saveToFile()
        return jorn

    def saveToFile(self):
        di={}
        di["pages"]=[i.toDict() for i in self.pages]
        di["groupList"]=self.groupList
        dum0=json.dumps(di)

        with lzma.open(module_dir/f"{self.groupname}.Jornl", "w") as lzf:
            lzf.write(dum0.encode('utf-8'))

        with lzma.open(module_dir/f"{self.groupname}.Jornl", "r") as lzf:
            dum1=lzf.read().decode('utf-8')

        if(dum0==dum1):
            print("file correct writen")
        else:
            print("error writing file")

    def stylesDefenition(self):
        self.bordersStyleMassive=[[],[]]

        self.style0=xlwt.XFStyle()
        self.styleOnlyTNR = xlwt.XFStyle()

        font0 = xlwt.Font()
        font0.name = 'Times New Roman'
        self.styleOnlyTNR.font=font0
        self.style0.font = font0

        alignmentObj=xlwt.Alignment()
        self.style0.alignment = alignmentObj
        self.style0.alignment.horz= alignmentObj.HORZ_CENTER
        self.style0.alignment.vert=alignmentObj.VERT_CENTER

        bord=xlwt.Borders()
        self.style0.borders=bord
        self.style0.borders.left   = bord.MEDIUM
        self.style0.borders.right  = bord.MEDIUM
        self.style0.borders.top    = bord.MEDIUM
        self.style0.borders.bottom = bord.MEDIUM

    def retStyle(self,cube0_r,cube_r,cube0_c,cube_c,actual_r,actual_c):
        tmpBoles=[
            actual_r==cube0_r,
            actual_r==cube_r,
            actual_c==cube0_c,
            actual_c==cube_c
        ]
        if tmpBoles in self.bordersStyleMassive[0]:
            tmpSt=self.bordersStyleMassive[1][self.bordersStyleMassive[0].index(tmpBoles)]
        else:
            tmpSt=xlwt.XFStyle()
            b=xlwt.Borders()
            tmpSt.borders=b
            tmpSt.borders.top = b.MEDIUM if tmpBoles[0] else b.THIN
            tmpSt.borders.bottom = b.MEDIUM if tmpBoles[1] else b.THIN
            tmpSt.borders.left = b.MEDIUM if tmpBoles[2] else b.THIN
            tmpSt.borders.right = b.MEDIUM if tmpBoles[3] else b.THIN

            self.bordersStyleMassive[1].append(tmpSt)
            self.bordersStyleMassive[0].append(tmpBoles)

        return tmpSt

    def makeOtzOtch(self,month,year):
        nums='0123456789'
        ListNames=[i.discName for i in self.pages]
        NEwwListNames=ListNames.copy()
        for i in range(len(NEwwListNames)):
            for j in nums:
                NEwwListNames[i]=NEwwListNames[i].replace(j,'')

        emptyL=[[] for n in self.groupList]
        predm=self.onlyMarkAll(month,year)


        optimizedNames=[]
        optimizedPredm=[]
        m=0
        for i in NEwwListNames:
            if i not in optimizedNames:
                optimizedNames.append(i)
                optimizedPredm.append(predm[m])
            else:
                optimizedNamesIndex=optimizedNames.index(i)
                for peple in range(len(optimizedPredm[optimizedNamesIndex])):
                    optimizedPredm[optimizedNamesIndex][peple].extend(predm[m][peple])
            m+=1

        predm=optimizedPredm
        for i in range(len(predm)):
            if predm[i]==emptyL:
                predm[i].clear()

        for i in range(len(predm)):
            if len(predm[i])!=0:
                max=0
                for j in predm[i]:
                    if len(j)>max:max=len(j)
                if max<3:max=3
                for j in range(len(predm[i])):
                    while len(predm[i][j])<max:
                        predm[i][j].append('')
        return predm,optimizedNames

    def saveaOtzOtchj(self,month,year):
        self.stylesDefenition()
        OtzOtch,optimizedNames=self.makeOtzOtch(month,year)
        monthName = self.monthList[month]

        maxFIOlen=2
        for i in self.groupList:
            if len(i)>maxFIOlen:maxFIOlen=len(i)
        v=f'Успеваемость за {monthName} {year} -  группа {self.groupname}'


        wb = xlwt.Workbook()
        ws = wb.add_sheet(f'отчёт {monthName}')
        totalLen=2
        for i in range(len(OtzOtch)):
            if len(OtzOtch[i])!=0:
                totalLen+=len(OtzOtch[i][0])
        ws.write_merge(0, 0, 0, totalLen, v, self.style0)

        ws.write_merge(1,1,0, 1, "ФИО", self.style0)
        #ws.write(row,coll,data,style)

        for i in range(len(self.groupList)):
            ws.write(i+2,0,i+1,self.retStyle(2,2+len(self.groupList)-1,0,1,i+2,0))
            ws.write(i+2,1,self.groupList[i],self.retStyle(2,2+len(self.groupList)-1,0,1,i+2,1))
        lastRow=2
        lastColl=2
        for i in range(len(OtzOtch)):
            if len(OtzOtch[i])!=0:
                thatColWidth=len(OtzOtch[i][0])
                lastPredmCol=lastColl
                ws.write_merge(1,1,lastPredmCol,lastPredmCol+thatColWidth-1,optimizedNames[i],self.style0)
                for h in range(len(OtzOtch[i])):
                    for b in range(len(OtzOtch[i][h])):
                        boxStyle=self.retStyle(lastRow,lastRow+len(self.groupList)-1,lastPredmCol,lastPredmCol+thatColWidth-1,lastRow+h,lastColl+b)
                        towr=int(OtzOtch[i][h][b]) if OtzOtch[i][h][b]!='' else OtzOtch[i][h][b]
                        ws.write(lastRow+h,lastColl+b,towr,boxStyle)
                lastColl+=thatColWidth

        ws.write(1,lastColl,"Сред.",self.style0)
        for i in range(len(self.groupList)):
            boxStyle=self.retStyle(lastRow,lastRow+len(self.groupList)-1,lastColl,lastColl,lastRow+i,lastColl)
            boxStyle.num_format_str="0.00"
            ws.write(lastRow+i,lastColl,
            xlwt.Formula(f"AVERAGE({rowcol_to_cell(2+i,2)}:{rowcol_to_cell(lastRow+i,lastColl-1)})"),
            boxStyle
            )
        boxStyle=self.retStyle(lastRow+len(self.groupList),lastRow+len(self.groupList),lastColl,lastColl,lastRow+len(self.groupList),lastColl)
        boxStyle.num_format_str="0.00"

        ws.write(lastRow+len(self.groupList),lastColl,
        xlwt.Formula(f"AVERAGE({rowcol_to_cell(2,lastColl)}:{rowcol_to_cell(lastRow+len(self.groupList)-1,lastColl)})"),
        boxStyle
        )
        ws.col(0).width =256*3
        ws.col(1).width =256*maxFIOlen
        for i in range(2,lastColl):
            ws.col(i).width = 256*3
        wb.save(f'{v}.xls')

    def saveNkiOtch(self,month,year,yBchac=None):
        self.stylesDefenition()
        mLen=monthrange(year, month)[1]
        monDays=[i for i in range(1,mLen+1)]
        monthName = self.monthList[month]
        maxFIOlen=2
        for i in self.groupList:
            if len(i)>maxFIOlen:maxFIOlen=len(i)
        v=f'Пропуски за {monthName} {year} -  группа {self.groupname}'

        wb = xlwt.Workbook()
        ws = wb.add_sheet(f'отчёт {monthName}')

        ws.write_merge(0, 0, 0, mLen+2+2, v, self.style0)

        ws.write_merge(1,1,0, 1, "ФИО", self.style0)
        #ws.write(row,coll,data,style)
        lastRow=2
        lastColl=2

        for i in range(len(self.groupList)):
            ws.write(i+2,0,i+1,self.retStyle(2,2+len(self.groupList)-1,0,1,i+2,0))
            ws.write(i+2,1,self.groupList[i],self.retStyle(2,2+len(self.groupList)-1,0,1,i+2,1))

        for i in range(mLen):
            ws.write(1,i+2,monDays[i],self.retStyle(1,1,2,2+mLen-1,1,i+2))

        for i in range(len(self.groupList)):
            toWrite=self.skiped(i,month,year)[1]
            for g in range(mLen):
                boxStyle=self.retStyle(2,2+len(self.groupList)-1,2,2+mLen-1,lastRow+i,lastColl+g)
                wr=toWrite[g]
                wr=None if wr==0 else wr
                ws.write(lastRow+i,lastColl+g,wr,boxStyle)

        ws.write(1,lastColl+mLen,"всего",self.style0)
        ws.write(1,lastColl+mLen+1,"уваж.",self.style0)
        ws.write(1,lastColl+mLen+2,"неуваж.",self.style0)
        allAll=[]
        if yBchac==None:
            yBchac=[0 for i in self.groupList]

        for i in range(len(self.groupList)):
            ws.write(lastRow+i,lastColl+mLen,
            xlwt.Formula(f"sum({rowcol_to_cell(2+i,2)}:{rowcol_to_cell(lastRow+i,lastColl+mLen-1)})"),
            self.retStyle(2,2+len(self.groupList)-1,lastColl+mLen,lastColl+mLen,lastRow+i,lastColl+mLen))

        ws.write(lastRow+len(self.groupList),lastColl+mLen,
        xlwt.Formula(f"sum({rowcol_to_cell(lastRow,lastColl+mLen)}:{rowcol_to_cell(lastRow+len(self.groupList)-1,lastColl+mLen)})"),
        self.retStyle(lastRow+len(self.groupList),lastRow+len(self.groupList),lastColl+mLen,lastColl+mLen,lastRow+len(self.groupList),lastColl+mLen)
        )

        for i in range(len(self.groupList)):
            ws.write(lastRow+i,lastColl+mLen+1,yBchac[i],self.retStyle(2,2+len(self.groupList)-1,lastColl+mLen+1,lastColl+mLen+1,lastRow+i,lastColl+mLen+1))
        ws.write(lastRow+len(self.groupList),lastColl+mLen+1,
        xlwt.Formula(f"sum({rowcol_to_cell(lastRow,lastColl+mLen+1)}:{rowcol_to_cell(lastRow+len(self.groupList)-1,lastColl+mLen+1)})"),
        self.retStyle(lastRow+len(self.groupList),lastRow+len(self.groupList),lastColl+mLen+1,lastColl+mLen+1,lastRow+len(self.groupList),lastColl+mLen+1)
        )

        for i in range(len(self.groupList)):
            ws.write(lastRow+i,lastColl+mLen+2,
            xlwt.Formula(f"{rowcol_to_cell(lastRow+i,lastColl+mLen)}-{rowcol_to_cell(lastRow+i,lastColl+mLen+1)})"),
            self.retStyle(2,2+len(self.groupList)-1,lastColl+mLen+2,lastColl+mLen+2,lastRow+i,lastColl+mLen+2))
        ws.write(lastRow+len(self.groupList),lastColl+mLen+2,
        xlwt.Formula(f"sum({rowcol_to_cell(lastRow,lastColl+mLen+2)}:{rowcol_to_cell(lastRow+len(self.groupList)-1,lastColl+mLen+2)})"),
        self.retStyle(lastRow+len(self.groupList),lastRow+len(self.groupList),lastColl+mLen+2,lastColl+mLen+2,lastRow+len(self.groupList),lastColl+mLen+2)
        )
        ws.col(0).width =256*3
        ws.col(1).width =256*maxFIOlen
        for i in range(2,mLen+2):
            ws.col(i).width = 256*3
        wb.save(f'{v}.xls')

if __name__ == '__main__':
    b=Journal.fromFile(module_dir/"﻿23-П.Jornl")
    # b.pages[4].percent(20)
    print(b.groupList[0])
    # print(b.skiped(0,11,2021))
    b.saveaOtzOtchj(11,2021)
    b.saveNkiOtch(11,2021)
    # print(b.pages[0].onlyMark(7))
    # print(b.pages[0].average(7))
    # print(b.skiped(1,11,2021))
    # print(b.onlyMarkAll(11,2021))
    #IDGAF
