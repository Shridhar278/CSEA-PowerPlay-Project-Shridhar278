"""
Checking time to find one schedule : n Teams
using graph theory DFS

1. Single Round Robin: nC2 matches DONE
2. Double Round Robin: 2 * nC2 matches

(optional) no. of schedules found before CRASH:
"""

import time
start = time.perf_counter()
#__________________________________________________________________________________________________________

from itertools import combinations

teams = "ABCDEFGH"

graph = {}

def nC2(n):
    return n * (n - 1) // 2

for match in combinations(teams, 2):
    for next_match in combinations(teams, 2):
        if match != next_match and not set(match).intersection(set(next_match)):
            if match not in graph:
                graph[match] = []
            graph[match].append(next_match)

# print("Graph:", graph)

times=10000

def dfs_srr(schedule, visited, current):
    global times
    if len(schedule) == nC2(len(teams)):  # nC2 matches for double round robin with 8 teams
        print("Schedule found:", schedule)
        times -= 1
        return True
    
    for match in graph[current]:
        if match not in visited:
            # print("Visiting:", match)
            visited.add(match)
            schedule.append(match)
            if dfs_srr(schedule, visited, match):
                if times<=0:
                    return True
            # fail then backtrack
            schedule.pop()
            visited.remove(match)
    
    return False

def find_schedule_srr(param):
    if param:
        # for all starts
        for match in graph.keys():
            visited = set()
            visited.add(match)
            dfs_srr([match], visited, match)
    else:
        # for unique start
        dfs_srr([("A", "B")], set([("A", "B")]), ("A", "B"))



"""
just ORDER MATTERS for DOUBLE ROUND-ROBIN and we are GOOD
"""



def build_drr_graph():
    """Build graph for double round robin where order matters (home vs away)"""
    drr_graph = {}
    
    # Create all ordered matches (A,B) and (B,A) are different
    all_matches = []
    for team1 in teams:
        for team2 in teams:
            if team1 != team2:
                all_matches.append((team1, team2))
    
    # Build adjacency: match can follow another if no team overlap
    for match in all_matches:
        drr_graph[match] = []
        for next_match in all_matches:
            if match != next_match and not set(match).intersection(set(next_match)):
                drr_graph[match].append(next_match)
    
    return drr_graph, all_matches

def dfs_drr(drr_graph, all_matches, schedule, visited, current):
    global times
    target_matches = 2 * nC2(len(teams))  # double round robin
    
    if len(schedule) == target_matches:
        print("Schedule found:", schedule)
        times -= 1
        return True
    
    for match in drr_graph[current]:
        if match not in visited:
            visited.add(match)
            schedule.append(match)
            if dfs_drr(drr_graph, all_matches, schedule, visited, match):
                if times <= 0:
                    return True
            # fail then backtrack
            schedule.pop()
            visited.remove(match)
    
    return False

def find_schedule_drr(param):
    drr_graph, all_matches = build_drr_graph()
    
    if param:
        # for all starts
        for match in drr_graph.keys():
            visited = set()
            visited.add(match)
            dfs_drr(drr_graph, all_matches, [match], visited, match)
    else:
        # for unique start
        start_match = ("A", "B")
        visited = set([start_match])
        dfs_drr(drr_graph, all_matches, [start_match], visited, start_match)


# find_schedule_srr(0)
find_schedule_drr(0)
#__________________________________________________________________________________________________________
end = time.perf_counter()
print(f"Execution time: {end - start:.6f} seconds")