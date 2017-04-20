from __future__ import print_function, division
import requests
import pickle
import datetime
import re
import csv
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta
from selenium import webdriver
from collections import namedtuple, OrderedDict, defaultdict
from time import sleep

driver = webdriver.PhantomJS()

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

def get_updated_teams_dict(teams_dict):
    csv_reader = csv.reader(open('../data/teams/manual_id_mapping.csv', 'r'))

    for row in csv_reader:
        team, team_id = row
        teams_dict[team] = int(team_id) if team_id != '-999' else None

    return teams_dict


def yearsago(years, from_date=None):
    'credit: http://stackoverflow.com/questions/765797/python-timedelta-in-years'
    if from_date is None:
        from_date = datetime.datetime.now()
    return from_date - relativedelta(years=years)


def num_years(begin, end=None):
    'credit: http://stackoverflow.com/questions/765797/python-timedelta-in-years'
    if end is None:
        end = datetime.datetime.now()
    num_years = int((end - begin).days / 365.25)
    if begin > yearsago(num_years, end):
        return num_years - 1
    else:
        return num_years


def get_age_at_date(date_str, dob_str):
    date = datetime.datetime.strptime(date_str, '%d/%m/%Y')
    dob = datetime.datetime.strptime(dob_str, '%Y-%m-%d')
    return num_years(dob, date)


def get_player_wiki_soup(clean_p_name, team_name):
    if team_name == 'Man. United':
        team_name = 'Manchester United'
    elif team_name == 'Man. City':
        team_name = 'Manchester City'

    url = 'https://en.wikipedia.org/wiki/{}'.format(clean_p_name)
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    infobox = soup.find('table', {'class':'infobox vcard'})

    if infobox is not None and team_name in infobox.get_text():
        pass
    else:
        uls = soup.find_all('ul')
        links = list()
        for ul in uls:
            for li in ul.find_all('li'):
                if li.find('a') is not None:
                    links.append(li.find('a').get('href'))

        try:
            links.remove(None)
        except:
            pass

        links = [link for link in links if not (':' in link or 'Main_Page' in link or '?' in link or '//' in link or '#' in link or link == '/wiki/{}'.format(clean_p_name))]

        # consider the disambiguation
        url = 'https://en.wikipedia.org/wiki/{}_(disambiguation)'.format(clean_p_name)
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')

        variety_list = [li.find('a').get('href') for li in soup.find('ul').find_all('li') if 'variety of association football players' in li.get_text()]
        if len(variety_list) > 0:
            url = 'https://en.wikipedia.org{}'.format(variety_list[0])
            r = requests.get(url)
            soup = BeautifulSoup(r.text, 'html.parser')
            variety_links = [li.find('a').get('href') for li in soup.find_all('li') if 'born' in li.get_text()]
            links = variety_links + links
        else:
            other_links = [li.find('a').get('href') for li in soup.find('ul').find_all('li') if 'football' in li.get_text() and not '#' in li.get_text()]
            links = other_links + links

        # check all links
        for link in links:
            url = 'https://en.wikipedia.org{}'.format(link)
            r = requests.get(url)
            soup = BeautifulSoup(r.text, 'html.parser')

            infobox = soup.find('table', {'class':'infobox vcard'})

            if infobox is not None and team_name in infobox.get_text():
                break
        else:
            soup = None

    return soup


def get_player_age_cob_dob(player_name, team_name, date):
    clean_p_name = '_'.join(player_name.replace(' (GK)', '').replace(' (C)', '').split())

    try:
        soup = get_player_wiki_soup(clean_p_name, team_name)
        infobox = soup.find('table', {'class':'infobox vcard'})
        dob_str = [tr.find('td').find('span', {'class':'bday'}).get_text() for tr in infobox.find_all('tr') if 'Date of birth' in tr.get_text()][0]
        cob_str = [tr.find('td').get_text().split(', ')[-1] for tr in infobox.find_all('tr') if 'Place of birth' in tr.get_text()][0]
        try:
            trs = infobox.find_all('tr')
            form_idx = [i+1 for i, tr in enumerate(trs) if 'Youth career' in tr.get_text()][0]
            form_str = trs[form_idx].find('a').get_text()
        except:
            form_str = None

        age = get_age_at_date(date, dob_str)

    except:
        print("Failed to get age and cob for player {} from team {} for game on {}".format(clean_p_name, team_name, date))
        with open('../data/players/manual_age_cob_players.csv', 'a') as f:
            f.write("{},{},{}\n".format(clean_p_name, team_name, date))
        age = None
        cob_str = None
        dob_str = None
        form_str = None

    return age, cob_str, dob_str, form_str


