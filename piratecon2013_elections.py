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
    p.add_argument('--withdraw', nargs='*',
            help="Candidates to be withdrawn from count")
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

    for key in keys:
        ballot_list = ballots[key]
        for ballot in ballot_list:
            if ballot.get('ballot') is None or\
                        ballot['ballot'].get('elections') is None:
                if args.show_errors:
                    print("Erroneous ballot: %s" % json.dumps(ballot))
                errors += 1
                continue

            election = ballot['ballot']['elections']
            for position, o in election.items():
                count[position] += 1
                if o.get('Approval') is not None:
                    parsed_approval[position].append(o['Approval'])
                else:
                    parsed_ranking[position].append(o)
    print("There were %d erroneous ballots.\n" % errors)

    # Phase 1: Approval
    if args.approval:
        print("# Approval")
        for position, ballots in parsed_approval.items():
            print("\n## %s" % position)

            counter = Counter()
            for ballot in ballots:
                for candidate, value in ballot.items():
                    # 'on' is default HTML value for a checked checkbox.
                    if value == "on":
                        counter[candidate] += 1

            for candidate, value in counter.items():
                print("%s: Y:%s N:%s [%s%%]" % (candidate, value,
                     count[position] - value, "%.2f" % (value / count[position] * 100)))
        print()

    # Phase 2: Ranking
    if args.ranking:
        print ("# Ranking")
        # Convert ballots to CSV for schulze.py counting
        csvs = defaultdict(list)
        for position, ballots in parsed_ranking.items():
            candidates = list(sorted(parsed_ranking[position][0].keys()))
            csvs[position].append(",".join(candidates))
            for ballot in ballots:
                csvs[position].append(",".join([ballot[candidate] for candidate in candidates]))

        parsed_csvs = {}
        for position, csv in csvs.items():
            parsed_csvs[position] = "\n".join(csv)

        for position, csv in parsed_csvs.items():
            print("\n## %s" % position)
            run_election(csv, *args.withdraw or [], **{
                "show_errors": args.show_errors,
                "html": args.html,
                "urlencode": True
            })
