from __future__ import division
from collections import defaultdict, Counter
from itertools import chain
from schulze import run_election

import argparse
import json
import sys


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument('--slugs', nargs='*',
            help="Elections to be calculated (Default: all)")
    p.add_argument('--approval', action="store_true",
            help="Approval phase only")
    p.add_argument('--ranking', action="store_true",
            help="Ranking phase only")
    p.add_argument("--show-errors", action="store_true",
            help="Show erroneous ballots")
    p.add_argument("--html", action="store_true",
            help="Output HTML")
    p.add_argument('ballots', type=argparse.FileType('r'))
    args = p.parse_args()

    if not args.approval and not args.ranking:
        args.approval = True
        args.ranking = True

    ballots = json.load(args.ballots)
    parsed_approval = defaultdict(list)
    parsed_ranking = defaultdict(list)
    count = Counter()
    errors = 0

    # Phase 0: Parse ballots
    if args.slugs:
        keys = args.slugs
    else:
        keys = list(ballots.keys())
        # This key has no elections
        keys.remove('ppm2013')

    for key in keys:
        ballot_list = ballots[key]
        for ballot in ballot_list:
            if ballot.get('ballot') is None or\
                        ballot['ballot'].get('election') is None:
                if args.show_errors:
                    print("Erroneous ballot: %s" % json.dumps(ballot))
                errors += 1
                continue

            election = ballot['ballot']['election']
            for state, o in election.items():
                count[state] += 1
                for phase, values in o.items():
                    if phase == "Approval":
                        parsed_approval[state].append(values)
                    elif phase == "Ranking":
                        parsed_ranking[state].append(values)
    print("There were %d erroneous ballots.\n" % errors)

    # Phase 1: Approval
    if args.approval:
        print("# Approval")
        for state, ballots in parsed_approval.items():
            print("\n## %s" % state)

            counter = Counter()
            for ballot in ballots:
                for candidate, value in ballot.items():
                    # 'on' is default HTML value for a checked checkbox.
                    if value == "on":
                        counter[candidate] += 1

            for candidate, value in counter.items():
                print("%s: Y:%s N:%s [%s%%]" % (candidate, value,
                     count[state] - value, "%.2f" % (value / count[state] * 100)))
        print()

    # Phase 2: Ranking
    if args.ranking:
        print ("# Ranking")
        # Convert ballots to CSV for schulze.py counting
        csvs = defaultdict(list)
        for state, ballots in parsed_ranking.items():
            candidates = list(sorted(parsed_ranking[state][0].keys()))
            csvs[state].append(",".join(candidates))
            for ballot in ballots:
                csvs[state].append(",".join([ballot[candidate] for candidate in candidates]))

        parsed_csvs = {}
        for state, csv in csvs.items():
            parsed_csvs[state] = "\n".join(csv)

        for state, csv in parsed_csvs.items():
            print("\n## %s" % state)
            run_election(csv, *[], **{
                "show_errors": args.show_errors,
                "html": args.html,
                "urlencode": True
            })
