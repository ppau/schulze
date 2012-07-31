import json
import sys

from collections import Counter, defaultdict

votes = json.load(open(sys.argv[1]))

out = defaultdict(Counter)

for vote in votes:
	for k, v in vote.items():
		if not k.startswith("election"):
			out[k][v] += 1
			continue


def calc_motions(obj):
	# Sorry, I sort like a crazy man. And this barely works.
	keys = [i.rsplit('-', 1)[0] + '-' + ( max(0, 2-len(i.rsplit('-',1)[-1])) )*'0' + i.rsplit('-', 1)[-1] for i in obj.keys()]
	keys.sort()

	for name in keys:
		# If it worked, I wouldn't need to do this thing here.
		if name.startswith('quo'):
			name = "quorum"
		x = obj[name.replace('0', '')]


		sys.stdout.write("- %s: " % name)
		res = (x['yes'] / (x['yes'] + x['no']) * 100)
		
		# I screwed up the HTML form.
		# Option 1 = "yes"
		# Option 2 = "no"
		if name != "motion-01":
			if res > 50:
				print("PASSED")
			else:
				print("FAILED")
		
		if name == "motion-01":
			print("\n{:>7}: {:<3} {}".format('Opt 1', x['yes'], "(%.2f%%)" % (x['yes'] / (x['yes'] + x['no']) * 100)))
			print("{:>7}: {:<3} {}".format('Opt 2', x['no'], "(%.2f%%)" % (x['no'] / (x['yes'] + x['no']) * 100)))
		else:
			for choice in ["yes", "no"]:
				print("{:>7}: {:<3} {}".format(choice, x[choice], "(%.2f%%)" % (x[choice] / (x['yes'] + x['no']) * 100)))

if __name__ == "__main__":
	calc_motions(out)
