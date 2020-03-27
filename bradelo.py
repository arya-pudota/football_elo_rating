from urllib.request import urlopen
import json
import ast
import csv
import math

print("Which year(s) (separate by comma for multiple years) do you wish to analyze for?")
x = input()
x = x.split(',')
for i in range(len(x)):
    x[i] = int(x[i])

print("Which years do you want to include postseason games for the years you have selected? (y/n)")
y = input()
y = y.split(',')
for i in range(len(y)):
    y[i] = int(y[i])

#At the first stage, we compile all team data by parsing the three years and setting default ELO
game_json_list = list()

for i in x:
    url_val = "https://api.collegefootballdata.com/games?year=" + str(i)
    with urlopen(url_val) as url:
        s = url.read()
        game_json_list += json.loads(s.decode('utf-8'))

for i in y:
    url_val = "https://api.collegefootballdata.com/games?year=" + str(i)
    url_val+="&seasonType=postseason"
    with urlopen(url_val) as url:
        s = url.read()
        game_json_list += json.loads(s.decode('utf-8'))



game_json_list = sorted(game_json_list, key = lambda i: (i['season'], i['id']))
print("Sorted data by id")
team_score = {}
conf_score = {}
team_conf = {}
team_home_wins = {}
team_away_wins = {}

for i in game_json_list:
    if i['home_conference'] == 'FBS Independents':
        i['home_conference'] = i['home_team']
    elif i['away_conference'] == 'FBS Independents':
        i['away_conference'] = i['away_team']
    team_score[i['home_team']] = 1500.0
    team_score[i['away_team']] = 1500.0
    conf_score[i['home_conference']] = 1500.0
    conf_score[i['away_conference']] = 1500.0
    team_conf[i['home_team']] = i['home_conference']
    team_conf[i['away_team']] = i['away_conference']
    if i['home_team'] not in team_home_wins:
        team_home_wins[i['home_team']] = []
    if i['away_team'] not in team_away_wins:
        team_away_wins[i['away_team']] = []

print("Initialized data structures")

max_year = x[-1]
currentyear = x[0]
total_games = 0
no_right = 0
no_wrong_home_lost = 0
no_wrong_away_lost = 0
home_lost = 0
away_lost = 0
win_percent_mult = 0
for game in game_json_list:
    total_games+=1
    if game['season'] - currentyear > 0:
        print("The current year is", currentyear)
        for i in team_score:
            team_score[i] = 1500 + ((team_score[i]-1500) * 0.67)
        for i in conf_score:
            conf_score[i] = 1500 + ((conf_score[i]-1500) * 0.67)
        print("The accuracy of the model is:", round(no_right/total_games*100,2), "%")
        total_games = 0
        no_right = 0
        currentyear = game['season']
    if game['home_team'] not in team_score:
        team_score[game['home_team']] = 1500.0
        team_conf[game['home_team']] = game['home_conference']
        if game['home_conference'] not in conf_score:
            conf_score['home_conference'] = 1500.0
    if game['away_team'] not in team_score:
        team_score[game['away_team']] = 1500.0
        team_conf[game['away_team']] = game['away_conference']
        if game['away_conference'] not in conf_score:
            conf_score['away_conference'] = 1500.0
    s1, s2 = 0.0, 0.0
    if len(team_home_wins[game['home_team']]) == 15 and len(team_away_wins[game['away_team']]) == 15:
        win_percent_mult = (sum(team_home_wins[game['home_team']]) - sum(team_away_wins[game['away_team']]))/15
        if win_percent_mult > 0:
            win_percent_mult = win_percent_mult ** 2
        else:
            win_percent_mult = -1 * (abs(win_percent_mult) ** 2)
    else:
        win_percent_mult = 0
    r1 = 10.0**((team_score[game['home_team']] * ((conf_score[team_conf[game['home_team']]]/1500.0) ** 0.5))/400.0)
    r2 = 10.0**((team_score[game['away_team']] * ((conf_score[team_conf[game['away_team']]]/1500.0) ** 0.5))/400.0)
    e1 = r1/(r1+r2) + win_percent_mult
    e2 = 1.0 - e1

    if type(game['home_points']) == int and type(game['away_points']) == int:
        if game['neutral_site'] == 0:
            if game['home_points'] > game['away_points']:
                if len(team_home_wins[game['home_team']]) < 15:
                    team_home_wins[game['home_team']].append((conf_score[game['away_conference']]/1500)**2)
                else:
                    del(team_home_wins[game['home_team']][0])
                    team_home_wins[game['home_team']].append((conf_score[game['away_conference']]/1500)**2)
                if len(team_away_wins[game['away_team']]) < 15:
                    team_away_wins[game['away_team']].append(0)
                else:
                    del(team_away_wins[game['away_team']][0])
                    team_away_wins[game['away_team']].append(0)
            else:
                if len(team_home_wins[game['home_team']]) < 15:
                    team_home_wins[game['home_team']].append(0)
                else:
                    del(team_home_wins[game['home_team']][0])
                    team_home_wins[game['home_team']].append(0)
                if len(team_away_wins[game['away_team']]) < 15:
                    team_away_wins[game['away_team']].append((conf_score[game['home_conference']]/1500)**2)
                else:
                    del(team_away_wins[game['away_team']][0])
                    team_away_wins[game['away_team']].append((conf_score[game['home_conference']]/1500)**2)
        k = (game['season']-x[0]+1)/(x[-1]-x[0]+1)*32.0 * math.log(abs(game['home_points'] - game['away_points'])+1, 4) * (2.2/(abs(team_score[game['home_team']]-team_score[game['away_team']])*0.001+2.2))
        if game['home_points'] > game['away_points']:
            away_lost += 1
            if(e1 > e2):
                no_right+=1
            else:
                if game['neutral_site'] == 0:
                    no_wrong_away_lost+=1
            s1 = 1.0
        else:
            home_lost += 1
            if(e1 < e2):
                no_right+=1
            else:
                if game['neutral_site'] == 0:
                   no_wrong_home_lost+=1
            s2 = 1.0
        r1 = 10.0**((team_score[game['home_team']])/400.0)
        r2 = 10.0**((team_score[game['away_team']])/400.0)
        e1 = r1/(r1+r2)
        e2 = 1.0 - e1
        team_score[game['home_team']] += k*(s1-e1)
        team_score[game['away_team']] += k*(s2-e2)
        if game['home_conference'] != game['away_conference']:
            r1 = 10.0**(conf_score[game['home_conference']]/400.0)
            r2 = 10.0**(conf_score[game['away_conference']]/400.0)
            e1 = r1/(r1+r2)
            e2 = 1.0 - e1
            if k*(s1-e1) > 0:
                conf_score[game['home_conference']] += (k*(s1-e1))**0.5
            else: 
                conf_score[game['home_conference']] += -1*(abs((k*(s1-e1)))**0.5)
            if k*(s2-e2) > 0:
                conf_score[game['away_conference']] += (k*(s2-e2))**0.5
            else: 
                conf_score[game['away_conference']] += -1*(abs((k*(s2-e2)))**0.5)


