import json
import sys
import re

from collections import Counter, defaultdict

votes = json.load(open(sys.argv[1]))

out = defaultdict(Counter)

for vote in votes:
	for k, v in vote.items():
		if not k.startswith("election"):
			out[k][v] += 1
			continue


def calc_motions(obj):
	# Sorry, I sort like a crazy man.
	x = re.compile(r"(.*?)-(\d+)([a-z])?")
	y = []
	for key in obj.keys():
		rx = x.findall(key)
		if len(rx) == 0:
			y.append([key, '0', -1, ''])
		else:	
			y.append([key, rx[0][0], int(rx[0][1]), rx[0][2]])
	for i in reversed(range(1,4)):
		y = sorted(y, key=lambda l: l[i])
	keys = [i[0] for i in y]

	for name in keys:
		x = obj[name]

		sys.stdout.write("%s: " % name)
		res = (x['yes'] / (x['yes'] + x['no']) * 100)
		
		# I screwed up the HTML form.
		# Option 1 = "yes"
		# Option 2 = "no"
		if name != "motion-1":
			if res > 50:
				print("PASSED")
			else:
				print("FAILED")
		else:
			if res > 50:
				print("NO CHANGE")
			else:
				print("CHANGE ADOPTED")
		
		if name == "motion-1":
			print("{:>7}: {:<3} {}".format('Opt 1', x['yes'], "(%.2f%%)" % (x['yes'] / (x['yes'] + x['no']) * 100)))
			print("{:>7}: {:<3} {}".format('Opt 2', x['no'], "(%.2f%%)" % (x['no'] / (x['yes'] + x['no']) * 100)))
		else:
			for choice in ["yes", "no"]:
				print("{:>7}: {:<3} {}".format(choice, x[choice], "(%.2f%%)" % (x[choice] / (x['yes'] + x['no']) * 100)))
		print()

if __name__ == "__main__":
	calc_motions(out)
