# match_data_fetcher.py

from __future__ import print_function, division
import requests
import pickle
import datetime
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from collections import namedtuple, OrderedDict
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
        ['gen_data', 'players_data']
        )

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

def get_date_from_match_page_soup(soup, h_club_name):
    date = None

    try:
        text = soup.find('div', {'id': 'VenueDetails'}).get_text()
        date = re.findall('\d\d\/\d\d\/\d\d\d\d', text)[0]
    except:
        tables = soup.find_all('table', {'class': 'RS_Content'})
        i = [i for i, table in enumerate(tables) if h_club_name in table.get_text()][0]
        full_date = soup.find_all('span', {'class':'rName'})[i].get_text().strip()
        date = datetime.datetime.strptime(full_date, "%d %B %Y").strftime("%d/%m/%Y")

    return date


def get_lineup_from_match_page_soup(soup):
    person_lines = soup.find_all('tr', {'class': 'people'})[:18]

    l_persons = []
    r_persons = []

    for p_line in person_lines:
        l_person, r_person = [td.get_text() for td in p_line.find_all('td')][1::5]
        l_persons.append(l_person)
        r_persons.append(r_person)

    return l_persons, r_persons


def get_managers_data(soup):
    managers_line = soup.find_all('tr', {'class': 'people'})[18]
    h_manager_data, a_manager_data = [
            td.get_text() for td in managers_line.find_all('td')[1::3]]
    h_manager_nat = re.findall('\([A-Z]{3}\)', h_manager_data)[0]
    a_manager_nat = re.findall('\([A-Z]{3}\)', a_manager_data)[0]
    h_manager = h_manager_data.replace(h_manager_nat, '').strip()
    a_manager = a_manager_data.replace(a_manager_nat, '').strip()
    return h_manager, h_manager_nat, a_manager, a_manager_nat


def get_match_stat(soup, stat):
    el = [el for el in soup.find('div', {'class': 'matchstat'}).find_all('tr')
            if stat in el.find('td').get_text()][0]
    h = int(el.find('td', {'class': 'lstat r'}).get_text().strip())
    a = int(el.find('td', {'class': 'rstat l'}).get_text().strip())
    return h, a


def get_event_minute(event):
    text = event.get_text()
    if '+' in text:
        minute = sum(map(int, text.split('+')))
    else:
        minute = int(text)
    return minute


def get_match_events(soup):
    people = soup.find_all('tr', {'class': 'people'})
    h_yellow_cards = []
    a_yellow_cards = []
    h_red_cards = []
    a_red_cards = []
    h_subs = []
    a_subs = []
    h_rgoals = []
    a_rgoals = []
    h_scored_pen = []
    a_scored_pen = []

    for people_el in people:
        try:
            h_events, a_events = people_el.find_all('td', {'class': 'l w155 plev'})
            h_yc_events = sorted(map(lambda x: get_event_minute(x),
                h_events.find_all('img', {'alt': 'Yellow Card'})))
            a_yc_events = sorted(map(lambda x: get_event_minute(x),
                a_events.find_all('img', {'alt': 'Yellow Card'})))
            h_rc_events = sorted(map(lambda x: get_event_minute(x),
                h_events.find_all('img', {'alt': 'Red Card'})))
            a_rc_events = sorted(map(lambda x: get_event_minute(x),
                a_events.find_all('img', {'alt': 'Red Card'})))
            h_subs_events = sorted(map(lambda x: get_event_minute(x),
                h_events.find_all('img', {'alt': 'Substitution'})))
            a_subs_events = sorted(map(lambda x: get_event_minute(x),
                a_events.find_all('img', {'alt': 'Substitution'})))
            h_rgoals_events = sorted(map(lambda x: get_event_minute(x),
                h_events.find_all('img', {'src': '/img/icons/event/goals.gif'})))
            a_rgoals_events = sorted(map(lambda x: get_event_minute(x),
                a_events.find_all('img', {'src': '/img/icons/event/goals.gif'})))
            h_scored_pen_events = sorted(map(lambda x: get_event_minute(x),
                h_events.find_all('img', {'src': '/img/icons/event/goals_P.gif'})))
            a_scored_pen_events = sorted(map(lambda x: get_event_minute(x),
                a_events.find_all('img', {'src': '/img/icons/event/goals_P.gif'})))
            h_yellow_cards.extend(h_yc_events)
            a_yellow_cards.extend(a_yc_events)
            h_red_cards.extend(h_rc_events)
            a_red_cards.extend(a_rc_events)
            h_subs.extend(h_subs_events)
            a_subs.extend(a_subs_events)
            h_rgoals.extend(h_rgoals_events)
            a_rgoals.extend(a_rgoals_events)
            h_scored_pen.extend(h_scored_pen_events)
            a_scored_pen.extend(a_scored_pen_events)
        except:
            pass

    dict_to_return = {
            'h_yc': sorted(list(set(h_yellow_cards))),
            'a_yc': sorted(list(set(a_yellow_cards))),
            'h_rc': sorted(list(set(h_red_cards))),
            'a_rc': sorted(list(set(a_red_cards))),
            'h_subs': sorted(list(set(h_subs))),
            'a_subs': sorted(list(set(a_subs))),
            'h_rgoals': sorted(list(set(h_rgoals))),
            'a_rgoals': sorted(list(set(a_rgoals))),
            'h_scored_pen': sorted(list(set(h_scored_pen))),
            'a_scored_pen': sorted(list(set(a_scored_pen)))
            }

    return dict_to_return


