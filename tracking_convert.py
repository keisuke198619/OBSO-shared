

import numpy as np
import pandas as pd
from tqdm import tqdm
import warnings
import pdb
import os
import argparse
warnings.simplefilter('ignore')

# create parser
parser = argparse.ArgumentParser()
parser.add_argument('--id', type=int, default=0, help='id is game id in JLeague data')
args = parser.parse_args()

# set foler name and file name
Jdatafolder = "../JLeagueData"
FMfolder = "/Data_2019FM/"
Jdata_FM = Jdatafolder + FMfolder
event_data_name = "/play.csv"
player_data_name = "/player.csv"
game_date =  os.listdir(path=Jdata_FM)

tracking_data_name1 = "/tracking_1stHalf.csv"
tracking_data_name2 = "/tracking_2ndHalf.csv"

# set game id
game_id = args.id
# set data in event, tracking and player
event_data = pd.read_csv(Jdata_FM+game_date[game_id]+event_data_name, encoding="shift_jis")
player_data = pd.read_csv(Jdata_FM+game_date[game_id]+player_data_name, encoding="shift_jis")
tracking_data1 = pd.read_csv(Jdata_FM+game_date[game_id]+tracking_data_name1, encoding="shift_jis")
tracking_data2 = pd.read_csv(Jdata_FM+game_date[game_id]+tracking_data_name2, encoding="shift_jis")


tracking_home_columns = ['Period', 'Time [s]', 'Home_1_x', 'Home_1_y',
       'Home_2_x', 'Home_2_y', 'Home_3_x', 'Home_3_y', 'Home_4_x', 'Home_4_y',
       'Home_5_x', 'Home_5_y', 'Home_6_x', 'Home_6_y', 'Home_7_x', 'Home_7_y',
       'Home_8_x', 'Home_8_y', 'Home_9_x', 'Home_9_y', 'Home_10_x','Home_10_y', 
       'Home_11_x', 'Home_11_y', 'Home_12_x', 'Home_12_y', 'Home_13_x', 'Home_13_y',
       'Home_14_x', 'Home_14_y', 'ball_x', 'ball_y']
       
tracking_away_columns = ['Period', 'Time [s]', 'Away_1_x', 'Away_1_y',
       'Away_2_x', 'Away_2_y', 'Away_3_x', 'Away_3_y', 'Away_4_x', 'Away_4_y',
       'Away_5_x', 'Away_5_y', 'Away_6_x', 'Away_6_y', 'Away_7_x', 'Away_7_y',
       'Away_8_x', 'Away_8_y', 'Away_9_x', 'Away_9_y', 'Away_10_x','Away_10_y', 
       'Away_11_x', 'Away_11_y', 'Away_12_x', 'Away_12_y', 'Away_13_x', 'Away_13_y',
       'Away_14_x', 'Away_14_y', 'ball_x', 'ball_y']

tracking_home = pd.DataFrame(columns=tracking_home_columns)
tracking_away = pd.DataFrame(columns=tracking_away_columns)

ball_track1 = tracking_data1[tracking_data1["ホームアウェイF"]==0]
ball_track2 = tracking_data2[tracking_data2["ホームアウェイF"]==0]
home_track1 = tracking_data1[tracking_data1["ホームアウェイF"]==1]
home_track2 = tracking_data2[tracking_data2["ホームアウェイF"]==1]
away_track1 = tracking_data1[tracking_data1["ホームアウェイF"]==2]
away_track2 = tracking_data2[tracking_data2["ホームアウェイF"]==2]
# get player jurseynumbers
home_jurseynum_list = list(home_track1["背番号"].unique()) + list(home_track2["背番号"].unique())
home_jurseynum_list = pd.Series(home_jurseynum_list).unique()
if len(home_jurseynum_list) < 14:
    for _ in range(14-len(home_jurseynum_list)):
        home_jurseynum_list = np.append(home_jurseynum_list, -1)
away_jurseynum_list = list(away_track1["背番号"].unique()) + list(away_track2["背番号"].unique())
away_jurseynum_list = pd.Series(away_jurseynum_list).unique()
if len(away_jurseynum_list) < 14:
    for _ in range(14-len(away_jurseynum_list)):
        away_jurseynum_list = np.append(away_jurseynum_list, -1)

# get min and max frame number
min_frame1 = min(home_track1["フレーム番号"])
max_frame1 = max(home_track1["フレーム番号"])
min_frame2 = min(home_track2["フレーム番号"])
max_frame2 = max(home_track2["フレーム番号"])
# calculate frame lenth
frame_len1 = max_frame1 - min_frame1 + 1
frame_len2 = max_frame2 - min_frame2 + 1

Period_label = ([1]*frame_len1) + ([2]*frame_len2)

tracking_home["Period"] = Period_label
tracking_home["Time [s]"] = [i * 0.04 for i in range(frame_len1+frame_len2)]
tracking_away["Period"] = Period_label
tracking_away["Time [s]"] = [i * 0.04 for i in range(frame_len1+frame_len2)]

