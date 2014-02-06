import urllib.request
import string
import re
import codecs

linkMatcher = re.compile('<a href="(\S*)".*')
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
        self.Name = NameIn,
        self.Description = DescriptionIn

def generateCSV(QList):
    f = codecs.open('final_data2.csv', 'w','utf-8')
    for q in QList:
            f.write('{0}\n{1}\n\n'.format(q.Name, q.Description))
    f.close()

    
def processDoc(page):
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
                    curDesc = '{0}\n{1}'.format(curDesc, continueStatus.group(1))
                else:
                    break           
            t = Question(Question.curId, curName, curDesc)
            curName = None
            curDesc = None
            Question.curId = Question.curId + 1
            Questions.append(t)

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
                    print("bullet continue")
                    curDesc = '{0}-{1}\n'.format(curDesc, bulletContinue.group(1))
                else:
                    break
            print ('bullet parse evaluated to {0}'.format(curDesc))
        if advance:
            curLine = page.readline()

def main():
    cur_line = PRIMARY_DOC.readline()
    for x in range(0 , 135):
        cur_line = PRIMARY_DOC.readline()
    lineStr = str( cur_line, encoding='utf8' )
    lineStr = lineStr.split("<strong>")[1]
    split_line = lineStr.split("<li>")
    linkList = []
    for entry in split_line:
        match = linkMatcher.search(entry)
        if match:
            linkList.append(match.group(1))
    for entry in linkList:
        print ("reading")
        curDoc = urllib.request.urlopen(entry)
        processDoc(curDoc)
    generateCSV(Questions)    
main()

    
                 
    
