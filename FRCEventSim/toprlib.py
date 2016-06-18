import bscout
import oprlib
import numpy
import csv

normal_criteria = [
				# AUTO
				"autoPoints", "autoBouldersLow", "autoBouldersHigh", \
				"autoBoulderPoints", "autoReachPoints", "autoCrossingPoints", \
				# TELEOP BOULDERS
				"teleopBouldersLow", "teleopBouldersHigh", \
				"teleopBoulderPoints", \
				# TELEOP DEFENCES
				"teleopDefensesBreached", "teleopCrossingPoints", \
				# TELEOP ENDGAME
				"teleopScalePoints", "teleopChallengePoints", "teleopTowerCaptured", \
				
				# TELEOP OTHER
				"teleopPoints", "foulCount", "techFoulCount", "totalPoints", \
				]

special_criteria = ["teleopTowerFacesChallenged", "teleopTowerFacesScaled", "defenseCrosses"]

match_sim_criteria = ["autoBouldersLow", "autoBouldersHigh", "teleopBouldersLow", \
				"teleopBouldersHigh", "defenseCrosses"]

#removed: breach points, capture points

criteria = sorted(normal_criteria + special_criteria)


def initialize_stats_data(teams_list):
	result = {}
	for criterion in criteria:
		result[criterion] = {}
		for team in teams_list:
			result[criterion][team] = 0
	return result

def add_match(match_data, stats_data):
	colors = ("red", "blue")
	for color in colors:
		scoring = match_data["score_breakdown"][color]
		for team in match_data["alliances"][color]["teams"]:
			team_num = int(team[3:])
			for criterion in normal_criteria:
				stats_data[criterion][team_num] += int(scoring[criterion])
			values = scoring.values()
			stats_data["teleopTowerFacesChallenged"][team_num] += values.count("Challenged")
			stats_data["teleopTowerFacesScaled"][team_num] += values.count("Scaled")
			for i in range(5):
				def_crosses = scoring["position"+str(i+1)+"crossings"]
				stats_data["defenseCrosses"][team_num] += def_crosses

def get_stats_data(event_key):
	teams = bscout.get_event_teams_list(event_key)
	data = initialize_stats_data(teams)
	matches = bscout.get_event_matches(event_key)
	for match in matches:
		if match["comp_level"] == "qm" and match["alliances"]["red"]["score"] != -1:
			add_match(match, data)
	return data

def make_columns(event_key, stats_data):
	teams = bscout.get_event_teams_list(event_key)
	columns = {}
	for criterion in stats_data:
		criterion_list = [stats_data[criterion][team] for team in teams]
		columns[criterion] = numpy.ndarray((len(teams), 1))
		for i in range(len(teams)):
			columns[criterion][i][0] = criterion_list[i]
	return columns

def get_tOPRs(event_key, columns):
	A = oprlib.get_partner_matrix(event_key=event_key)
	tOPRs = {}
	for criterion in criteria:
		tOPRs[criterion] = numpy.linalg.solve(A, columns[criterion])
	return tOPRs

def get_tOPRs_match_sim(event_key, columns):
	A = oprlib.get_partner_matrix(event_key=event_key)
	tOPRs = {}
	for criterion in match_sim_criteria:
		tOPRs[criterion] = numpy.linalg.solve(A, columns[criterion])
	return tOPRs

def write_sheet_to_CSV(event_key, sheet):
	with open("%s_tasks.csv" % event_key, 'wb') as csvfile:
		writer = csv.writer(csvfile, dialect='excel')
		for row in sheet:
			writer.writerow(row)

def write_tOPRs_CSV(event_key):
	data = get_stats_data(event_key)
	columns = make_columns(event_key, data)
	tOPRs = get_tOPRs(event_key, columns)
	teams = bscout.get_event_teams_list(event_key)
	top_row = ["Team"] + [criterion for criterion in criteria]
	sheet = [top_row] + [[team] for team in teams]
	for criterion in criteria:
		column = tOPRs[criterion]
		for i in range(len(column)):
			sheet[i+1].append(round(column[i][0],2))
	write_sheet_to_CSV(event_key, sheet)
