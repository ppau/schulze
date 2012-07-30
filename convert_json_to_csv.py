import json
import sys

from collections import defaultdict

positions = defaultdict(dict)

ballots = json.load(open(sys.argv[1]))

# Find positions
for k in ballots[0].keys():
	if not k.startswith("election"):
		continue
	
	pos, person = k.split("-", 1)[1].split("_")
	if not positions[pos].get('candidates'):
		positions[pos] = {
			'candidates': [],
			'ballots': []
		}
	
	positions[pos]['candidates'].append(person)

# Find results
for ballot in ballots:
	for pos, x in positions.items():
		b = []
		for candidate in x['candidates']:
			b.append(ballot['election-%s_%s' % (pos, candidate)])
		x['ballots'].append(b)

# Output files
for pos, x in positions.items():
	f = open("%s.ballot.csv" % pos, 'w')
	f.write(",".join(x['candidates']) + "\n")
	
	for ballot in x['ballots']:
		f.write(",".join(ballot) + "\n")
	f.close()

