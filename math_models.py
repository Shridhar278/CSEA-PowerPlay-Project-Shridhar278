import enum

from classes import Team, Config

# alt-venues case APPEND when needed:
# -> in preliminary_checks function / alt_venue_bonus function
# -> in travel_cost function / cummulative_distance_fatigue function
# -> in equity_penalty function

def objective_func(teams : dict[str, Team],
            travel_matrix : dict[str, dict[str, float]],
            config : Config,
            bids : dict[tuple[str, str], dict],
            schedule: list, isalternate: list[bool]):
    objective=0
    objective+=broadcast_revenue(bids, schedule)
    objective+=alt_venue_bonus(teams, config, schedule, isalternate)
    for team in teams.keys():
        objective-=travel_cost(teams, travel_matrix, schedule, teams[team], isalternate)
        objective-=cummulative_distance_fatigue(teams, travel_matrix, config, schedule, teams[team], isalternate)
        objective-=stay_at_location_penalty(config, schedule, teams[team], isalternate)
        objective-=match_density_penalty(config, schedule, teams[team])
        objective-=gap_since_last_match_penalty(config, schedule, teams[team])
    objective-=config.lambda_eq*travel_equity_penalty(teams, travel_matrix, config, schedule, isalternate)
    
    # """debugging MAX-lossers"""
    # print("_______________________________________________________________________________________________________")
    # print("Broadcast revenue:", broadcast_revenue(bids, schedule))
    # print("Alt-venue bonus:", alt_venue_bonus(teams, config, schedule, isalternate))
    
    # net_tc=0
    # net_cdf=0
    # net_stay=0
    # net_md=0
    # net_gap=0

    # for team in teams.keys():
    #     tc=travel_cost(teams, travel_matrix, schedule, teams[team], isalternate)
    #     cdf=cummulative_distance_fatigue(teams, travel_matrix, config, schedule, teams[team], isalternate)
    #     stay=stay_at_location_penalty(config, schedule, teams[team], isalternate)
    #     md=match_density_penalty(config, schedule, teams[team])
    #     gap=gap_since_last_match_penalty(config, schedule, teams[team])
    #     net_tc+=tc
    #     net_cdf+=cdf
    #     net_stay+=stay
    #     net_md+=md
    #     net_gap+=gap

    # print("Net travel cost:", -net_tc)
    # print("Net distance fatigue penalty:", -net_cdf)
    # print("Net stay penalty:", -net_stay)
    # print("Net match density penalty:", -net_md)
    # print("Net gap penalty:", -net_gap)

    # print("Travel equity penalty:", -config.lambda_eq*travel_equity_penalty(teams, travel_matrix, config, schedule, isalternate))
    
    
    return objective


# revenue

def preliminary_checks(teams : dict[str, Team],
            blackouts : dict[str, list[int]], schedule: list, isalternate: list[bool]):
    # alt-venues case APPEND when needed:

    # CHECK BLACKOUTS
    for i, match in enumerate(schedule):
        if (i+1) in blackouts[teams[match[0]].home_venue]:
            print("Blackout violation for match", match, "on day", i+1)
            return False
        
    # CHECK MAX. 4 DIFFERENCE RULE
    def max_min_diff(count):
        values = count.values()
        return max(values) - min(values)

    count = {}
    for team in teams.keys():
        count[team] = 0

    for match in schedule:
        for team in match:
            count[team] += 1
        if max_min_diff(count) > 4:
            print("Max-min difference exceeded after match", match, "with counts", count)
            return False
        
    # CHECK MAX 2 MATCHES IN EACH ALTERNATE VENUE RULE
    alt_limit = {}
    for team in teams.values():
        if team.alt_venue:
            alt_limit[team.code]=2
        else:
            alt_limit[team.code]=0
    # print(schedule)
    # print(isalternate)
    for i, alt in enumerate(isalternate):
        if alt:
            team_code = schedule[i][0] # home team
            alt_limit[team_code] -= 1
            if alt_limit[team_code] < 0:
                print("Alternate venue limit exceeded for team", team_code,
                       "after match", schedule[i])
                return False
    

    # ALL GOOD
    return True

def broadcast_revenue(
            bids : dict[tuple[str, str], dict],
            schedule: list):
    revenue=0
    for i, match in enumerate(schedule):
        if i+1 in bids[match]["preferred_days"]:
            revenue+=bids[match]['alpha_cr']
        elif (i+1)%7<=1:
            revenue+=bids[match]['beta_cr']
        else:
            revenue+=bids[match]['gamma_cr']
    return revenue

def alt_venue_bonus(teams : dict[str, Team],
            config : Config,
             schedule: list, isalternate: list[bool]):
    bonus = 0
    for i, alt in enumerate(isalternate):
        if alt:
            bonus += teams[schedule[i][0]].alt_bonus_cr
    return bonus