jurseynum_df = pd.DataFrame(index=list(range(1, 15)), columns=["Home", "Away"])
jurseynum_df["Home"] = home_jurseynum_list
jurseynum_df["Away"] = away_jurseynum_list

# tracking_home_sample = tracking_home.loc[:10]

# first period tracking data
track_index = 0
for frame in tqdm(range(min_frame1, max_frame1+1)):
    ball_x = ball_track1["座標X"][ball_track1["フレーム番号"]==frame]
    ball_y = ball_track1["座標Y"][ball_track1["フレーム番号"]==frame]
    
    if ball_x.nunique()==1 and ball_y.nunique()==1:
        tracking_home["ball_x"].loc[track_index] = np.array(ball_x)[0] / 100
        tracking_home["ball_y"].loc[track_index] = np.array(ball_y)[0] / 100
        tracking_away["ball_x"].loc[track_index] = np.array(ball_x)[0] / 100
        tracking_away["ball_y"].loc[track_index] = np.array(ball_y)[0] / 100
    player_id = 1
    # home team
    for num in home_jurseynum_list:
        home_x = home_track1["座標X"][(home_track1["背番号"]==num)&(home_track1["フレーム番号"]==frame)]
        home_y = home_track1["座標Y"][(home_track1["背番号"]==num)&(home_track1["フレーム番号"]==frame)]
        
        if home_x.nunique()==1 and home_y.nunique()==1:
            tracking_home["Home_{}_x".format(player_id)].loc[track_index] = np.array(home_x)[0] / 100
            tracking_home["Home_{}_y".format(player_id)].loc[track_index] = np.array(home_y)[0] / 100
        player_id += 1
    player_id = 1
    # away team
    for num in away_jurseynum_list:
        away_x = away_track1["座標X"][(away_track1["背番号"]==num)&(away_track1["フレーム番号"]==frame)]
        away_y = away_track1["座標Y"][(away_track1["背番号"]==num)&(away_track1["フレーム番号"]==frame)]
        if away_x.nunique()==1 and away_y.nunique()==1:
            tracking_away["Away_{}_x".format(player_id)].loc[track_index] = np.array(away_x)[0] / 100
            tracking_away["Away_{}_y".format(player_id)].loc[track_index] = np.array(away_y)[0] / 100
        player_id += 1
    track_index += 1

# second period tracking data
for frame in tqdm(range(min_frame2, max_frame2+1)):
    ball_x = ball_track2["座標X"][ball_track2["フレーム番号"]==frame]
    ball_y = ball_track2["座標Y"][ball_track2["フレーム番号"]==frame]
    
    if ball_x.nunique()==1 and ball_y.nunique()==1:
        tracking_home["ball_x"].loc[track_index] = np.array(ball_x)[0] / 100
        tracking_home["ball_y"].loc[track_index] = np.array(ball_y)[0] / 100
        tracking_away["ball_x"].loc[track_index] = np.array(ball_x)[0] / 100
        tracking_away["ball_y"].loc[track_index] = np.array(ball_y)[0] / 100
    player_id = 1
    # home team
    for num in home_jurseynum_list:
        if num == -1:
            break
        home_x = home_track2["座標X"][(home_track2["背番号"]==num)&(home_track2["フレーム番号"]==frame)]
        home_y = home_track2["座標Y"][(home_track2["背番号"]==num)&(home_track2["フレーム番号"]==frame)]
        
        if home_x.nunique()==1 and home_y.nunique()==1:
            tracking_home["Home_{}_x".format(player_id)].loc[track_index] = np.array(home_x)[0] / 100
            tracking_home["Home_{}_y".format(player_id)].loc[track_index] = np.array(home_y)[0] / 100
        player_id += 1
    player_id = 1
    # away_team
    for num in away_jurseynum_list:
        if num == -1:
            break
        away_x = away_track2["座標X"][(away_track2["背番号"]==num)&(away_track2["フレーム番号"]==frame)]
        away_y = away_track2["座標Y"][(away_track2["背番号"]==num)&(away_track2["フレーム番号"]==frame)]
        if away_x.nunique()==1 and away_y.nunique()==1:
            tracking_away["Away_{}_x".format(player_id)].loc[track_index] = np.array(away_x)[0] / 100
            tracking_away["Away_{}_y".format(player_id)].loc[track_index] = np.array(away_y)[0] / 100
        player_id += 1
    track_index += 1

home_file_name = "/home_tracking.csv"
away_file_name = "/away_tracking.csv"
jurseynum_file_name = "/juseynumber.csv"

tracking_home.to_csv(Jdata_FM+game_date[game_id]+home_file_name)
tracking_away.to_csv(Jdata_FM+game_date[game_id]+away_file_name)
jurseynum_df.to_csv(Jdata_FM+game_date[game_id]+jurseynum_file_name)



