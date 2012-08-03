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
    if candidate not in candidates:
        return
    x = candidates.index(candidate)
    del candidates[x]
    for ballot in ballots:
        del ballot[x]


def check_ballot(candidates, ballot):
    for i in range(len(ballot)):
        if ballot[i] == '':
            ballot[i] = None
            continue
        
        try:
            if int(ballot[i]) <= 0:
                return False
        
        except:
            return False
        
        ballot[i] = int(ballot[i])
    return True
    

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


def calculate_first_prefs(candidates, ballots):
    first_prefs = Counter()

    for ballot in ballots:
        if not check_ballot(candidates, ballot):
            print("Invalid ballot: %s" % ballot)
            del ballot
            continue
        
        highest = []
        
        for a in range(len(ballot)):
            if ballot[a] is None:
                pass
            elif len(highest) < 1 or ballot[a] < ballot[highest[0]]:
                highest = [a]
            elif ballot[a] == ballot[highest[0]]:
                highest.append(a)
            
        for i in highest:
            first_prefs[candidates[i]] += 1
    
    return first_prefs


def print_first_prefs(candidates, ballots):
    fp = calculate_first_prefs(candidates, ballots)
    
    print("Total ballots: %s" % len(ballots))
    for name, value in fp.most_common():
        print("{:>12}: {:<2} [All: {}%] [Compared: {}%]".format(
            name,
            value,
            "%.2f" % (value / len(ballots) * 100),
            "%.2f" % (value / sum(fp.values()) * 100)
        ))


def count_ballots(candidates, ballots):
    count = build_matrix(len(candidates))

    for ballot in ballots:
        if not check_ballot(candidates, ballot):
            print("Invalid ballot: %s" % ballot)
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
                elif ballot[a] is ballot[b] is None:
                    continue

                # If a is blank, fail
                elif ballot[a] is None:
                    continue

                # all ints < blank or x < y
                elif ballot[b] is None or ballot[a] < ballot[b]:
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


def print_rankings(candidates, rankings, winner_only=False):
    count = Counter()
    for i in range(len(candidates)):
        count[i] = rankings[i]
    count = count.most_common()

    if winner_only:
        print(candidates[count[0][0]])
        return

    c = 0
    for k, v in count:
        c += 1
        print("(%s) %s" % (c, candidates[k]))


def run_election(fn, *withdraws, winner_only=False, hide_grids=False, first_prefs=False, html=False):
    candidates, ballots = load_ballots(fn)
    for w in withdraws:
        withdraw_candidate(w, candidates, ballots)
    
    if first_prefs:
        print_first_prefs(candidates, ballots)
        return
    
    count = count_ballots(candidates, ballots)
    if html:
        print(convert_matrix_to_html_table(candidates, count))
        return 
    
    paths = calculate_strongest_paths(count)
    rankings = calculate_candidate_order(paths)
    
    if not winner_only and not hide_grids:
        print("Count matrix:")
        print_matrix(count)
        print()

        print("Path matrix:")
        print_matrix(paths)
        print()

    print_rankings(candidates, rankings, winner_only)


def convert_matrix_to_html_table(candidates, matrix):
    x = ["<tr><th></th><th style='border: 1px solid gray'>" + 
            "</th><th style='border: 1px solid gray'>".join(candidates) + 
            "</th></tr>"]

    for i in range(len(matrix)):
        row = []
        for j in range(len(matrix[i])):
            if i == j:
                row.append("<td style='border: 1px dotted gray; background-color:#ddd'></td>")
            elif matrix[i][j] < matrix[j][i]:
                row.append("<td style='border: 1px dotted gray; background-color:#fcc'>%s</td>" % matrix[i][j])
            elif matrix[i][j] > matrix[j][i]:
                row.append("<td style='border: 1px dotted gray; background-color:#cfc'>%s</td>" % matrix[i][j])
        x.append("<tr><th style='border: 1px solid gray'>%s</th>%s</tr>" % (candidates[i], "".join(row)))

    return "<table style='border-collapse: collapse; border: 1px solid black'><tbody>" + "".join(x) + "</tbody><table>"


if __name__ == "__main__":
    args = {}
   
    # TODO: make this sane, obviously. This is just derpy.

    if '-h' in sys.argv:
        args['html'] = True
        del sys.argv[sys.argv.index('-h')]

    if '-w' in sys.argv:
        args['winner_only'] = True
        del sys.argv[sys.argv.index('-w')]
    
    if '-s' in sys.argv:
        args['hide_grids'] = True
        del sys.argv[sys.argv.index('-s')]
    
    if '-f' in sys.argv:
        args['first_prefs'] = True
        del sys.argv[sys.argv.index('-f')]
    
    run_election(sys.argv[1], *sys.argv[2:], **args)