# team-wise penalties

def travel_cost(teams : dict[str, Team],
            travel_matrix : dict[str, dict[str, float]],
            schedule: list, team: Team, isalternate: list[bool]):
    # when alt-venues CONSIDERED tweak LOGIC
    cost=0
    first=1
    last_pos=""

    def g(day):
        if (day-1)//7<=5:
            return 1
        elif (day-1)//7==6:
            return 1.25
        else:
            return 1.60
        
    for i, match in enumerate(schedule):
        if team.code in match:
            if first:
                first=0
                if isalternate[i]: # alt-venue case
                    last_pos=teams[match[0]].alt_venue
                else:
                    last_pos=teams[match[0]].home_venue 
            else:
                if isalternate[i]: # alt-venue case
                    current_pos=teams[match[0]].alt_venue
                else:
                    current_pos=teams[match[0]].home_venue 
                cost+=travel_matrix[last_pos][current_pos][1]*g(i+1)
                last_pos=current_pos
    return cost

def cummulative_distance_fatigue(teams : dict[str, Team],
            travel_matrix : dict[str, dict[str, float]],
            config : Config,
            schedule: list, team: Team, isalternate: list[bool]):
    # when alt-venues CONSIDERED tweak LOGIC
    distance=0
    first=1
    last_pos=""

    def penalty(total_dist):
        return config.kappa*max(0, total_dist-config.D0_limit_km)**config.p_exponent

    for i, match in enumerate(schedule):
        if team.code in match:
            if first:
                first=0
                if isalternate[i]: # alt-venue case
                    last_pos=teams[match[0]].alt_venue
                else:
                    last_pos=teams[match[0]].home_venue 
            else:
                if isalternate[i]: # alt-venue case
                    current_pos=teams[match[0]].alt_venue
                else:
                    current_pos=teams[match[0]].home_venue
                distance+=travel_matrix[last_pos][current_pos][0]
                last_pos=current_pos
    
    return penalty(distance)


def stay_at_location_penalty(config : Config,
            schedule: list, team: Team, isalternate: list[bool]):
    def f_stay(x):
        return config.eta*max(0, x-config.x0_limit_days)**config.q_exponent
    
    stay_penalty=0

    for i, match in enumerate(schedule):
        if team.code in match:
            if match[1]==team.code or (isalternate[i] and match[0]==team.code): # alt-venue case
                for j in range(i+1, len(schedule)):
                    if team.code in schedule[j]:
                        stay_penalty+=f_stay(j-i)
                        break

    return stay_penalty

def match_density_penalty(
            config : Config,
            schedule: list, team: Team):
    
    net_delta=0

    def delta(matches):
        if matches==0:
            return config.delta_0_rust_cr
        elif matches==1:
            return 0
        elif matches==2:
            return config.delta_2_tired_cr
        else:
            return config.delta_3_cooked_cr

    matches=[]
    for i, match in enumerate(schedule):
        if team.code in match:
            matches.append(i+1)
    
    for i in range(len(matches)-1):
        count=0
        for j in range(7):
            if matches[i]-j-1 in matches:
                count+=1
        net_delta+=delta(count)

    return net_delta   


def gap_since_last_match_penalty(
            config : Config,
            schedule: list, team: Team):
    first=1
    last_day=0
    total_gap=0

    def psi(gap):
        if gap<=config.tau_star_days:
            return config.a_low_cr*((config.tau_star_days-gap)**2)
        else:
            return config.a_high_cr*((gap-config.tau_star_days)**2)

    for i, match in enumerate(schedule):
        if team.code in match:
            if first:
                first=0
                last_day=i+1
            else:
                total_gap+=psi((i+1-last_day-1))
                last_day=i+1
    return total_gap

# overall penalty

def travel_equity_penalty(teams : dict[str, Team],
            travel_matrix : dict[str, dict[str, float]],
            config : Config,
            schedule: list, isalternate: list[bool]):
    # when alt-venues CONSIDERED tweak LOGIC
    max_D=-1
    min_D=float('inf')

    for team in teams.keys():
        distance=0
        first=1
        last_pos=""

        for i, match in enumerate(schedule):
            if team in match:
                if first:
                    first=0
                    if isalternate[i]: # alt-venue case
                        last_pos=teams[match[0]].alt_venue
                    else:
                        last_pos=teams[match[0]].home_venue 
                else:
                    if isalternate[i]: # alt-venue case
                        current_pos=teams[match[0]].alt_venue
                    else:
                        current_pos=teams[match[0]].home_venue
                    distance+=travel_matrix[last_pos][current_pos][0]
                    last_pos=current_pos

        max_D=max(max_D, distance)
        min_D=min(min_D, distance)
    
    equity=max(0, max_D-min_D-config.delta_0_disparity_km)
    return equity