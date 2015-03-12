from flask import Flask, render_template, url_for, request, redirect, flash, session
from random import randint
import datetime, collections

app = Flask(__name__)

fullWordList=[] #gobal
PATH4FILES = ''
@app.route('/')
def display_home():
    MIN_SRC_WRD_LEN=7
    orgWordFile=PATH4FILES+'words.txt'
    wordsList=[]
    global fullWordList
    i=0
    #Get source word
    with open(orgWordFile) as words:
        for word in words:
            word = word[0:len(word)-1].lower()
            fullWordList.append(word)
            if len(word) >= MIN_SRC_WRD_LEN and word.isalpha() is True:
                wordsList.append(word)
                i+=1

    sourceWord = wordsList[randint(0,i-1)]
    session['srcWrd'] = sourceWord.title()
    session['sTime']= datetime.datetime.now()

    return render_template("game.html",
            the_title="Word Game",
            source_word=session.get('srcWrd'),
            the_time=session.get('sTime').strftime('%H:%M:%S'),
            submit_Ans_url=url_for("display_score"), )

@app.route('/recordScore', methods=["POST"])
def display_score():
    startTime=session.get('sTime')
    sourceWord=session.get('srcWrd').lower()
    endTime = datetime.datetime.now()
    totalTime = endTime.replace(microsecond=0) - startTime.replace(microsecond=0)
    session['elTime']=str(totalTime)

    NO_OF_INPUTS=7
    SPEC_CHAR="'"
    MIN_IN_LEN=3

    incorrectWords=[]
    wordsEntered=[]
    reason=[]
    #Get 7 words from user
    #Assuption - source words cant have apostrophes
    i=0
    entStr = 'word_Entered_'
    while i is not NO_OF_INPUTS:
        wordsEntered.append((request.form[entStr + str(i)]).lower().strip())
        i+=1

    #validate entered words
    i=0
    wrdLen=0
    for i in range(NO_OF_INPUTS):
        correct=True
        if SPEC_CHAR in wordsEntered[i]:
            wrdLen=len(wordsEntered[i])-1
        else:
            wrdLen=len(wordsEntered[i])
        if wrdLen < MIN_IN_LEN:
            reason.append("is too short")
            incorrectWords.append(wordsEntered[i])
        elif wordsEntered[i] == sourceWord:
            reason.append("is a source word")
            incorrectWords.append(wordsEntered[i])
        elif wordsEntered.count(wordsEntered[i])>1:
            reason.append("is entered more than once")
            incorrectWords.append(wordsEntered[i])
        elif wrdLen > len(sourceWord):
            reason.append("it's longer than source word")
            incorrectWords.append(wordsEntered[i])
        elif wordsEntered[i] not in fullWordList:
            reason.append("is not in dictionary")
            incorrectWords.append(wordsEntered[i])
        else:
            c=0
            for c in range(len(wordsEntered[i])):
                if SPEC_CHAR not in wordsEntered[i][c]:
                    if (wordsEntered[i] not in incorrectWords) and ((
                            sourceWord.count(wordsEntered[i][c]) < wordsEntered[i].count(wordsEntered[i][c]))or(
                            wordsEntered[i][c] not in sourceWord)):
                        reason.append("it has incorrect number of letters/used letters not from source word")
                        incorrectWords.append(wordsEntered[i])
                c+=1
        i+=1

    #generate string with invalid words
    cEmpty=0
    incorrWrds=""
    for i in range(len(incorrectWords)):
        if str(incorrectWords[i]) == "":
            cEmpty+=1
        else:
            incorrWrds+=", '"+str(incorrectWords[i])+"' "+reason[i]

    incorrWrds=incorrWrds.lstrip(", ")
    attempt=""
    message=""
    session['noOfInvalWrds'] = str(len(incorrectWords))

    if cEmpty is NO_OF_INPUTS:
        message="You haven't even try! Shame on you."
    elif len(incorrectWords) is cEmpty and cEmpty is not 0:
        message= "All entered words were correct! And you didn't attempt to think of "+session.get('noOfInvalWrds')+ " more words :("
    elif cEmpty is not 0:
        message= "You have "+session.get('noOfInvalWrds')+ " incorrect words, "+str(cEmpty)+" not even attempted! Your incorrect words are: " + incorrWrds+"."
    elif (cEmpty is 0) and (int(session.get('noOfInvalWrds')) != 0):
        message= "You have "+session.get('noOfInvalWrds')+ " incorrect words. Your incorrect words are: " + incorrWrds+"."
    elif int(session.get('noOfInvalWrds')) is 0:
        message="Wow! You have all "+str(NO_OF_INPUTS)+" words correct!"
    else:
        message="WTF?! how did you get here?!"

    session['msg']= message

    #if user wont get 7 correct words then display scores and invite to play again
    if int(session.get('noOfInvalWrds')) is 0:
        #GO TO --RECORD SCORE-- SCREEN
        return render_template("recordScore.html",
                the_title="Word Game",
                msg_for_usr=session.get('msg'),
                the_time=session.get('elTime'),
                submit_score_url=url_for("display_hscores"),)
    else:
        #GO TO --SCORES-- SCREEN
        scoreNamesList=[]
        userName=""
        scoreNamesList=displayScoreBoard(userName);
        return render_template("scores.html",
                the_title="Word Game Scores",
                msg_for_usr=session.get('msg'),
                score_list=scoreNamesList,
                play_again_url=url_for("display_home"),)

