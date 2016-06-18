import requests
import datetime

header = {'X-TBA-App-Id' : 'BrianMaher:BrianScoutLib:0'}

round_to = 2

current_year = int(datetime.date.today().__str__()[:4])

#EVENT FUCNTIONS

#returns the URL of an event
def get_event_url(event_key):
	return 'http://www.thebluealliance.com/api/v2/event/' + event_key

#RETURNS LIST OF ALL EVENTS
def get_events(year):
	url = 'http://www.thebluealliance.com/api/v2/events/' + str(year)
	events_request = requests.get(url, params = header)
	return events_request.json()

#RETURNS EVENT INFO
def get_event_info(event_key):
	event_url = get_event_url(event_key)
	event_request = requests.get(event_url, params = header)
	return event_request.json()

#RETURNS TEAMS AT AN EVENT
def get_event_teams(event_key):
	teams_url = get_event_url(event_key) + '/teams'
	teams_request = requests.get(teams_url, params = header)
	return teams_request.json()

#RETURNS TEAMS AT AN EVENT IN LIST FORM
def get_event_teams_list(event_key):
	return sorted([int(team[1]) for team in get_event_rankings(event_key)[1:]])

#RETURNS MATCH RESULTS
def get_event_matches(event_key):
	matches_url = get_event_url(event_key) + '/matches'
	matches_request = requests.get(matches_url, params = header)
	return matches_request.json()

#RETURNS OPR, DPR, CCWM
def get_event_stats(event_key):
	stats_url = get_event_url(event_key) + '/stats'
	stats_request = requests.get(stats_url, params = header)
	return stats_request.json()

#RETURNS EVENT RANKINGS
def get_event_rankings(event_key):
	rankings_url = get_event_url(event_key) + '/rankings'
	rankings_request = requests.get(rankings_url, params = header)
	return rankings_request.json()

#RETURNS AWARDS GIVEN AT EVENT
def get_event_awards(event_key):
	awards_url = get_event_url(event_key) + '/awards'
	awards_request = requests.get(awards_url, params = header)
	return awards_request.json()

#RETURNS ALL THE INFO FROM AN EVENT
def get_event(event_key):
	event = {}
	event['info'] = get_event_info(event_key)
	event['teams'] = get_event_teams(event_key)
	event['matches'] = get_event_matches(event_key)
	event['stats'] = get_event_stats(event_key)
	event['rankings'] = get_event_rankings(event_key)
	event['awards'] = get_event_awards(event_key)
	return event

#TEAM FUCNTIONS

def team_url(team):
	return "http://www.thebluealliance.com/api/v2/team/frc" + str(team)

def team_event_url(team, event_key):
	return team_url(team) + "/event/" + event_key

#Get basic info about the team
def get_team(team):
#	team_url = team_url(team)
	team_url = "http://www.thebluealliance.com/api/v2/team/frc" + str(team)
	team_request = requests.get(team_url, params = header)
	return team_request.json()

#Get a list of a teams' events
def get_team_events(team, year):
	team_events_url = team_url(team) + "/" + str(year) + "/events"
	team_events_request = requests.get(team_events_url, params = header)
	return team_events_request.json()

def get_team_event_awards(team, event_key):
	team_event_awards_url = team_event_url(team, event_key) + "/awards"
	team_event_awards_request = requests.get(team_event_awards_url, params = header)
	return team_event_awards_request.json()

def get_team_event_matches(team, event_key):
	team_event_matches_url = team_event_url(team, event_key) + "/matches"
	team_event_matches_request = requests.get(team_event_matches_url, params = header)
	return team_event_matches_request.json()

