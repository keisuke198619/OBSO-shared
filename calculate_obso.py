import Metrica_IO as mio
import Metrica_Viz2 as mviz
import Metrica_Velocities as mvel
import Metrica_PitchControl2 as mpc
import Metrica_EPV as mepv


import numpy as np
import pandas as pd
from tqdm import tqdm
import os
import pdb
import warnings
import re
import argparse

warnings.simplefilter('ignore')

import third_party as thp
import obso_player as obs


# create parser
parser = argparse.ArgumentParser()
parser.add_argument('--id', type=int, default=2, help='game id')
parser.add_argument('--data', type=str, default='metrica', help='dataset')
parser.add_argument('--start_ev', type=int, default=0, help='dataset')
parser.add_argument('--end_ev', type=int, default=0, help='dataset')
# parser.add_argument('--len_event', type=int, default=0, help='dataset')
args = parser.parse_args()

# select game number
game_id = args.id

if args.data == 'metrica':
    # set up initial path to data
    DATADIR = '../metrica-sample-data/data/'

    # read in the event data
    events = mio.read_event_data(DATADIR,game_id)

    # read in tracking data
    tracking_home = mio.tracking_data(DATADIR,game_id,'Home')
    tracking_away = mio.tracking_data(DATADIR,game_id,'Away')

    # Convert positions from metrica units to meters (note change in Metrica's coordinate system since the last lesson)
    tracking_home = mio.to_metric_coordinates(tracking_home)
    tracking_away = mio.to_metric_coordinates(tracking_away)
    events = mio.to_metric_coordinates(events)

    # reverse direction of play in the second half so that home team is always attacking from right->left
    tracking_home,tracking_away,events = mio.to_single_playing_direction(tracking_home,tracking_away,events)

    # Calculate player velocities
    tracking_home = mvel.calc_player_velocities(tracking_home,smoothing=True)
    tracking_away = mvel.calc_player_velocities(tracking_away,smoothing=True)
    Metrica_df = events

# filter:Savitzky-Golay
tracking_home = mvel.calc_player_velocities(tracking_home, smoothing=True) 
tracking_away = mvel.calc_player_velocities(tracking_away, smoothing=True)

# set parameter
params = mpc.default_model_params()
GK_numbers = [mio.find_goalkeeper(tracking_home), mio.find_goalkeeper(tracking_away)]

# load control and transition model
EPV = mepv.load_EPV_grid('EPV_grid.csv')
EPV = EPV / np.max(EPV)
Trans_df = pd.read_csv('Transition_gauss.csv', header=None)
Trans = np.array((Trans_df))
Trans = Trans / np.max(Trans)

# set OBSO data
if args.end_ev == 0:
    args.end_ev = len(Metrica_df)
args.len_event = args.end_ev - args.start_ev
obso = np.zeros((args.len_event, 32, 50))
PPCF = np.zeros((args.len_event, 32, 50)) 
Transition = np.zeros((args.len_event, 32, 50)) 
event_num0 = 0
for event_num, frame in tqdm(enumerate(Metrica_df['Start Frame'][args.start_ev:args.end_ev])):
    event_num += args.start_ev
    if np.isnan(frame):
        obso[event_num0] = np.zeros((32, 50))
        PPCF[event_num0] = np.zeros((32, 50))
        continue
    elif Metrica_df['Team'].loc[event_num]=='Home':
        # check attack direction 1st half or 2nd half
        if Metrica_df.loc[event_num]['Period']==1:
            direction = mio.find_playing_direction(tracking_home[tracking_home['Period']==1], 'Home')
        elif Metrica_df.loc[event_num]['Period']==2:
            direction = mio.find_playing_direction(tracking_home[tracking_home['Period']==2], 'Home')
        PPCF[event_num0], _, _, _ = mpc.generate_pitch_control_for_event(event_num, Metrica_df, tracking_home, tracking_away, params, GK_numbers, offsides=True)

    elif Metrica_df['Team'].loc[event_num]=='Away': 
        # check attack direction 1st half or 2nd half
        if Metrica_df.loc[event_num]['Period']==1:
            direction = mio.find_playing_direction(tracking_away[tracking_away['Period']==1], 'Away')
        elif Metrica_df.loc[event_num]['Period']==2:
            direction = mio.find_playing_direction(tracking_away[tracking_away['Period']==2], 'Away')
        PPCF[event_num0], _, _, _ = mpc.generate_pitch_control_for_event(event_num, Metrica_df, tracking_home, tracking_away, params, GK_numbers, offsides=True)
    
    else:
        obso[event_num0] = np.zeros((32, 50))
        PPCF[event_num0] = np.zeros((32, 50))
        continue
    obso[event_num0], Transition[event_num0] = obs.calc_obso(PPCF[event_num0], Trans, EPV, tracking_home.loc[frame], attack_direction=direction)
    event_num0 += 1 

