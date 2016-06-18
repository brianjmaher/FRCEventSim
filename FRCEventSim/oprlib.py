import bscout
import numpy
import csv

def get_teams_matrix(event_key="", event_rankings=[]):
	if len(event_rankings) == 0:
		event_rankings = bscout.get_event_rankings(event_key)
	teams = sorted([int(ranking[1]) for ranking in event_rankings[1:]])
	return list_to_column(teams)

def get_partner_matrix(event_key="", event_matches=[], teams_matrix=[]):
	pairings_dict = {}
	if len(teams_matrix) == 0:
		teams_matrix = get_teams_matrix(event_key)
	if len(event_matches) == 0:
		event_matches = bscout.get_event_matches(event_key)

	initialize_pairings(pairings_dict, teams_matrix)

	for match in event_matches:
		if match['comp_level'] == "qm":
			alliances = match['alliances']['red'], match['alliances']['blue']
			for alliance in alliances:
				if alliance['score'] > -1:
					add_pairing(pairings_dict, alliance['teams'])

	teams_list = column_to_list(teams_matrix)
	partner_matrix = numpy.zeros((len(teams_list), len(teams_list)))

	teams_range = range(len(teams_list))
	for i in teams_range:
		for j in teams_range:
			partner_matrix[i][j] = pairings_dict[teams_list[i]][teams_list[j]]
	return partner_matrix

def get_opp_matrix(event_key="", event_matches=[], teams_matrix=[]):
	pairings_dict = {}
	if len(teams_matrix) == 0:
		teams_matrix = get_teams_matrix(event_key)
	if len(event_matches) == 0:
		event_matches = bscout.get_event_matches(event_key)

	initialize_pairings(pairings_dict, teams_matrix)

	for match in event_matches:
		if match['comp_level'] == "qm":
			alliances = match['alliances']['red'], match['alliances']['blue']
			colors = ("red", "blue")
			for i in (0, 1):
				if alliances[i]['score'] > -1:
					add_opponent(pairings_dict, alliances[i]['teams'], alliances[1-i]['teams'])

	teams_list = column_to_list(teams_matrix)
	partner_matrix = numpy.zeros((len(teams_list), len(teams_list)))

	teams_range = range(len(teams_list))
	for i in teams_range:
		for j in teams_range:
			partner_matrix[i][j] = pairings_dict[teams_list[i]][teams_list[j]]
	return partner_matrix

def get_marg_partner_matrix(event_key="", event_matches=[], teams_matrix=[]):
	if len(event_matches) == 0:
		event_matches=bscout.get_event_matches(event_key)
	if len(teams_matrix) == 0:
		get_teams_matrix(event_key)
	return get_partner_matrix(event_matches=event_matches, teams_matrix=teams_matrix) \
		   - get_opp_matrix(event_matches=event_matches, teams_matrix=teams_matrix)

def get_scores_matrix(event_key="", event_matches=[], teams_matrix=[]):
	points = {}
	if len(teams_matrix) == 0:
		teams_matrix = get_team_matrix(event_key)
	if len(event_matches) == 0:
		event_matches = bscout.get_event_matches(event_key)
	teams_list = column_to_list(teams_matrix)
	for team in teams_list:
		points[team] = 0
	for match in event_matches:
		if match['comp_level'] == "qm":
			for color in ("red", "blue"):
				for team in match['alliances'][color]['teams']:
					score = match['alliances'][color]['score']
					if score > -1:
						points[int(team[3:])] += score
	scores_matrix = list_to_column([points[team] for team in teams_list])
	return scores_matrix

def get_opp_scores_matrix(event_key="", event_matches=[], teams_matrix=[]):
	points = {}
	if len(teams_matrix) == 0:
		teams_matrix = get_team_matrix(event_key)
	if len(event_matches) == 0:
		event_matches = bscout.get_event_matches(event_key)
	teams_list = column_to_list(teams_matrix)
	for team in teams_list:
		points[team] = 0
	for match in event_matches:
		if match['comp_level'] == "qm":
			colors = ("red", "blue")
			for i in (0, 1):
				for team in match['alliances'][colors[i]]['teams']:
					score = match['alliances'][colors[1-i]]['score']
					if score > -1:
						points[int(team[3:])] += score
	scores_matrix = list_to_column([points[team] for team in teams_list])
	return scores_matrix

