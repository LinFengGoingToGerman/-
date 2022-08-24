import random,datetime,sys,io
import pandas as pd
from enum import Enum


class PlayType(Enum):
    古原女皮 = 0
    古原男皮 = 1
    现原女皮 = 2
    现原男皮 = 3

namePlayTypeDic = {'古原女皮':PlayType.古原女皮, '古原男皮':PlayType.古原男皮, '现原女皮':PlayType.现原女皮, '现原男皮':PlayType.现原男皮}
playTypeNameDic = {PlayType.古原女皮:'古原女皮', PlayType.古原男皮:'古原男皮', PlayType.现原女皮:'现原女皮', PlayType.现原男皮:'现原男皮'}

PARTICIPANTS_FILEPATH = r"C:\Users\gao_xiaolin\Desktop\reply\GitRepositoryNew\Participants.tsv"
HEROINES_FILEPATH = r"C:\Users\gao_xiaolin\Desktop\reply\GitRepositoryNew\Heroines.tsv"

# 输入路径，读取TSV文件
def readTsvWithPandas(fileName):
    df = pd.read_table(fileName, header = None, index_col = 0)
    df.dropna(axis = 1,how = 'all',inplace = True)
    df.fillna('补位', inplace = True)
    return df

# 输入路径，输出TSV文件
def outputTsvWithPandas(df, fileName):
    df.to_csv(fileName, sep = '\t', header = None, index= False)

# 报名者
class Applicants:
    def __init__(self):
        self.Applicants = []
        self.chooseFemale = False
        self.chooseMale = False
    
    def add(self, applicant):
        self.Applicants.append(applicant)

    class Applicant: 
        def __init__(self, name, playType):
            self.name = name
            self.playType = playType

# 主角
class Heroines:
    def __init__(self):
        self.today = datetime.date.today()
        self.heroines = {}
        # 读取存放主角资料的TSV文件
        dfH = pd.read_table(HEROINES_FILEPATH, header = None, index_col = None)
        heroinesList = dfH.to_numpy().tolist()
        if heroinesList:
            for i in heroinesList:
                name = i[0]
                datet = datetime.datetime.strptime(i[1], '%Y-%m-%d')
                date = datetime.date(datet.year, datet.month, datet.day)
                count = i[2]
                self.heroines[name] = Heroines.Heroine(name, date, count)

    def chooseHeroine(self, applicants):
        # 从候选人中删除最近一月已担任过主角的
        for index, i in enumerate(applicants):
            if i.name in self.heroines and (self.heroines[i.name].date + datetime.timedelta(days=27)) > self.today:
                del applicants[index]
        
        # 如上述操作后仍有候选人，从中随机抽取一位作为本周主角
        if applicants:
            applicant = random.choice(applicants)
            return applicant    

    # 输出主角
    def printHeroines(self, resultList, chooseFemale, chooseMale):
        if not chooseFemale and not chooseMale:
            print('因报名人数过少，本期轮空。')
            return

        print('本期主角：')
        if chooseFemale and chooseMale:
            pass
        elif chooseFemale:
            resultList = [value for value in resultList if value.playType in (PlayType.古原女皮, PlayType.现原女皮)]
            print('因报名人数过少，本期男皮轮空。')
        elif chooseMale:
            resultList = [value for value in resultList if value.playType in (PlayType.古原男皮,PlayType.现原男皮)]
            print('因报名人数过少，本期女皮轮空。')

        for l in resultList:
            print(playTypeNameDic[l.playType] + ':' + l.name)
        
        return resultList

    # 更新存放主角人选的TSV文件
    def outputHeroines(self,resultList):
        for i in resultList:
            # 重复参加：更新末次日期，参加次数+1
            if i.name in self.heroines:
                self.heroines[i.name].date = self.today
                self.heroines[i.name].count += 1
            else:
                self.heroines[i.name] = Heroines.Heroine(i.name, self.today)

        outputList = []
        for j in self.heroines.values():
            outputList.append([j.name, j.date, j.count]) 

        df = pd.DataFrame(outputList)
        outputTsvWithPandas(df,HEROINES_FILEPATH) 

    class Heroine:
        def __init__(self, name, date, count=1):
            self.name = name
            self.date = date
            self.count = count  

# 读取存放参加者资料的TSV文件
df = readTsvWithPandas(PARTICIPANTS_FILEPATH)

# 分古原女皮，古原男皮，现原女皮，现原男皮四项，分别抽取主角。
heroines = Heroines()
resultList = []    

judgeDic = {PlayType.古原女皮:False, PlayType.古原男皮:False, PlayType.现原女皮:False, PlayType.现原男皮:False}
chooseFemale = chooseMale = False
for row in df.itertuples(name=None):
    aps = Applicants() 
    if any(n != '补位' for n in row[1:]):
        for name in row[1:]:
            if name != '补位':
                aps.add(Applicants.Applicant(name, namePlayTypeDic[row[0]]))

    # 抽取主角
    result = heroines.chooseHeroine(aps.Applicants)
    if result:
        resultList.append(result)

# 当缺失任意类型女皮时，取消女皮配对。男皮同理。
if any(af.playType == PlayType.古原女皮 for af in resultList) and any(mf.playType == PlayType.现原女皮 for mf in resultList):
    chooseFemale = True
if any(am.playType == PlayType.古原男皮 for am in resultList) and any(mm.playType == PlayType.现原男皮 for mm in resultList):
    chooseMale = True

# 输出主角
printedList = heroines.printHeroines(resultList, chooseFemale, chooseMale)
# 更新存放主角的文件
heroines.outputHeroines(printedList)







