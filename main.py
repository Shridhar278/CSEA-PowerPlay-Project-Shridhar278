import datetime
import time

# TIME STARTS
start = time.perf_counter()
print("Start Time:", datetime.datetime.now())

#________________________________________________________________________________________________________

from loader import load_json, save_json
from classes import Team, Config
from processor import process

# testcases
CASES = {1:"inst_1", 2:"inst_2"}

# testcase change here
CASE=1

# total DFS searches: processv1 = (8c2*2)*LIMIT
LIMIT=50000

# helpers
def map_blackouts(blackouts):
    blackout_dict = {}
    for blackout in blackouts:
        venue = blackout['venue']
        day = blackout['day']
        if venue not in blackout_dict:
            blackout_dict[venue] = []
        blackout_dict[venue].append(day)
    return blackout_dict

def map_teams(teams):
    teams = [Team(**team) for team in teams]
    team_dict = {}
    for team in teams:
        team_dict[team.code] = team
    return team_dict

def map_bids(bids):
    bid_dict = {}
    for bid in bids:
        index = (bid['team_a'], bid['team_b'])
        bid_dict[index] = {"alpha_cr": bid['alpha_cr'],
                            "beta_cr": bid['beta_cr'],
                            "gamma_cr": bid['gamma_cr'],
                            "preferred_days": bid['preferred_days']}
        index = (bid['team_b'], bid['team_a'])
        bid_dict[index] = {"alpha_cr": bid['alpha_cr'],
                            "beta_cr": bid['beta_cr'],
                            "gamma_cr": bid['gamma_cr'],
                            "preferred_days": bid['preferred_days']}
    return bid_dict

def convert_schedule(schedule, alternate):
    solution = []
    for i, match in enumerate(schedule):
        solution.append({
            "day": i+1,
            "home_team": match[0],
            "away_team": match[1],
            "is_alternate": alternate[i]
        })
    return solution

"""
python main.py
"""

files=CASES[CASE]

# load data
teams_json=load_json(f"{files}/teams.json")
travel_matrix=load_json(f"{files}/travel_matrix.json") # untouched for NOW
parameters=load_json(f"{files}/parameters.json")
broadcaster_bids=load_json(f"{files}/broadcaster_bids.json") # untouched for NOW
blackouts_json=load_json(f"{files}/blackouts.json")

# classify data
teams = map_teams(teams_json)
config = Config(**parameters)
blackouts = map_blackouts(blackouts_json)
bids=map_bids(broadcaster_bids)

# process data
schedule, alternate, score = process(teams, travel_matrix, config, bids, blackouts, LIMIT) 

# save data
save_json(convert_schedule(schedule, alternate), f"schedule{CASE}.json")

#________________________________________________________________________________________________________

# TIME ENDS
end = time.perf_counter()
print(f"Execution time: {end - start:.6f} seconds")