def get_match_result(soup, h_club_name, a_club_name):
    tables = soup.find_all('table', {'class': 'RS_Content'})
    table = [table for table in tables if h_club_name in table.get_text()][0]
    trs = table.find_all('tr')
    tr = [tr for tr in trs if h_club_name in tr.get_text()][0]
    result = tr.find('div', {'class':'result clearfix'}).find('a').get_text()
    return result


def get_gen_match_data_from_page_soup(soup):
    h_club_name, a_club_name = (team.get_text() for team in soup.find_all('h2', {'class':'bigTitle'}))
    date = get_date_from_match_page_soup(soup, h_club_name)
    result = get_match_result(soup, h_club_name, a_club_name)
    h_lineup, a_lineup = get_lineup_from_match_page_soup(soup)
    h_manager, h_manager_nat, a_manager, a_manager_nat = get_managers_data(soup)
    h_goals, a_goals = get_match_stat(soup, 'Goals scored')
    try:
        h_poss, a_poss = get_match_stat(soup, 'Possession')
    except:
        h_poss, a_poss = None, None
    h_ant, a_ant = get_match_stat(soup, 'on target')
    h_aft, a_aft = get_match_stat(soup, 'off target')
    try:
        h_blocked, a_blocked = get_match_stat(soup, 'blocked')
    except:
        h_blocked, a_blocked = None, None
    try:
        h_post, a_post = get_match_stat(soup, 'woodwork')
    except:
        h_post, a_post = None, None
    h_corners, a_corners = get_match_stat(soup, 'Corners')
    h_offs, a_offs = get_match_stat(soup, 'Offsides')
    h_yc, a_yc = get_match_stat(soup, 'Yellow')
    h_rc, a_rc = get_match_stat(soup, 'Red')
    h_fc, a_fc = get_match_stat(soup, 'Fouls committed')
    try:
        h_fs, a_fs = get_match_stat(soup, 'Fouls suffered')
    except:
        h_fs, a_fs = None, None
    events_dict = get_match_events(soup)
    h_yc_events = events_dict['h_yc']
    a_yc_events = events_dict['a_yc']
    h_rc_events = events_dict['h_rc']
    a_rc_events = events_dict['a_rc']
    h_subs_events = events_dict['h_subs']
    a_subs_events = events_dict['a_subs']
    h_rgoals_events = events_dict['h_rgoals']
    a_rgoals_events = events_dict['a_rgoals']
    h_scored_pen_events = events_dict['h_scored_pen']
    a_scored_pen_events = events_dict['a_scored_pen']


    gen_match_data = GenMatchData(date, h_club_name, a_club_name,
                     result, h_lineup, a_lineup, h_manager, h_manager_nat, a_manager,
                     a_manager_nat, h_goals, a_goals, h_poss, a_poss, h_ant, a_ant, h_aft, a_aft,
                     h_blocked, a_blocked, h_post, a_post, h_corners, a_corners, h_offs, a_offs, h_yc, a_yc,
                     h_rc, a_rc, h_fc, a_fc, h_fs, a_fs, h_yc_events, a_yc_events, h_rc_events, a_rc_events,
                     h_subs_events, a_subs_events, h_rgoals_events, a_rgoals_events,
                     h_scored_pen_events, a_scored_pen_events)

    return gen_match_data