def get_all_players_data(match_data, already_seen):
    gen_data = match_data.gen_data
    d_players_data = OrderedDict()
    d_players_data['home'] = OrderedDict()
    d_players_data['away'] = OrderedDict()

    h_players = gen_data.h_lineup
    while '' in h_players:
        h_players.remove('')

    a_players = gen_data.a_lineup
    while '' in a_players:
        a_players.remove('')


    for player_name in h_players:
        name = player_name.replace(' (GK)', '').replace(' (C)', '')

        player_team_key = "{}_{}".format('_'.join(name.split()), gen_data.h_club_name)
        if player_team_key in already_seen:
            if already_seen[player_team_key]['dob'] is not None:
                age = get_age_at_date(match_data.gen_data.date, already_seen[player_team_key]['dob'])
            else:
                age = None

            cob = already_seen[player_team_key]['cob']
            form_str = already_seen[player_team_key]['form']
        else:
            age, cob, dob, form_str = get_player_age_cob_dob(player_name, gen_data.h_club_name, gen_data.date)
            already_seen[player_team_key]['dob'] = dob
            already_seen[player_team_key]['cob'] = cob
            already_seen[player_team_key]['form'] = form_str

        minutes = match_data.players_data['home'][name].minutes
        yellow_cards = match_data.players_data['home'][name].yellow_cards
        red_card = match_data.players_data['home'][name].red_card
        goals = match_data.players_data['home'][name].goals
        own_goals = match_data.players_data['home'][name].own_goals
        penalties_in = match_data.players_data['home'][name].penalties_in
        penalties_mi = match_data.players_data['home'][name].penalties_mi
        match_stats_dict = match_data.players_data['home'][name].match_stats_dict
        d_player_data = DetailedPlayerMatchData(name, age, cob, form_str, minutes, yellow_cards, red_card,
                        goals, own_goals, penalties_in, penalties_mi, match_stats_dict)
        d_players_data['home'][name] = d_player_data

    for player_name in a_players:
        name = player_name.replace(' (GK)', '').replace(' (C)', '')

        player_team_key = "{}_{}".format('_'.join(name.split()), gen_data.a_club_name)
        if player_team_key in already_seen:
            if already_seen[player_team_key]['dob'] is not None:
                age = get_age_at_date(match_data.gen_data.date, already_seen[player_team_key]['dob'])
            else:
                age = None

            cob = already_seen[player_team_key]['cob']
            form_str = already_seen[player_team_key]['form']
        else:
            age, cob, dob, form_str = get_player_age_cob_dob(player_name, gen_data.a_club_name, gen_data.date)
            already_seen[player_team_key]['dob'] = dob
            already_seen[player_team_key]['cob'] = cob
            already_seen[player_team_key]['form'] = form_str

        minutes = match_data.players_data['away'][name].minutes
        yellow_cards = match_data.players_data['away'][name].yellow_cards
        red_card = match_data.players_data['away'][name].red_card
        goals = match_data.players_data['away'][name].goals
        own_goals = match_data.players_data['away'][name].own_goals
        penalties_in = match_data.players_data['away'][name].penalties_in
        penalties_mi = match_data.players_data['away'][name].penalties_mi
        match_stats_dict = match_data.players_data['away'][name].match_stats_dict
        d_player_data = DetailedPlayerMatchData(name, age, cob, form_str, minutes, yellow_cards, red_card,
                        goals, own_goals, penalties_in, penalties_mi, match_stats_dict)
        d_players_data['away'][name] = d_player_data

    return d_players_data, already_seen


def main():
    teams_dict = get_updated_teams_dict(pickle.load(open('../data/teams/teams_dict.p', 'rb')))

    already_seen = defaultdict(defaultdict)

    for s_end_year in range(2007, 2016):
        print('Fetching data for season ending in {}'.format(s_end_year))
        season_stats = pickle.load(open('../data/season_stats/season_stats_{}.p'.format(s_end_year),'rb'))
        for i in range(5):
            n = len(season_stats[i])
            for j in range(n):
                print('\t- Fetching data for game {}/{} of stage {}/{} of season ending in {}'.format(j+1, n, i+1, 5, s_end_year))
                gen_data = season_stats[i][j].gen_data
                d_players_data, already_seen = get_all_players_data(season_stats[i][j], already_seen)
                season_stats[i][j] = MatchData(gen_data, d_players_data)

    pickle.dump(season_stats, open('../data/season_stats/pd_season_stats_{}.p'.format(s_end_year), 'wb'))
    pickle.dump(already_seen, open('../data/season_stats/pd_already_seen_{}.p'.format(s_end_year), 'wb'))


if __name__ == '__main__':
    main()