def get_marg_scores_matrix(event_key="", event_matches=[], teams_matrix=[]):
	points = {}
	if len(teams_matrix) == 0:
		teams_matrix = get_team_matrix(event_key)
	if len(event_matches) == 0:
		event_matches = bscout.get_event_matches(event_key)
	teams_list = column_to_list(teams_matrix)
	for team in teams_list:
		points[team] = 0
	for match in event_matches:
		if match['comp_level'] == "qm":
			colors = ("red", "blue")
			for i in (0, 1):
				for team in match['alliances'][colors[i]]['teams']:
					score = match['alliances'][colors[i]]['score']
					opp_score = match['alliances'][colors[1-i]]['score']
					if score > -1:
						points[int(team[3:])] += (score - opp_score)
	scores_matrix = list_to_column([points[team] for team in teams_list])
	return scores_matrix

def compute_OPR(event_key):
	event_matches = bscout.get_event_matches(event_key)
	event_rankings = bscout.get_event_rankings(event_key)
	teams_matrix = get_teams_matrix(event_rankings=event_rankings)
	
	Apart = get_partner_matrix(event_matches=event_matches, \
										teams_matrix=teams_matrix)
	Bpart = get_scores_matrix(event_matches=event_matches, \
									  teams_matrix=teams_matrix)

	Xopr = numpy.linalg.solve(Apart, Bpart)
	return Xopr

def compute_DPR(event_key):
	event_matches = bscout.get_event_matches(event_key)
	event_rankings = bscout.get_event_rankings(event_key)
	teams_matrix = get_teams_matrix(event_rankings=event_rankings)
	
	Apart = get_partner_matrix(event_matches=event_matches, \
										teams_matrix=teams_matrix)
	Bopp = get_opp_scores_matrix(event_matches=event_matches, \
									  teams_matrix=teams_matrix)

	Xdpr = numpy.linalg.solve(Apart, Bopp)
	return Xdpr

def compute_CCWM(event_key):
	event_matches = bscout.get_event_matches(event_key)
	event_rankings = bscout.get_event_rankings(event_key)
	teams_matrix = get_teams_matrix(event_rankings=event_rankings)
	
	Apart = get_partner_matrix(event_matches=event_matches, \
							   teams_matrix=teams_matrix)
	Bmarg = get_marg_scores_matrix(event_matches=event_matches, \
								   teams_matrix=teams_matrix)

	Xccwm = numpy.linalg.solve(Apart, Bmarg)
	return Xccwm

def compute_MPR(event_key):
	event_matches = bscout.get_event_matches(event_key)
	event_rankings = bscout.get_event_rankings(event_key)
	teams_matrix = get_teams_matrix(event_rankings=event_rankings)
	
	Amarg = get_marg_partner_matrix(event_matches=event_matches, \
									teams_matrix=teams_matrix)
	Bmarg = get_marg_scores_matrix(event_matches=event_matches, \
								   teams_matrix=teams_matrix)

	Xmpr = numpy.linalg.solve(Amarg, Bmarg)
	return Xmpr

def initialize_pairings(pairings_dict, teams_matrix):
	for team1 in teams_matrix:
		pairings_dict[team1[0]] = {}
		for team2 in teams_matrix:
			pairings_dict[team1[0]][team2[0]] = 0

def add_pairing(pairings_dict, alliance):
	for team1 in alliance:
		team_num1 = int(team1[3:])
		for team2 in alliance:
			team_num2 = int(team2[3:])
			pairings_dict[team_num1][team_num2] += 1

def add_opponent(pairings_dict, alliance1, alliance2):
	for team1 in alliance1:
		team_num1 = int(team1[3:])
		for team2 in alliance2:
			team_num2 = int(team2[3:])
			pairings_dict[team_num1][team_num2] += 1

def list_to_column(some_list):
	return numpy.array([[value] for value in some_list])

def column_to_list(some_column):
	return [value[0] for value in some_column]

def writeCSV(teams_matrix, data_matrix):
	with open('out.csv', 'wbz') as csvfile:
		writer = csv.writer(csvfile, dialect=csv.excel)
		for i in range(len(teams_matrix)):
			row = [teams_matrix[i][0], data_matrix[i][0]]
			writer.writerow(row)

def write_stats_CSV(event_key):
	with open('%s_general_stats.csv' % event_key, 'wb') as csvfile:
		writer = csv.writer(csvfile, dialect=csv.excel)
		teams_matrix = get_teams_matrix(event_key)
		Xopr = compute_OPR(event_key)
		Xdpr = compute_DPR(event_key)
		Xccwm = compute_CCWM(event_key)
		Xmpr = compute_MPR(event_key)

		writer.writerow(["Team", "OPR", "DPR", "CCWM", "MPR"])
		for i in range(len(teams_matrix)):
			row = [teams_matrix[i][0], Xopr[i][0], Xdpr[i][0], Xccwm[i][0], Xmpr[i][0]]
			writer.writerow(row)

if __name__ == "__main__":
	import sys
	stat_print(sys.argv[1], compute_OPR)