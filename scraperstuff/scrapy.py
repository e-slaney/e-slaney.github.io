import requests
import json
import pandas as pd

with open("./wash_true_sched.json","r") as file:
    jsonData = json.load(file)

dates = jsonData['dates']
special_list = []
goal_db = pd.DataFrame(columns=['DateTime', 'Shot Type', 'PowerPlay', 'XLocation', 'YLocation'])
count = 0
for i in range(len(dates)):

    curr_page = requests.get('https://statsapi.web.nhl.com' + dates[i]['games'][0]['link'])
    curr_game = json.loads(curr_page.content)
    curr_date = curr_game['gameData']['datetime']['dateTime']

    for obj in curr_game['liveData']['plays']['allPlays']:
        curr_shot_type = ''
        curr_x = ''
        curr_y = ''
        curr_pp = False
        
        curr_keys = obj.keys()
        if ('players' in curr_keys) and ('result' in curr_keys) and ('coordinates' in curr_keys):
            curr_results = obj['result']
            curr_players = obj['players']
            curr_coordinates = obj['coordinates']

            # Check if Event was a goal
            if curr_results['event'] == 'Goal':
                # Check if OVI was scorer
                for list1elem in curr_players:
                    if (list1elem['playerType'] == 'Scorer') and (list1elem['player']['fullName'] == 'Alex Ovechkin'):
                        if 'secondaryType' in curr_results.keys():
                            try:
                                curr_shot_type = curr_results['secondaryType']
                            except: 
                                curr_shot_type = ''
                        else:
                            curr_shot_type = ''                            
                        if(curr_results['strength']['code'] == 'PPG'):
                            curr_pp = False
                        else:
                            curr_pp = True
                        curr_x = curr_coordinates['x']
                        curr_y = curr_coordinates['y']
                        ## Add to our dataframe!
                        data_list = {'DateTime': curr_date, 'Shot Type': curr_shot_type, 'PowerPlay': curr_pp, 'XLocation': curr_x, 'YLocation': curr_y}
                        temp_df = pd.DataFrame([data_list])
                        goal_db = pd.concat([goal_db, temp_df])
                        special_list.append(list1elem['player']['fullName'])
                        
goal_db.to_csv('ovi_goals.csv', index=False)


