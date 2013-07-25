from collections import defaultdict, Counter
from itertools import chain

import argparse
import json
import sys

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument('ballots', type=argparse.FileType('r'),
            help="Ballot JSON file")
    p.add_argument('--show-errors', action='store_true',
            help="Show erroneous ballots")
    args = p.parse_args()

    # As the ballot json file is a list of dicts, we only care about the values
    # of each dict, so we're going to flatten it.
    ballots = chain(*json.load(args.ballots).values())
    motions = defaultdict(Counter)
    errors = 0

    for ballot in ballots:
        if ballot['ballot'].get('motions') is None:
            if args.show_errors:
                print("Errorneous ballot: " + json.dumps(ballot['ballot']))
            errors += 1
            continue
        for k, v in ballot['ballot']['motions'].items():
            motions[k][v] += 1


    print("There were %d erroneous ballots.\n" % errors)
    for n in sorted(motions.keys()):
        c = motions[n]
        percent = "%.2f" % (c["Yes"] / (c["Yes"] + c["No"]) * 100)
        print("%s: Y:%s N:%s A:%s [%s%%]" % (n, c["Yes"], c['No'],
            c['Abstain'], percent))