#score types:
#0 is rank
#1 is team number
#2 is QS
#3 is assist
#4 is auton
#5 is truss and catch
#6 is teleop
#9 is matches played
def get_event_rank_by(event_key, score_type):
	if type(score_type) == int:
		teams_rankings = get_event_rankings(event_key)
		key = [teams_rankings[0][0], teams_rankings[0][1], teams_rankings[0][score_type]]
		teams_rankings.pop(0)

		scores = []
		for team in teams_rankings:
			scores.append(float(team[score_type]))

		scores.sort()
		scores.reverse()
		for score in scores:
			score = str(score)

		rank = 1
		ranked_teams = []

		for score in scores:
			with_score = []
			for team in teams_rankings:
				if float(team[score_type]) == float(score):
					score_per_match = str(round(float(team[score_type]) / float(team[9]), round_to))
					ranked_teams.append([str(rank), team[1], score_per_match])
					with_score.append(team)
			for team in with_score:
				teams_rankings.remove(team)	
			rank += 1

		ranked_teams.insert(0, key)
		return ranked_teams

def get_team_event_rank_by(team, event_key, score_type):
	rankings = get_event_rank_by(event_key, score_type)
	for team_rank in rankings:
		if str(team) == team_rank[1]:
			return team_rank


def is_qualifier(match):
	if match['comp_level'] == 'qm':
		return True
	else:
		return False

def get_alliance(team, match):
	team_code = "frc" + str(team)
	for color in ["red", "blue"]:
		for team in match['alliances'][color]['teams']:
			if team == team_code:
				return color

def result(team, match):
	winner = ""
	loser = ""
	if match['alliances']['blue']['score'] > match['alliances']['red']['score']:
		winner = "blue"
		loser = "red"
	elif match['alliances']['blue']['score'] < match['alliances']['red']['score']:
		winner = "red"
		loser = "blue"
	if get_alliance(team, match) == winner:
		return "W"
	elif get_alliance(team, match) == loser:
		return "L"
	else:
		return "T"

#kind is either "all", "elim", or "qual"
def get_team_event_record(team, event_key, kind):
	matches = get_team_event_matches(team, event_key)
	win = 0
	loss = 0
	tie = 0
	if kind == "qual" or kind == "all":
		for match in matches:
			if match['comp_level'] == 'qm':
				if result(team, match) == "W":
					win += 1
				elif result(team, match) == "L":
					loss += 1
				else:
					tie += 1
	if kind == "elim" or kind == "all":
		for match in matches:
			if match['comp_level'] != 'qm':
				if result(team, match) == "W":
					win += 1
				elif result(team, match) == "L":
					loss += 1
				else:
					tie += 1
	return [win, loss, tie]

def get_team_event_rank(team, event_key):
	rankings = get_event_rankings(event_key)
	for ranking in rankings:
		if str(team) == ranking[1]:
			return ranking[0]

#entry 1 is OPR, 2 is CCWM, 3 is DPR
def get_team_event_stats(team, event_key):
	stats = get_event_stats(event_key)
	team_stats = {}
	team_string = str(team)
	for team in stats['oprs']:
		if team == team_string:
			team_stats['OPR'] = round(stats['oprs'][team], round_to)
			break
	for team in stats['ccwms']:
		if team == team_string:
			team_stats['CCWM'] = round(stats['ccwms'][team], round_to)
			break
	for team in stats['dprs']:
		if team == team_string:
			team_stats['DPR'] = round(stats['dprs'][team], round_to)
			break
	return team_stats

def get_team_nickname(team):
	url = team_url(team)
	team_request = requests.get(url, params = header)
	return team_request.json()['nickname']

def get_event_number_of_teams(event_key):
	return len(get_event_rankings(event_key)) - 1

#DISTRICT THINGS yay thanks thebluealliance :D

def get_district_url(district, year):
	return "http://www.thebluealliance.com/api/v2/district/" + district + "/" + str(year)

def get_event_district_points(event_key):
	url = get_event_url(event_key) + "/district_points"
	points_request = requests.get(url, params = header)
	return points_request.json()

def get_districts(year):
	url = get_district_url("", 0)[::-1][3:][::-1] + "s/" + str(year)
	districts_request = requests.get(url, params = header)
	return districts_request.json()

def get_district_events(district, year):
	url = get_district_url(district, year) + "/events"
	district_events_request = requests.get(url, params = header)
	return district_events_request.json()

def get_district_rankings(district, year):
	url = get_district_url(district, year) + "/rankings"
	district_rankings_request = requests.get(url, params = header)
	return district_rankings_request.json()