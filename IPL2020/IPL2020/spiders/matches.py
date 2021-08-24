# -*- coding: utf-8 -*-
from numpy import diff, dsplit
import scrapy
import json
import math as m

class MatchidSpider(scrapy.Spider):
    name = 'matches'
    allowed_domains = ['hs-consumer-api.espncricinfo.com']
    start_urls = ['https://hs-consumer-api.espncricinfo.com/v1/pages/series/schedule?lang=en&seriesId=1210595&fixtures=false']


    '''In "parse" func below I'm parsing the response received from the request sent to "start_urls". Json Reponse contains ids for all the matches
        played in the IPL 2020. "Parse" func is sending request to web pages using these ids and then response is forwarded to the "parse1" func to
        yeild details for both the innings played in that match.
    '''

    def parse(self, response):
       dict=json.loads(response.body)
       count=0
       for x in dict.get('content').get('matches'):             #looping through matchid's
           yield scrapy.Request(url=f"https://hs-consumer-api.espncricinfo.com/v1/pages/match/scorecard?lang=en&seriesId=1210595&matchId={x.get('objectId')}",callback=self.parse1)
    
    
    def parse1(self,response):
        dict=json.loads(response.body)
        x=dict.get('content').get('notes').get('groups')
        
        scorecard=dict.get('content').get('scorecard')
        firstinnings=dict.get('content').get('scorecard').get('innings')[0]
        secondinnings=dict.get('content').get('scorecard').get('innings')[1]
        
        '''Below we are assigning values particular to the innings'''
        
        FirstInningsTeam = str((' ').join([name for name in x[0].get('notes')[0].split(' ') if name!='innings']))
        FirstInningsPPRuns=x[0].get('notes')[1].split('(')[1].split(' ')[2]
        FirstInningsPPWickets= x[0].get('notes')[1].split('(')[1].split(' ')[4]
        FirstInningsExtras=firstinnings.get('extras')
        FirstInningsRuns=firstinnings.get('runs')
        
        SecondInningsTeam=str((' ').join([name for name in x[1].get('notes')[0].split(' ') if name!='innings']))
        SecondInningsPPRuns=x[1].get('notes')[1].split('(')[1].split(' ')[2]
        SecondInningsPPWickets= x[1].get('notes')[1].split('(')[1].split(' ')[4]
        SecondInningsExtras=secondinnings.get('extras')
        SecondInningsRuns=secondinnings.get('runs')
        
        
        '''Below we want to find out which team won: Team that played first inning or the team that played second inning'''
        
        if SecondInningsRuns>FirstInningsRuns:
            firstresult='Lost'
            secondresult='Won'
        elif SecondInningsRuns==FirstInningsRuns:               
            if dict.get('match').get('statusText') in FirstInningsTeam:
                firstresult='Won'
                secondresult='Lost'
            else:
                firstresult='Lost'
                secondresult='Won'
        else:
            firstresult='Won'
            secondresult='Lost'
            
                
        '''Here we are looping through both the innings one by one and yeilding the value to be incorporated into the csv file'''    
        
        for innings in scorecard.get('innings'):
            runs=innings.get('runs')
            legbyes=innings.get('legbyes')
            wickets=innings.get('wickets')
            extrareceive=innings.get('extras')
            fours=0
            sixes=0
            
            '''We are specifying values to the variable according to the inning number'''
            
            if innings.get('inningNumber')==1:
                team=FirstInningsTeam
                ppruns=FirstInningsPPRuns
                ppwickets=FirstInningsPPWickets
                extrasgiven=SecondInningsExtras
                against=SecondInningsTeam
                result=firstresult
                wickettaken=secondinnings.get('wickets')
            else:
                team=SecondInningsTeam
                ppruns=SecondInningsPPRuns
                ppwickets=SecondInningsPPWickets
                extrasgiven=FirstInningsExtras
                against=FirstInningsTeam
                result=secondresult
                wickettaken=firstinnings.get('wickets')
            
            '''Below we are trying to calculate the "mid over runs" and "last four over" runs by looping through "inningOvers" key of the "innings" dictionary '''
       
            mid_over_runs=0
            last_four_over_runs=0
            
            over_played=innings.get('overs')                               
            if type(over_played)==float:                        # If overs has value other than 20 then we are type casting and re-initializing the variable over_played
                over_played=int(m.floor(over_played))+1                 
            
            if over_played<20:                          
                diff=20-over_played              
                for x in range(6,over_played):
                    if x in range(6,16-diff):
                        mid_over_runs+=innings.get('inningOvers')[x].get('overRuns')
                    else:
                        last_four_over_runs+=innings.get('inningOvers')[x].get('overRuns')
            else:
                for x in range(6,over_played):
                    if x in range(6,16):
                        mid_over_runs+=innings.get('inningOvers')[x].get('overRuns')
                    else:
                        last_four_over_runs+=innings.get('inningOvers')[x].get('overRuns')
         
                    
            '''I'm tryin to sum up the number of fours and sixes in an inning'''   
        
            for batsman in innings.get('inningBatsmen'):
                if batsman.get('fours')==None:
                    fours+=0
                else:
                    fours+=batsman.get('fours')

                if batsman.get('sixes')==None:
                    sixes+=0
                else:
                    sixes+=batsman.get('sixes')
            
            '''Now, I want to add columns that keep overall count for each way every batsman got dismissed in an inning
                and also the count of 100s,70s,50s and 30s in an inning.'''
                
            dismiss={}
            hundereds_seventies={'hundred':0,'seventies':0,'fifties':0,'thirties':0}
            for x in innings.get('inningBatsmen'):
                if x.get('dismissalBowler'):
                    dismissal=x.get('dismissalText').get('short')
                    iskeeper=x.get('dismissalFielders')[0].get('isKeeper')
                    if dismissal=='caught' and iskeeper:
                        if 'keeper catch' not in dismiss:
                            dismiss['keeper catch']=1
                        else:
                            dismiss['keeper catch']+=1
                    else:
                        if dismissal not in dismiss:
                            dismiss[dismissal]=1         
                        else:
                            dismiss[dismissal]+=1
                            
                # Now we want to add columns that keep count of 100s,70s,50s and 30s in an inning.
                
                
                if x.get('runs'):
                    if x.get('runs')>=100:
                        hundereds_seventies['hundred']+=1
                    elif x.get('runs')>=75 and x.get('runs')<=99:
                        hundereds_seventies['seventies']+=1
                    elif x.get('runs')>=50 and x.get('runs')<=74:
                        hundereds_seventies['fifties']+=1
                    elif x.get('runs')>=30 and x.get('runs')<=49 :
                        hundereds_seventies['thirties']+=1
                
            
            
                        
            yield {
                    'Team': team,
                    'Runs': runs,
                    'Wickets': wickets,
                    'Fours': fours,
                    'Sixes':sixes,
                    'PowerPlay Runs': ppruns,
                    'PowerPlay Wickets':ppwickets,
                    'Mid Over Runs':mid_over_runs,
                    'Last Four Over':last_four_over_runs,
                    'Extra Receive': extrareceive,
                    'Extra Given':extrasgiven,
                    'Wickets Taken':wickettaken,
                    'Overs':innings.get('overs'),
                    'Run Rate':round(runs/innings.get('overs'),2),
                    'hundred':hundereds_seventies.get('hundred'),
                    'seventies':hundereds_seventies.get('seventies'),
                    'fifties':hundereds_seventies.get('fifties'),
                    'thirties':hundereds_seventies.get('thirties'),
                    'Caught': dismiss.get('caught'),
                    'bowled':dismiss.get('bowled'),
                    'keeper catch':dismiss.get('keeper catch'),
                    'run out':dismiss.get('run out'),
                    'lbw':dismiss.get('lbw'),
                    'hit wicket':dismiss.get('hit wicket'),
                    'Innings':innings.get('inningNumber'),
                    'Super Over':dict.get('match').get('isSuperOver'),
                    'Against':against,
                    'Ground':dict.get('match').get('ground').get('town').get('name'),
                    'Result':result,
                    'DOM':dict.get('match').get('endDate')[0:10]
                    }         