team_adj_score = {}

for i in team_score:
    team_adj_score[i] = team_score[i] * ((conf_score[team_conf[i]]/1500.0) ** 0.5)

sorted_dict = sorted(team_adj_score.items(), key = lambda x: x[1], reverse=True)[:25]
print()
print("The calculated Top 25 by BradELO is:")
for i in range(25):
    print("%-3i %-20s %4.1f" % (i+1, sorted_dict[i][0], sorted_dict[i][1]))
print('\n')
print("The accuracy of the model for final season is:", round(no_right/total_games*100,2), "%")
print("Percentage of games wrongly predicted where home team lost is", round(no_wrong_home_lost/(no_wrong_home_lost+no_wrong_away_lost)*100, 2), "%")
print("Percentage of where home team lost is", round(home_lost/(home_lost+away_lost)*100, 2), "%")
while True:
    print()
    print("Enter match-up to predict win probability (X vs Y, eg. Michigan vs Ohio State")
    in_val = input()
    print("Is the match on neutral ground? (y/n)")
    in_val_2 = input()
    if in_val == "q":
        break
    in_val = in_val.split('vs')
    for i in range(len(in_val)):
        in_val[i] = in_val[i].strip()
    if in_val[0] not in team_score:
        print("Team 1 does not exist")
    elif in_val[1] not in team_score:
        print("Team 2 does not exist")
    else:
        s1, s2 = 0.0, 0.0
        if in_val_2 == 'n':
            if len(team_home_wins[in_val[0]]) == 15 and len(team_away_wins[in_val[1]]) == 15:
                win_percent_mult = (sum(team_home_wins[in_val[0]]) - sum(team_away_wins[in_val[1]]))/15
                if win_percent_mult > 0:
                    win_percent_mult = win_percent_mult ** 2
                else:
                    win_percent_mult = -1 * (abs(win_percent_mult) ** 2)
            else:
                win_percent_mult = 0
        else:
            win_percent_mult = 0
        r1 = 10.0**((team_score[in_val[0]] * ((conf_score[team_conf[in_val[0]]]/1500.0) ** 0.5))/400.0)
        r2 = 10.0**((team_score[in_val[1]] * ((conf_score[team_conf[in_val[1]]]/1500.0) ** 0.5))/400.0)
        e1 = r1/(r1+r2) + win_percent_mult
        e2 = 1.0 - e1
        if e1 > e2:
            print(in_val[0], "is predicted to win the match with a likelihood of", round(e1*100, 2), "%")
        else:
            print(in_val[1], "is predicted to win the match with a likelihood of", round(e2*100, 2), "%")
   
with open('team_data.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    for i in team_score:
        writer.writerow([i, team_score[i] * ((conf_score[team_conf[i]]/1500.0) ** 0.5)])

        

    
    