#!/bin/bash

# visualze OBSO (not compute)
python test_visualize_obso.py 

# compute OBSO
python calculate_obso.py --start_ev 820 --end_ev 823 --data metrica 


# Tutorial (metrica data)
python Tutorial1_GettingStarted.py
python Tutorial2_DelvingDeeper.py
python Tutorial3_PitchControl.py
python Tutorial4_EPV.py