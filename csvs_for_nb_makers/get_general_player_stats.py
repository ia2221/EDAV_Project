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
    mapped_countries = {
        'Joué-lès-Tours,[1] France': 'France',
        'Berlin. Germany': 'Germany',
        'Cameroon[2]': 'Cameroon',
        'Burkina Faso[2]': 'Burkina Faso',
        'Spain[1]': 'Spain',
        "Cote d'Ivoire": 'Ivory Coast',
        'Soviet Union now Ukraine': 'Soviet Union',
        'Argentina [1]': 'Argentina',
        'England[1]': 'England',
        'Italy[3]': 'Italy',
        'West Germany[3]': 'West Germany',
        "Côte d'Ivoire[1]": "Ivory Coast",
        'Truskolasy,[1] Poland': 'Poland',
        'Suriname[1]': 'Suriname',
        'Soviet Union[1]': 'Soviet Union',
        'SFR Yugoslavia[1]': 'Yugoslavia',
        'Belgium[2]': 'Belgium',
        'Guaratinguetá,[1] Brazil': 'Brazil',
        'Belgium[1]': 'Belgium',
        'Italy[1]': 'Italy',
        'Portugal[2]': 'Portugal',
        'Brazil[1]': 'Brazil',
        'Bělkovice-Lašťany Czechoslovakia': 'Czechoslovakia',
        'Molde,[1] Norway': 'Norway',
        'Lille,[2] France': 'France',
        'SFR Yugoslavia\n(now Macedonia)': 'Yugoslavia',
        'Pizarra,[1] Spain': 'Spain',
        'Zlín,[1] Czechoslovakia': 'Czechoslovakia',
        'Czechoslovakia[1]': 'Czechoslovakia',
        'Rijeka,[2] Croatia': 'Croatia',
        'Mexico[2][3]': 'Mexico',
        'Munich,[1] Germany': 'Germany',
        'Peru[2]': 'Peru',
        'Buenos Aires,[3] Argentina': 'Argentina',
        'Chile[2][3]': 'Chile',
        'Turkey[1]': 'Turkey',
        'Scotland[1]': 'Scotland',
        'Ghana[2]': 'Ghana',
        'Rome,[1] Italy': 'Italy',
        'Venezuela.': 'Venezuela',
        'Soviet Union\n(now Latvia)': 'Soviet Union',
        'Bulgaria[2]': 'Bulgaria',
        'Bánovce nad Bebravou,\nCzechoslovakia': 'Czechoslovakia',
        'Belarussian SSR': 'Belarusian SSR',
        "Côte d'Ivoire": "Ivory Coast",
        'Greece[2]': 'Greece',
        'Denmark[3]': 'Denmark',
        'Sweden[1]': 'Sweden',
        'Argentina[2]': 'Argentina',
        'Sierre,[1] Switzerland': 'Switzerland',
        'Carapicuíba,[1] Brazil': 'Brazil',
        'France[1]': 'France',
        'West Germany[2]': 'West Germany',
        'Hokksund,[1] Norway': 'Norway',
        'West Germany[1]': 'West Germany',
        'Netherlands[3]': 'Netherlands',
        'Norway[2][3]': 'Norway',
        'Netherlands[1]': 'Netherlands',
        'Scotland[2]': 'Scotland',
        'Born at sea[1]': 'Born at sea',
        'West Berlin': 'West Germany',
        'Austria[2]': 'Austria',
        'Romania[1]': 'Romania',
        'Northern Ireland[2]': 'Northern Ireland',
        'Cape Verde[1]': 'Cape Verde',
        'Germany[2]': 'Germany',
        'Piatra-Olt,[1] Romania': 'Romania',
        'Ivory Coast[1]': 'Ivory Coast',
        'Soviet Union (now Russia)': 'Soviet Union',
        'England[3]': 'England',
        'Brazil[2]': 'Brazil',
        'RSFSR,\nSoviet Union[1]': 'Soviet Union',
        'FR Yugoslavia': 'Yugoslavia',
        'Germany[1]': 'Germany',
        'England[2]': 'England',
        'SFR Yugoslavia': 'Yugoslavia'
    }

    match_stats = list()

    for s_end_year in range(2013, 2017):
        season_stats = pickle.load(open('../data/season_stats/pd_season_stats_{}.p'.format(s_end_year),'rb'))
        for i, _ in enumerate(['Group stage', 'Round of 16', 'Quarter-Finals', 'Semi-Finals', 'Final']):
            n = len(season_stats[i])
            for j in range(n):
                match_data = season_stats[i][j]

                for h_player in match_data.players_data['home'].keys():
                    date = match_data.gen_data.date
                    club = match_data.gen_data.h_club_name
                    age = match_data.players_data['home'][h_player].age

                    pob = match_data.players_data['home'][h_player].country_of_birth
                    if pob in mapped_countries.keys():
                        pob = mapped_countries[pob]

                    formation = match_data.players_data['home'][h_player].formation
                    player_data = [date, club, h_player, age, pob, formation]
                    match_stats.append(player_data)

                for a_player in match_data.players_data['away'].keys():
                    date = match_data.gen_data.date
                    club = match_data.gen_data.a_club_name
                    age = match_data.players_data['away'][a_player].age

                    pob = match_data.players_data['away'][a_player].country_of_birth
                    if pob in mapped_countries.keys():
                        pob = mapped_countries[pob]

                    formation = match_data.players_data['away'][a_player].formation
                    player_data = [date, club, a_player, age, pob, formation]
                    match_stats.append(player_data)

    p_gen_stats_df = pd.DataFrame(match_stats, columns=['date', 'club', 'name', 'age', 'cob', 'formation'])
    p_gen_stats_df.to_csv('../data/csvs_for_nb/p_gen_stats_2013.csv')


if __name__ == '__main__':
    main()
