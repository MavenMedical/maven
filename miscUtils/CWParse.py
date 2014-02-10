import urllib.request
import string
import re
import codecs

linkMatcher = re.compile('<a href="(\S*)">(.*)</a>')
nameMatcher = re.compile('<div class="bullet-item item-(\d+).*<p>(.*)</p>')
descMatcher = re.compile('</div><div class="content"><p>(.*)</p>')
descContinueMatcher = re.compile('^<p>(.*)</p>$')
ulMatcher = re.compile('</*ul>')
bulletMatcher = re.compile('^</div><div class="content"><ul>')
bulletParser = re.compile('<li>(.*)</li>')
PRIMARY_DOC = urllib.request.urlopen("http://www.choosingwisely.org/doctor-patient-lists/")
Questions = []

class Question:
    curId = 0
    def __init__(self, IDin, NameIn, DescriptionIn):
        self.ID = IDin
        self.Name = NameIn
        self.Description = DescriptionIn
class QuestionSet:
    curID = 0
    def __init__(self, NameIn):
        self.ID = QuestionSet.curID
        QuestionSet.curID = QuestionSet.curID + 1
        print (QuestionSet.curID)
        self.List = []
        self.Name = NameIn
    def add(self, QIn):
        self.List.append(QIn)
        
def generateCSV(QList):
    f = codecs.open('final_data2.csv', 'w','utf-8')
    for q in QList:
            f.write('{0}\n{1}\n\n'.format(q.Name, q.Description))
    f.close()
def writeHTML(QSets):
    f = codecs.open('htmlTable.html', 'w', 'utf-8')
    f.write('<table>\n')
    for curSet in QSets:
        f.write('<th colspan = 3><h1>{0}</th>\n'.format(curSet.Name))
        for q in curSet.List:
                f.write('<tr><td>{0}</td><td rowspan ="2" width = "150"><input type="radio" form="primary" name="Perform{1}" value="1">Yes'.format(q.Name, q.ID))
                f.write('<br><input type="radio" form="primary" name="Perform{0}" value="0">No</td><td width = "100" rowspan ="2">'.format(q.ID))
                f.write('<center><input type="radio" form="primary" name="Difficulty{0}" value="Easy">Easy<br><input type="radio" form="primary" name="Difficulty{0}"'.format(q.ID))
                f.write('value="Medium">Medium<br><input type="radio" form="primary" name="Difficulty{0}" value="Hard">Hard</center></td></tr>'.format(q.ID))
                f.write('<tr><td><button id = "contentButton{0}" form="primary" type="button" onclick="showContent({0})">Show Details </button><br>'.format(q.ID))
                f.write('<output id="Content{0}"></output></td></tr>\n'.format(q.ID))
    f.write('</table>\n')
    f.close()                     
    
def processDoc(page, QSet):
    curLine = page.readline()
    curName = None
   
    curDesc = None
    while (curLine):
        advance = True
        lineStr = str( curLine, encoding='utf8' )
        nameStatus = nameMatcher.search(lineStr)
        if nameStatus:
            curName = nameStatus.group(2)
        descStatus = descMatcher.search(lineStr)
        if descStatus:
            advance = False
            curDesc = descStatus.group(1)
            
            while True:
                curLine = page.readline()
                lineStr = str(curLine, encoding='utf8' )            
                continueStatus = descContinueMatcher.match(lineStr)
                if (continueStatus):
                    curDesc = '{0}\\n{1}'.format(curDesc, continueStatus.group(1))
                else:
                    break           
            t = Question(Question.curId, curName, curDesc)
            curName = None
            curDesc = None
            Question.curId = Question.curId + 1
            QSet.add(t)

        bulletStatus = bulletMatcher.match(lineStr)
        if bulletStatus:
            advance = False
            curDesc=''
            
            while True:
                curLine = page.readline()
                lineStr = str(curLine, encoding='utf8' )
                while ulMatcher.match(lineStr):
                    curLine = page.readline()
                    lineStr = str(curLine, encoding='utf8' )
                
                bulletContinue = bulletParser.search(lineStr)
                if bulletContinue:
                    curDesc = '{0}-{1}<br>'.format(curDesc, bulletContinue.group(1))
                else:
                    break
            t = Question(Question.curId, curName, curDesc)
            curName = None
            curDesc = None
            Question.curId = Question.curId + 1
            QSet.add(t)            
        if advance:
            curLine = page.readline()
def writeContentArray(QSets):
    f = codecs.open('contentHash.txt', 'w','utf-8')
    f2 = codecs.open('titleHash.txt', 'w', 'utf-8')
    f3 = codecs.open('setsHash.txt', 'w', 'utf-8')
    for curSet in QSets:
        f3.write('SetHash[{0}] = \'{1}\'\n'.format(curSet.ID, curSet.Name))
        for q in curSet.List:
                f.write( 'ContentHash[{0}] = \'{1}\'\n'.format(q.ID, q.Description))
                f2.write('TitleHash[{0}] = \'{1}\'\n'.format(q.ID, q.Name))

    f.close()
    f2.close()
    f3.close()                      
    
def main():
    cur_line = PRIMARY_DOC.readline()
    for x in range(0 , 135):
        cur_line = PRIMARY_DOC.readline()
    lineStr = str( cur_line, encoding='utf8' )
    lineStr = lineStr.split("<strong>")[1]
    split_line = lineStr.split("<li>")
    
    for entry in split_line:
        match = linkMatcher.search(entry)
        if match:
            print('generating QSet under name {0}'.format(match.group(2)))
            QSet = QuestionSet(match.group(2))
            print ("reading")
            curDoc = urllib.request.urlopen(match.group(1))
            processDoc(curDoc, QSet)
            Questions.append(QSet)
    writeContentArray(Questions)
    writeHTML(Questions)                    
main()

    
                 
    