home_obso, away_obso = obs.calc_player_evaluate_match(obso, Metrica_df, tracking_home, tracking_away, args)

# calculate onball obso
home_onball_obso, away_onball_obso = obs.calc_onball_obso(Metrica_df, tracking_home, tracking_away, home_obso, away_obso, args)
# remove offside player
home_obso, away_obso = obs.remove_offside_obso(Metrica_df, tracking_home, tracking_away, home_obso, away_obso, args)

# save obso in home and away
resultfolder = "../OBSO-data/"+args.data+'/'

if args.data == 'metrica':
    resultfolder += 'game_'+str(game_id) + '_event_'+str(args.start_ev)+"_"+str(args.end_ev)

if not os.path.exists(resultfolder):
    os.makedirs(resultfolder)
    print(f"Directory {resultfolder} created.")

home_obso.to_pickle(resultfolder+'/home_obso.pkl')
away_obso.to_pickle(resultfolder+'/away_obso.pkl')
home_onball_obso.to_pickle(resultfolder+'/home_onball_obso.pkl')
away_onball_obso.to_pickle(resultfolder+'/away_onball_obso.pkl')
print(f"OBSO was saved at {resultfolder}.")


# create figures
# tracking_frame = 1
# attacking_team = 'Home'
# fig,ax = mviz.plot_pitchcontrol_for_tracking( tracking_frame, tracking_home, tracking_away, attacking_team, PPCF[event_num], annotate=True )
fig_dir = "./figure/"+args.data 
if not os.path.exists(fig_dir+"/OBSO"):
    os.makedirs(fig_dir+"/OBSO",exist_ok=True)

# Save the data for visualization testing

save_sample = True
if save_sample:
    event_nums = range(args.start_ev,args.end_ev)
    event_num0 = 2 
    events_ = events.loc[event_nums]
    pass_frame = events_.iloc[event_num0]['Start Frame']

    # Save each variable as a separate CSV file with _processed suffix
    events_.to_csv('./figure/events_processed.csv', index=False)
    tracking_home.loc[pass_frame-10:pass_frame+10].to_csv('./figure/tracking_home_processed.csv', index=False)
    tracking_away.loc[pass_frame-10:pass_frame+10].to_csv('./figure/tracking_away_processed.csv', index=False)
    pd.DataFrame(EPV).to_csv('./figure/EPV_processed.csv', index=False, header=False)
    pd.DataFrame(Transition[event_num0]).to_csv(f'./figure/Transition_processed.csv', index=False, header=False)
    pd.DataFrame(PPCF[event_num0]).to_csv(f'./figure/PPCF_processed.csv', index=False, header=False)
    pd.DataFrame(obso[event_num0]).to_csv(f'./figure/obso_processed.csv', index=False, header=False)
    print("Processed data saved for visualization testing.")
    import pdb; pdb.set_trace()

# create figures
fig,ax = mviz.plot_pitchcontrol_for_event(event_nums[event_num0], events,  tracking_home, tracking_away, EPV, annotate=True, colorbar=True)
fig.savefig(fig_dir+"/OBSO/EPV_"+str(game_id)+"_"+str(event_nums[event_num0])+".png")
fig,ax = mviz.plot_pitchcontrol_for_event(event_nums[event_num0], events,  tracking_home, tracking_away, Transition[event_num0], annotate=True, colorbar=True)
fig.savefig(fig_dir+"/OBSO/Transition_"+str(game_id)+"_"+str(event_nums[event_num0])+".png")
fig,ax = mviz.plot_pitchcontrol_for_event(event_nums[event_num0], events,  tracking_home, tracking_away, PPCF[event_num0], annotate=True, colorbar=True)
fig.savefig(fig_dir+"/OBSO/PPCF_"+str(game_id)+"_"+str(event_nums[event_num0])+".png")
fig,ax = mviz.plot_pitchcontrol_for_event(event_nums[event_num0], events,  tracking_home, tracking_away, obso[event_num0], annotate=True, vmax=0.2, colorbar=True)
fig.savefig(fig_dir+"/OBSO/OBSO_"+str(game_id)+"_"+str(event_nums[event_num0])+".png") 
print(f"OBSO figures were saved at {fig_dir}/OBSO.")
