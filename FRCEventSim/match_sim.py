import bscout
import oprlib
import toprlib
import random

tower_strength = 8
number_matches = 10 ** 4

class Data(object):

	def __init__(self):
		try:
			f = open("data.txt")
			string_data = f.readlines()
			self.tOPRs = eval(string_data[0].strip())
			self.OPRs = eval(string_data[1].strip())
			f.close()
		except IOError:

			self.teams = set()
			self.team_events = {}
			self.event_teams = {}
			self.events = [event["key"] for event in bscout.get_events(2016) \
							if (event["official"] and not event["key"] == "2016cmp")]

			for event in self.events:
				print "Getting event team lists: %s" % event
				self.event_teams[event] = []
				for team in bscout.get_event_teams_list(event):
					if team not in self.team_events:
						self.team_events[team] = []
					self.team_events[team].append(event)
					self.event_teams[event].append(team)
					self.teams.add(team)

			self.OPRs = {}

			OPRs_by_event = {}
			for event in self.events:
				print "Getting OPRs from event: %s" % event
				OPRs_by_event[event] = bscout.get_event_stats(event)["oprs"]
			for team in self.teams:
				print "Finding OPR for team: %d" % team
				oprs_list = []
				for event in self.team_events[team]:
					oprs_list.append(OPRs_by_event[event][str(team)])
				self.OPRs[team] = max(oprs_list)

			self.tOPRs = {}
		
			tOPRs_by_event = {}
			for event in self.events:
				print "Calculating tOPRs from event: %s" % event
				data = toprlib.get_stats_data(event)
				columns = toprlib.make_columns(event, data)
				tOPRs_by_event[event] = toprlib.get_tOPRs_match_sim(event, columns)
			for team in self.team_events:
				print "Finding tOPRs for team: %d" % team 
				boulders = []
				defenses = []

				for event in self.team_events[team]:
					index = self.event_teams[event].index(team)
					categories = ("autoBouldersHigh", "autoBouldersLow", "teleopBouldersHigh", \
									"teleopBouldersLow")
					boulders.append(sum([tOPRs_by_event[event][cat][index] for cat in categories]))
					defenses.append(tOPRs_by_event[event]["defenseCrosses"][index])

				self.tOPRs[team] = {"boulders": max(boulders)[0],
									"crossings": max(defenses)[0]}



			f = open("data.txt", "w")
			f.write(str(self.tOPRs) + "\n")
			f.write(str(self.OPRs) + "\n")
			f.close()


	def get_tOPRs(self):
		return self.tOPRs

	def get_OPRs(self):
		return self.OPRs

class Match(object):

	def __init__(self, data, teams):
		teams_copy = teams[:]
		random.shuffle(teams_copy)
		sample_teams = [teams_copy.pop() for i in range(6)]
		self.red_alliance = sample_teams[0:3]
		self.blue_alliance = sample_teams[3:6]
		self.data = data

	def __str__(self):
		return "%s vs %s" % (self.red_alliance, self.blue_alliance)

	def run_match(self):
		red_alliance = self.red_alliance
		blue_alliance = self.blue_alliance
		data = self.data

		RP = {}
		for team in red_alliance + blue_alliance:
			RP[team] = 0

		red_RP = 0
		blue_RP = 0

		red_score = sum([data.get_OPRs()[red_alliance[i]] for i in (0, 1, 2)]) 
		blue_score = sum([data.get_OPRs()[blue_alliance[i]] for i in (0, 1, 2)])

		red_score += random.uniform(-15, 15) 
		blue_score += random.uniform(-15, 15)

		red_crossings = sum([data.get_tOPRs()[red_alliance[i]]["crossings"] for i in (0, 1, 2)])
		blue_crossings = sum([data.get_tOPRs()[blue_alliance[i]]["crossings"] for i in (0, 1, 2)])

		red_boulders = sum([data.get_tOPRs()[red_alliance[i]]["boulders"] for i in (0, 1, 2)])
		blue_boulders = sum([data.get_tOPRs()[blue_alliance[i]]["boulders"] for i in (0, 1, 2)])

		# win or loss
		if int(red_score) == int(blue_score):
			red_RP, blue_RP = 1, 1
		elif red_score > blue_score:
			red_RP = 2
		else:
			blue_RP = 2

		# breach
		if red_crossings >= 8:
			red_RP += 1
		if blue_crossings >= 8:
			blue_RP += 1

		# capture
		if red_boulders >= tower_strength: 
			red_RP += 1
		if blue_boulders >= tower_strength: 
			blue_RP += 1

		print "%s (%d, %d RP) vs %s (%d, %d RP)" % (red_alliance, red_score, red_RP, \
			blue_alliance, blue_score, blue_RP) 

		for i in (0, 1, 2):
			RP[red_alliance[i]] = red_RP
			RP[blue_alliance[i]] = blue_RP

		return RP

if __name__ == "__main__":
	RPs = {}

	# IRI
	#event_teams = [16, 20, 25, 27, 33, 45, 67, 71, 118, 133, 135, 179, 195, 217, 225, 233, 234, 245, 330, 341, 346, 379, 461, 494, 503, 610, 624, 868, 910, 1011, 1023, 1024, 1058, 1086, 1114, 1241, 1257, 1310, 1405, 1511, 1529, 1619, 1640, 1675, 1718, 1720, 1731, 1746, 1747, 1806, 2013, 2052, 2056, 2338, 2451, 2468, 2481, 2502, 2590, 2614, 2767, 2771, 2823, 2826, 3015, 3130, 3357, 3476, 3538, 3620, 3683, 3824, 4039, 4587, 5172, 5254, 5460]
	# MkM
	event_teams = [11, 75, 102, 193, 223, 225, 293, 303, 316, 369, 484, 555, 806, 869, 1218, 1257, 1511, 1640, 1676, 1923, 2016, 2191, 2590, 3142, 4012, 4361, 4454, 4653, 4954, 5420, 5624, 5666, 5895]

	print "Collecting Data"
	data = Data()

	for team in event_teams:
		RPs[team] = []

	print "Simulating Matches"
	for i in xrange(number_matches):
		print "Match #%d" % i,
		match = Match(data, event_teams).run_match()
		for team in match:
			RPs[team].append(match[team])

	print "Ranking Teams"
	rankings = []
	for team in RPs:
		rankings.append((float(sum(RPs[team])) / len(RPs[team]), team))
	rankings.sort(reverse=True)

	final_rankings_list = []
	for i in range(len(rankings)):
		final_rankings_list.append((i+1, rankings[i][1], round(rankings[i][0], 2)))
	f = open("rankings.txt", "w")
	for i in range(len(final_rankings_list)):
		print final_rankings_list[i]
		f.write(str(final_rankings_list[i]) + "\n")
	f.close()