from collections import defaultdict, Counter
import json
import sys

"""
Ballots are csv's.
- First line contains the candidates
- Consecutive lines contain preferences in candidate order

Example:

smith,jones,james
1,2,3
,,1
,1,2
,4,4
"""

def load_ballots(fn):
    lines = open(fn, 'r').readlines()
    header = lines[0].strip().split(',')
    ballots = [line.strip().split(',') for line in lines[1:]]
    return header, ballots 


def withdraw_candidate(candidate, candidates, ballots):
    x = candidates.index(candidate)
    del candidates[x]
    for ballot in ballots:
        del ballot[x]


def check_ballot(candidates, ballot):
    for b in ballot:
        if b == '':
            continue
        int(b)
    

def build_matrix(size):
    x = [[0 for j in range(size)] for i in range(size)]
    for i in range(size):
        x[i][i] = None
    return x


def print_matrix(matrix):
    for line in matrix:
        print(("+----" * len(line)) + "+")
        for n in line:
            if n is None: n = 'X'
            sys.stdout.write("|" + "{:^4}".format(n))
        print("|")
    print(("+----" * len(line)) + "+")


def count_ballots(candidates, ballots):
    count = build_matrix(len(candidates))

    for ballot in ballots:
        valid = True
        try:
            check_ballot(candidates, ballot)
        except Exception as e: 
            valid = False
        if not valid:
            continue

        for a in range(len(ballot)):
            for b in range(len(ballot)):
                # Skip same number
                if a == b:
                    continue

                # Both equal, neither are lt, thus fail
                elif ballot[a] == ballot[b]: 
                    continue

                # Both blank, neither are lt, thus fail
                elif ballot[a] == "" and ballot[b] == "":
                    continue

                # If a is blank, it is always less than b if b != ''
                elif ballot[a] == "" and ballot[b] != "":
                    count[a][b] += 1

                # Blank is not lt any number
                elif int(ballot[a]) and ballot[b] == "":
                    count[a][b] += 1

                # Last actual check if both are ints
                elif int(ballot[a]) < int(ballot[b]):
                    count[a][b] += 1
        
    return count


def calculate_strongest_paths(count):
    paths = build_matrix(len(count))

    for i in range(len(count)):
        for j in range(len(count)):
            if i == j: continue
            if count[i][j] > count[j][i]:
                paths[i][j] = count[i][j]
    
    for i in range(len(count)):
        for j in range(len(count)):
            if i == j: continue
            for k in range(len(count)):
                if i != k and j != k:
                    paths[j][k] = max(paths[j][k], min(paths[j][i], paths[i][k]))
    
    return paths


def calculate_candidate_order(paths):
    ranking = [0 for i in range(len(paths))]
    for i in range(len(paths)):
        for j in range(len(paths)):
            if i == j: continue
            if paths[i][j] > paths[j][i]:
                ranking[i] += 1
    
    return ranking


def print_rankings(candidates, rankings):
    count = Counter()
    for i in range(len(candidates)):
        count[i] = rankings[i]
    count = count.most_common()

    c = 0
    for k, v in count:
        c += 1
        print("(%s) %s" % (c, candidates[k]))


def run_election(fn, *withdraws):
    candidates, ballots = load_ballots(fn)
    for w in withdraws:
        withdraw_candidate(w, candidates, ballots)
    count = count_ballots(candidates, ballots)
    paths = calculate_strongest_paths(count)
    rankings = calculate_candidate_order(paths)
    
    print("Count matrix:")
    print_matrix(count)
    print()

    print("Path matrix:")
    print_matrix(paths)
    print()

    print_rankings(candidates, rankings)

if __name__ == "__main__":
    run_election(sys.argv[1], *sys.argv[2:])
