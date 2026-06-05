from math import inf
import datetime


from classes import Team, Config
from math_models import objective_func, preliminary_checks


def _build_drr_graph(team_codes: list[str]) -> tuple[dict[tuple[str, str], list[tuple[str, str]]], list[tuple[str, str]]]:
    """Build the ordered double round robin adjacency graph."""
    all_matches: list[tuple[str, str]] = [
        (home, away)
        for home in team_codes
        for away in team_codes
        if home != away
    ]

    drr_graph: dict[tuple[str, str], list[tuple[str, str]]] = {}
    
    for match in all_matches:
        drr_graph[match] = [
            next_match
            for next_match in all_matches
            if match != next_match and not set(match).intersection(next_match)
        ]
    return drr_graph, all_matches


def processv5(teams : dict[str, Team],
            travel_matrix : dict[str, dict[str, float]],
            config : Config,
            bids : dict[tuple[str, str], dict],
            blackouts : dict[str, list[int]],
            limit: int | None = None):
        
    """Find the best ordered double round robin schedule with DFS."""
 
    team_codes = list(teams.keys())
    drr_graph, all_matches = _build_drr_graph(team_codes)
    target_matches = len(all_matches)

    best_schedule: list[tuple[str, str]] = []
    best_alternate: list[bool] = []
    best_score = -inf
    remaining = limit

    alt_limit = {}
    empty_alts = {}
    for team in teams.values():
        if team.alt_venue:
            alt_limit[team.code]=2
        else:
            alt_limit[team.code]=0
        empty_alts[team.code]=0

    kill=False

    def dfs(current: tuple[str, str],
            schedule: list[tuple[str, str]],
            isalternate: list[bool],
            visited: set[tuple[str, str]],
        appearances: dict[str, int],
           alternates: dict[str, int]) -> None:
        
        nonlocal best_schedule, best_score, best_alternate, remaining
        nonlocal kill
        nonlocal first

        # print("DFS at depth", len(schedule), "with current match", current)
        # print("Appearances:", appearances)
        # print("Current schedule:", schedule)

        if remaining <= 0:
            return

        if len(schedule) == target_matches:
            if not preliminary_checks(teams, blackouts, schedule, isalternate): # just formality
                print("Preliminary checks failed for schedule:", schedule)
                return

            # print("Evaluating schedule:", schedule)

            score = objective_func(teams, travel_matrix, config,
                                       bids, schedule, isalternate)
            
            # print("Score for this schedule:", score)

            if score >= best_score:
                best_score = score
                best_schedule = schedule.copy()
                best_alternate = isalternate.copy()
            
            if first:
                first-=1
                print("Seed Match: ", schedule[0])
                print("First complete schedule found:", schedule)
                print("First complete schedule found with score:", score)
                print("Timestamp:", datetime.datetime.now())
                if score<0:
                    print("Negative score, killing further DFS.")
                    # kill=True
            remaining -= 1
            return
        
        # Doing this to Optimize Gap_Since_Last_Match_Penalty

        options = [o for o in drr_graph[current] if o not in visited]
        
        # Time since last occurrence for each team in the current schedule:
        # if a team appears in the last match, it gets 1; second last gets 2; etc.
        last_occurrences = {team: inf for team in team_codes}
        for gap, match in enumerate(reversed(schedule), start=1):
            for team in match:
                if last_occurrences[team] == inf:
                    last_occurrences[team] = gap

    
        # priority 
        priority = {}
        for team in team_codes:
            if last_occurrences[team] == inf:
                priority[team] = -1
            elif last_occurrences[team] > 4:
                priority[team] = last_occurrences[team]
            elif last_occurrences[team] < 4:
                priority[team] = 56+(4-last_occurrences[team]) 
            elif last_occurrences[team] == 4:
                priority[team] = 0

        options.sort(
            key=lambda m: (
                min(priority[m[0]], priority[m[1]]),  # primary rule
                max(priority[m[0]], priority[m[1]])   # tie-break
            )
        )

        for next_match in options: 

            """redundant now"""
            if next_match in visited:
                continue
            
            """pre-check BLACKOUTS to prune DFS branches early"""
            next_day = len(schedule) + 1
            if next_day in blackouts[teams[next_match[0]].home_venue]:
                continue
            
            """pre-check (max-min)>4 to prune DFS branches early"""
            appearances[next_match[0]] += 1
            appearances[next_match[1]] += 1
            if max(appearances.values()) - min(appearances.values()) > 4:
                appearances[next_match[0]] -= 1
                appearances[next_match[1]] -= 1
                continue
            
            """pre-check for alternate venues"""

            if alternates[next_match[0]] < alt_limit[next_match[0]] and teams[next_match[0]].alt_venue:
                alternates[next_match[0]] += 1
                isalternate.append(True)
            else:
                isalternate.append(False)

            visited.add(next_match)
            schedule.append(next_match)

            dfs(next_match, schedule, isalternate, visited, appearances, alternates)
            if kill:
                return

            schedule.pop()
            visited.remove(next_match)
            appearances[next_match[0]] -= 1
            appearances[next_match[1]] -= 1
            if isalternate.pop():
                alternates[next_match[0]] -= 1
            


    for start_match in all_matches:
        # fine touch
        first=1

        if 1 in blackouts[teams[start_match[0]].home_venue]:
            continue

        visited = {start_match}
        appearances = {team: 0 for team in team_codes}
        for team_code in start_match:
            appearances[team_code] += 1

        dfs(start_match, [start_match], [False], visited, appearances, empty_alts.copy())
        kill=False

        print("Completed DFS with seed match", start_match)
        print("Best Schedule SO FAR:", best_schedule)
        print("Best Score SO FAR:", best_score)

        # if remaining <= 0: # removed to explore MORE options
        #     break

        remaining = limit # reset for next start so times=56*LIMIT

    print("Best Schedule:", best_schedule)
    print("Best Alternate:", best_alternate)
    print("Best Score:", best_score)
    return best_schedule, best_alternate, best_score

def process(teams : dict[str, Team],
            travel_matrix : dict[str, dict[str, float]],
            config : Config,
            bids : dict[tuple[str, str], dict],
            blackouts : dict[str, list[int]],
            limit: int | None = None):
    return processv5(teams, travel_matrix, config, bids, blackouts, limit)