@app.route('/hscores',methods=["POST"])
def display_hscores():
    all_ok = True
    if request.form['usr_name'] == '':
        all_ok = False
        flash("Sorry. Please enter your name. Try again")
    if all_ok:
        #save user data
        scrB = PATH4FILES+'scoreBoard.log'
        with open(scrB, 'a') as log:
            print(request.form['usr_name'],session.get('elTime'), file=log)
        scoreNamesList=[]
        userName=request.form['usr_name']
        scoreNamesList=displayScoreBoard(userName);
        return render_template("scores.html",
            the_title="Word Game Scores",
            pos_msg=session.get('posM'),
            msg_for_usr=session.get('msg'),
			score_list=scoreNamesList,
            play_again_url=url_for("display_home"),)
    else:
        #REFRESH --RECORD SCORE-- SCREEN
        return render_template("recordScore.html",
                the_title="Word Game",
                the_time=session.get('elTime'),
                msg_for_usr=session.get('msg'),
                submit_score_url=url_for("display_hscores"),)

def displayScoreBoard(userNam):
    #sort by time
    scrB = PATH4FILES+'scoreBoard.log'
    scoreLogList=scrB
    scoreNamesList=[]
    i=0
    with open(scoreLogList) as words:
        for scoreLine in words:
            scoreNamesList.append(scoreLine[0:len(scoreLine)-1])#delete '\n'
            i+=1
    #sort the list (best times to worse times)
    c=1
    while c is not 0:
        c, i=0, 0
        for i in range(len(scoreNamesList)-1):
            if scoreNamesList[i][scoreNamesList[i].rfind(" ")+1:] > scoreNamesList[i+1][scoreNamesList[i+1].rfind(" ")+1:]:
                scoreNamesList[i], scoreNamesList[i+1] = scoreNamesList[i+1], scoreNamesList[i]
                c+=1
            i+=1
    posMsg=""
    if userNam != '':
        name=request.form['usr_name']
        usrtime=session.get('elTime')
        nameTime=name+" "+usrtime
        scorePos=scoreNamesList.index(nameTime)+1

        if scorePos is 1:
            posMsg="Wow! You're 1st! Congratulations!"
        elif scorePos is 2:
            posMsg=name+" You're "+str(scorePos)+"nd! One more try and you might be 1st!."
        elif scorePos is 3:
            posMsg="So close to 1st place! "+name+" You're "+str(scorePos)+"rd! Maybe one more try?"
        elif scorePos <= 10:
            posMsg="Nice try, "+name+" You maded to Top 10! You're "+str(scorePos)+"th. Better luck next time."
        else:
            posMsg="Nice try, "+name+" You were ranked "+str(scorePos)+". Better luck next time."
    session['posM']= posMsg
    if len(scoreNamesList) > 10:
        scoreNamesList=scoreNamesList[:10]

    return scoreNamesList;

app.config['SECRET_KEY'] = 'thisismysecretkeywhichyouwillneverguesshahahahahahahaha'

def main():
    app.run(debug=True)
if __name__ == "__main__":
    main()
