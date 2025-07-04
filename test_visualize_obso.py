import Metrica_Viz2 as mviz

import pandas as pd
import os


# create figures
fig_dir = "./figure/metrica"
if not os.path.exists(fig_dir+"/OBSO"):
    os.makedirs(fig_dir+"/OBSO",exist_ok=True)

# Extract variables from the loaded data
# Save processed data to CSV files
events = pd.read_csv('./figure/events_processed.csv') # pandas.DataFrame, shape=(len_event, 14)
tracking_home_ = pd.read_csv('./figure/tracking_home_processed.csv') # pandas.DataFrame, shape=(num_frames, 74)
tracking_away_ = pd.read_csv('./figure/tracking_away_processed.csv') # pandas.DataFrame, shape=(num_frames, 64)
EPV = pd.read_csv('./figure/EPV_processed.csv', header=None).values # numpy.ndarray, shape=(32, 50)
Transition = pd.read_csv(f'./figure/Transition_processed.csv', header=None).values # numpy.ndarray, shape=(32, 50)
PPCF = pd.read_csv(f'./figure/PPCF_processed.csv', header=None).values # numpy.ndarray, shape=(32, 50)
obso = pd.read_csv(f'./figure/obso_processed.csv', header=None).values # numpy.ndarray, shape=(32, 50)

event_nums = range(820, 823)
game_id = 2
event_num0 = 2 
frame = 10

# pass_frame = events.loc[event_num0]['Start Frame']
pass_team = events.loc[event_num0].Team
tracking_home = tracking_home_.loc[frame]
tracking_away = tracking_away_.loc[frame]

fig,ax = mviz.plot_pitchcontrol_for_specific_event(pass_team,  tracking_home, tracking_away, EPV, annotate=True, colorbar=True)
fig.savefig(fig_dir+"/OBSO/EPV_"+str(game_id)+"_"+str(event_nums[event_num0])+".png")
fig,ax = mviz.plot_pitchcontrol_for_specific_event(pass_team,  tracking_home, tracking_away, Transition, annotate=True, colorbar=True)
fig.savefig(fig_dir+"/OBSO/Transition_"+str(game_id)+"_"+str(event_nums[event_num0])+".png")
fig,ax = mviz.plot_pitchcontrol_for_specific_event(pass_team,  tracking_home, tracking_away, PPCF, annotate=True, colorbar=True)
fig.savefig(fig_dir+"/OBSO/PPCF_"+str(game_id)+"_"+str(event_nums[event_num0])+".png")
fig,ax = mviz.plot_pitchcontrol_for_specific_event(pass_team,  tracking_home, tracking_away, obso, annotate=True, vmax=0.2, colorbar=True)
fig.savefig(fig_dir+"/OBSO/OBSO_"+str(game_id)+"_"+str(event_nums[event_num0])+".png") 
print(f"OBSO figures were saved at {fig_dir}/OBSO.")
