from __future__ import print_function, division
import pickle
import pandas as pd
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

def main():
    players_stats = defaultdict(lambda : defaultdict(int))

    for s_end_year in range(2007, 2016):
        season_stats = pickle.load(open('../data/season_stats/c_season_stats_{}.p'.format(s_end_year),'rb'))
        for i, _ in enumerate(['Group stage', 'Round of 16', 'Quarter-Finals', 'Semi-Finals', 'Final']):
            n = len(season_stats[i])
            for j in range(n):
                match_data = season_stats[i][j]

                for h_player in match_data.players_data['home'].keys():
                    current_p_data = match_data.players_data['home'][h_player]
                    if current_p_data.minutes > 0:
                        players_stats[h_player]['apps'] += 1
                        players_stats[h_player]['minutes'] += current_p_data.minutes
                        players_stats[h_player]['yellow_cards'] += len(current_p_data.yellow_cards)
                        players_stats[h_player]['red_cards'] += len(current_p_data.red_card)
                        players_stats[h_player]['goals'] += len(current_p_data.goals)
                        players_stats[h_player]['own_goals'] += len(current_p_data.own_goals)
                        players_stats[h_player]['penalties_in'] += len(current_p_data.penalties_in)
                        players_stats[h_player]['penalties_mi'] += len(current_p_data.penalties_mi)
                        players_stats[h_player]['assists'] += int(current_p_data.match_stats_dict['Assists'])
                        players_stats[h_player]['fouls_commited'] += int(current_p_data.match_stats_dict['Fouls committed'])
                        players_stats[h_player]['fouls_suffered'] += int(current_p_data.match_stats_dict['Fouls suffered'])
                        players_stats[h_player]['offsides'] += int(current_p_data.match_stats_dict['Offsides'])
                    else:
                        pass

                for a_player in match_data.players_data['away'].keys():
                    current_p_data = match_data.players_data['away'][a_player]
                    if current_p_data.minutes > 0:
                        players_stats[a_player]['apps'] += 1
                        players_stats[a_player]['minutes'] += current_p_data.minutes
                        players_stats[a_player]['yellow_cards'] += len(current_p_data.yellow_cards)
                        players_stats[a_player]['red_cards'] += len(current_p_data.red_card)
                        players_stats[a_player]['goals'] += len(current_p_data.goals)
                        players_stats[a_player]['own_goals'] += len(current_p_data.own_goals)
                        players_stats[a_player]['penalties_in'] += len(current_p_data.penalties_in)
                        players_stats[a_player]['penalties_mi'] += len(current_p_data.penalties_mi)
                        players_stats[a_player]['assists'] += int(current_p_data.match_stats_dict['Assists'])
                        players_stats[a_player]['fouls_commited'] += int(current_p_data.match_stats_dict['Fouls committed'])
                        players_stats[a_player]['fouls_suffered'] += int(current_p_data.match_stats_dict['Fouls suffered'])
                        players_stats[a_player]['offsides'] += int(current_p_data.match_stats_dict['Offsides'])
                    else:
                        pass

    p_stats_df = pd.DataFrame(players_stats).transpose()
    p_stats_df.to_csv('../data/csvs_for_nb/p_stats_df.csv')


if __name__ == '__main__':
    main()
