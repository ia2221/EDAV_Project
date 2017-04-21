from __future__ import print_function, division
import pickle
import numpy as np
import pandas as pd
from functools import reduce
from collections import namedtuple, OrderedDict, defaultdict

SeasonData = namedtuple(
                'SeasonData',
                ['season_code', 'rounds_data'])

RoundData = namedtuple(
                'RoundData',
                ['round_code', 'match_codes', 'matches_data'])

MatchData = namedtuple(
                'MatchData',
                ['gen_data', 'players_data'])

GenMatchData = namedtuple(
        'GenMatchData',
        ['date', 'h_club_name', 'a_club_name',
         'result', 'h_lineup', 'a_lineup', 'h_manager', 'h_manager_nat', 'a_manager',
         'a_manager_nat', 'h_goals', 'a_goals', 'h_poss', 'a_poss', 'h_ant', 'a_ant', 'h_aft', 'a_aft',
         'h_blocked', 'a_blocked', 'h_post', 'a_post', 'h_corners', 'a_corners', 'h_offs', 'a_offs', 'h_yc', 'a_yc',
         'h_rc', 'a_rc', 'h_fc', 'a_fc', 'h_fs', 'a_fs', 'h_yc_events', 'a_yc_events', 'h_rc_events', 'a_rc_events',
         'h_subs_events', 'a_subs_events', 'h_rgoals_events', 'a_rgoals_events',
         'h_scored_pen_events', 'a_scored_pen_events'])

PlayerMatchData = namedtuple(
        'PlayerMatchData',
        ['name', 'age', 'minutes', 'yellow_cards', 'red_card', 'goals', 'own_goals',
         'penalties_in', 'penalties_mi', 'match_stats_dict'])

DetailedMatchData = namedtuple(
        'DetailedMatchData',
        ['gen_data', 'players_data', 'team_skills'])

DetailedPlayerMatchData = namedtuple(
        'DetailedPlayerMatchData',
        ['name', 'age', 'country_of_birth', 'formation', 'minutes', 'yellow_cards', 'red_card', 'goals', 'own_goals',
         'penalties_in', 'penalties_mi', 'match_stats_dict'])

def get_set_of_teams_in_round(season_stats, round_name):
    r_teams = set()

    round_names = ['Group stage', 'Round of 16', 'Quarter-Finals', 'Semi-Finals', 'Final']
    i = round_names.index(round_name)

    n = len(season_stats[i])
    for j in range(n):
        match_data = season_stats[i][j]
        r_teams.add(match_data.gen_data.h_club_name)
        r_teams.add(match_data.gen_data.a_club_name)

    return r_teams


def get_set_of_teams_eliminated_in_gs(season_stats):
    gs_teams = get_set_of_teams_in_round(season_stats, 'Group stage')
    r16_teams = get_set_of_teams_in_round(season_stats, 'Round of 16')

    return gs_teams - r16_teams


def main():
    teams_skills = defaultdict(list)
    teams_skills_nNone = defaultdict(list)

    for s_end_year in range(2007, 2016):
        season_stats = pickle.load(open('../data/season_stats/c_season_stats_{}.p'.format(s_end_year),'rb'))

        ko_gs = get_set_of_teams_eliminated_in_gs(season_stats)
        i = ['Group stage', 'Round of 16', 'Quarter-Finals', 'Semi-Finals', 'Final'].index('Group stage')
        for j in range(len(season_stats[i])):
            match_data = season_stats[i][j]
            for team in ko_gs.intersection({match_data.gen_data.h_club_name, match_data.gen_data.a_club_name}):
                teams_skills['ko'].append(match_data.team_skills[team])

        sf_te = get_set_of_teams_in_round(season_stats, 'Semi-Finals')
        i = ['Group stage', 'Round of 16', 'Quarter-Finals', 'Semi-Finals', 'Final'].index('Semi-Finals')
        for j in range(len(season_stats[i])):
            match_data = season_stats[i][j]
            for team in sf_te.intersection({match_data.gen_data.h_club_name, match_data.gen_data.a_club_name}):
                teams_skills['sf'].append(match_data.team_skills[team])

        ko_avg = OrderedDict()
        teams_skills_nNone['ko'] = [team for team in teams_skills['ko'] if None not in team.values()]
        for skill in ['Overall', 'Attack', 'Midfield', 'Defense']:
            ko_avg[skill] = np.array((list(map(lambda x: x[skill], teams_skills_nNone['ko'])))).mean()


        sf_avg = OrderedDict()
        teams_skills_nNone['sf'] = [team for team in teams_skills['sf'] if None not in team.values()]
        for skill in ['Overall', 'Attack', 'Midfield', 'Defense']:
            sf_avg[skill] = np.array((list(map(lambda x: x[skill], teams_skills['sf'])))).mean()

    pickle.dump(ko_avg, open('../data/csvs_for_nb/ko_avg.p', 'wb'))
    pickle.dump(sf_avg, open('../data/csvs_for_nb/sf_avg.p', 'wb'))
    pickle.dump(teams_skills, open('../data/csvs_for_nb/teams_skills.p', 'wb'))
    pickle.dump(teams_skills_nNone, open('../data/csvs_for_nb/teams_skill_nNones.p', 'wb'))


if __name__ == '__main__':
    main()