def get_player_match_data(i, player, team_stats):
    header = team_stats.find('tr')
    stat_names = [th.find('abbr').get('title') if th.find('abbr') is not None
            else th.get_text()
            for th in header.find_all('th')]
    trs = team_stats.find_all('tr')[1:]
    name = player.find('span').get_text()
    try:
        tr = trs[i]
    except:
        tr = ''

    age = 25 #TODO: fix this so that the correct age is fetched

    substituted_minute = sorted(map(lambda x: get_event_minute(x), player.find_all('img',
        {'alt': 'Substitution'})))

    if i <= 10 and substituted_minute:
        minutes = min(90, substituted_minute)
    elif i <= 10 and not substituted_minute:
        minutes = 90
    elif i > 10 and substituted_minute:
        minutes = abs(90 - substituted_minute)
    elif i > 10 and not substituted_minute:
        minutes = 0

    yellow_cards = sorted(map(lambda x: get_event_minute(x), player.find_all('img',
        {'alt': 'Yellow Card'})))
    red_card = sorted(map(lambda x: get_event_minute(x), player.find_all('img',
        {'alt': 'Red Card'})))
    goals = sorted(map(lambda x: get_event_minute(x), player.find_all('img',
        {'alt': 'Goal'})))
    own_goals = sorted(map(lambda x: get_event_minute(x), player.find_all('img',
        {'src': '/img/icons/event/goals_O.gif'})))
    penalties_in = sorted(map(lambda x: get_event_minute(x), player.find_all('img',
        {'src': '/img/icons/event/goals_P.gif'})))
    penalties_mi = sorted(map(lambda x: get_event_minute(x), player.find_all('img',
        {'src': '/img/icons/event/goals_W.gif'})))

    player_stats = [td.get_text() for td in trs[i].find_all('td')]
    player_stats_dict = dict(zip(stat_names, player_stats))

    return PlayerMatchData(name, age, minutes, yellow_cards, red_card, goals, own_goals,
            penalties_in, penalties_mi, player_stats_dict)


def get_players_match_data_soup(soup, url):
    driver.get(url.replace('lineups', 'statistics'))
    sleep(5)
    page_content = driver.execute_script(
            "return document.getElementsByTagName('html')[0].innerHTML")
    stats_soup = BeautifulSoup(page_content, 'html.parser')

    try:
        home_stats, away_stats = stats_soup.find_all('div', {'class': 'statmatch-wrap'})
    except:
        home_stats, away_stats = stats_soup.find_all('table', {'class': 'statmatch sortTable d3-plugin'})

    players_match_data = dict()
    home_players_data = OrderedDict()
    away_players_data = OrderedDict()
    lineups = get_lineup_from_match_page_soup(soup)

    players = soup.find_all('tr', {'class': 'people'})[:18]

    for i, p_line in enumerate(players):
        tables = p_line.find_all('table', {'class':'pname noboder'})
        if len(tables) == 2:
            h_player, a_player = tables
            h_player_match_data = get_player_match_data(i, h_player, home_stats)
            a_player_match_data = get_player_match_data(i, a_player, away_stats)
            home_players_data[h_player_match_data.name] = h_player_match_data
            away_players_data[a_player_match_data.name] = a_player_match_data
        elif len(tables) == 1:
            if lineups[0][i] and not lineups[1][i]:
                h_player = tables[0]
                h_player_match_data = get_player_match_data(i, h_player, home_stats)
                home_players_data[h_player_match_data.name] = h_player_match_data
            elif lineups[1][i] and not lineups[0][i]:
                a_player = tables[0]
                a_player_match_data = get_player_match_data(i, a_player, away_stats)
                away_players_data[a_player_match_data.name] = a_player_match_data
        else:
            pass

    players_match_data['home'] = home_players_data
    players_match_data['away'] = away_players_data
    return players_match_data


def get_match_data_for_season_round_match(s_data, r_name, m_code):
    url = "https://www.uefa.com/uefachampionsleague/season={}/matches/"\
          "round={}/match={}/postmatch/lineups/index.html".format(
                  s_data.season_code,
                  s_data.rounds_data[r_name].round_code,
                  m_code)
    driver.get(url)
    sleep(5)
    page_content = driver.execute_script(
            "return document.getElementsByTagName('html')[0].innerHTML")
    soup = BeautifulSoup(page_content, 'html.parser')

    gen_match_data = get_gen_match_data_from_page_soup(soup)
    players_match_data = get_players_match_data_soup(soup, url)

    match_data = MatchData(gen_match_data, players_match_data)

    return match_data


def get_matches_data_for_season_round(s_data, r_name):
    r_m_stats = []

    for m_code in s_data.rounds_data[r_name].match_codes:
        print("Getting data for {} phase of {} season, match {}".format(r_name,
            s_data.season_code, m_code))
        m_stats = get_match_data_for_season_round_match(s_data, r_name, m_code)
        r_m_stats.append(m_stats)

    return r_m_stats


def get_matches_data_for_season(s_data):
    s_r_m_stats = []

    for r_name in s_data.rounds_data.keys():
        r_stats = get_matches_data_for_season_round(s_data, r_name)
        s_r_m_stats.append(r_stats)

    return s_r_m_stats


def main():
    codes_data = pickle.load(open('../data/codes_data.p', 'rb'))

    for s_end_year in [2016]:
        season_stats = get_matches_data_for_season(codes_data[s_end_year])
        pickle.dump(season_stats, open('../data/season_stats/season_stats_{}.p'.format(s_end_year), 'wb'))



if __name__ == '__main__':
    main()
