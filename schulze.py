from collections import defaultdict, Counter
from urllib.parse import quote
from io import StringIO

import json
import sys
import argparse

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

def load_ballots(f):
    lines = f.readlines()
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


def count_ballots(candidates, ballots, show_errors=False):
    count = build_matrix(len(candidates))

    for ballot in ballots:
        if not check_ballot(candidates, ballot):
            if show_errors:
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


def determine_rankings(paths):
    ranking = [0 for i in range(len(paths))]
    for i in range(len(paths)):
        for j in range(len(paths)):
            if i == j: continue
            if paths[i][j] > paths[j][i]:
                ranking[i] += 1

    return ranking


def break_ties(paths, ranking):
    scores = [0 for i in range(len(paths))]
    for i in range(len(paths)):
        if ranking[i] == 0:
            continue
        for j in range(len(paths)):
            if i == j: continue
            if paths[i][j] > paths[j][i]:
                scores[i] += paths[i][j] - paths[j][i]

    return scores


def print_rankings(candidates, rankings, winner_only=False):
    count = Counter()
    for i in range(len(candidates)):
        count[i] = rankings[i]
    count = count.most_common()

    if winner_only:
        print(candidates[count[0][0]])
        return

    c = 0
    print("Rankings:\n")
    for k, v in count:
        c += 1
        print("(%s) %s" % (c, candidates[k]))


def output(candidates, paths, rankings, count, tie, winner_only=False, html=False, urlencode=False, hide_grids=False):
    if html:
        print(convert_matrix_to_html_table(candidates, count, urlencode))
        #print(strongest_path_html(candidates, paths))
        print("<pre>")
        if tie:
            print("Tie detected. Ranking by strongest path scores:\n")
            for i in range(len(candidates)):
                print("%s: %s" % (candidates[i], rankings[i]))
            print()
        print_rankings(candidates, rankings, winner_only)
        print("</pre>")
        return

    if not winner_only and not hide_grids:
        print("Count matrix:")
        print_matrix(count)
        print()

        print("Path matrix:")
        print_matrix(paths)
        print()

        if tie:
            print("Tie detected. Ranking by combined strongest path scores:\n")
            for i in range(len(candidates)):
                print("%s: %s" % (candidates[i], rankings[i]))
            print()

    print_rankings(candidates, rankings, winner_only)


def run_election(f, *withdraws, winner_only=False, hide_grids=False, first_prefs=False, html=False, urlencode=False, show_errors=False):
    if isinstance(f, str):
        f = StringIO(f)
    candidates, ballots = load_ballots(f)
    for w in withdraws:
        withdraw_candidate(w, candidates, ballots)

    if first_prefs:
        print_first_prefs(candidates, ballots)
        return

    count = count_ballots(candidates, ballots, show_errors)
    paths = calculate_strongest_paths(count)
    rankings = determine_rankings(paths)

    # check to see if highest rank is shared
    tie = False
    if rankings.count(max(rankings)) > 1:
        tie = True
        rankings = break_ties(count, rankings)

    output(candidates, paths, rankings, count, tie, winner_only, html, urlencode, hide_grids)


def strongest_path_html(candidates, matrix):
    cross = "&times;"
    info = "These are the strongest paths. This is required to determine a winner in the case of no obvious majority pairwise winner."
    headers = "<tr><th class='empty'></th><th><div>" +\
        "</div></th><th><div>".join(candidates) + "</div></th></tr>"
    x = []

    for i in range(len(matrix)):
        row = []
        for j in range(len(matrix[i])):
            if i == j:
                row.append("<td></td>")
                continue

            total = matrix[i][j] + matrix[j][i]
            if total != 0:
                success = int(matrix[i][j] / total * 100)
                fail = 100 - success
            else:
                success = fail = 0
            if matrix[i][j] < matrix[j][i]:
                row.append("<td class='red'>%s</td>" % cross)
            elif matrix[i][j] > matrix[j][i]:
                row.append("<td class='green'>%s</td>" % matrix[i][j])
            elif matrix[i][j] == matrix[j][i]:
                row.append("<td class='yellow'>%s</td>" % cross)
        x.append("<tr><th>%s</th>%s</tr>" % (candidates[i], "".join(row)))

    return ("<table><caption>%s</caption><thead>%s</thead><tbody>" % (info, headers)) + "".join(x) + "</tbody></table>"


def convert_matrix_to_html_table(candidates, matrix, urlencode):
    info = "The horizontal axis is compared with the vertical axis to see who is the most preferred candidate. The ranking order is determined by the candidates with the most green squares."
    headers = '<tr><th class="empty"></th><th><div>' +\
        "</div></th><th><div>".join(candidates) + "</div></th></tr>"
    x = []
    data = {}

    for i in range(len(matrix)):
        row = []
        for j in range(len(matrix[i])):
            if i == j:
                row.append("<td></td>")
                continue

            title = candidates[i] + ' vs ' + candidates[j]
            total = matrix[i][j] + matrix[j][i]
            if total != 0:
                success = int(matrix[i][j] / total * 100)
                fail = 100 - success
            else:
                success = fail = 0
            content = ('''<p>%s voters prefer %s over %s.</p><div class='progress'>''' +\
                '''<div class='bar bar-success' style='width: %s%%'>%s</div>''' +\
                '''<div class='bar bar-danger' style='width: %s%%'>%s</div>''' +\
            '''</div>''') % (matrix[i][j], candidates[i], candidates[j],
                    success, "%s (%s%%)" % (matrix[i][j], success),
                    fail, "%s (%s%%)" % (matrix[j][i], fail))
            data[title] = content
            if matrix[i][j] < matrix[j][i]:
                row.append('<td title="%s" class="red">%s</td>' % (title, matrix[i][j]))
            elif matrix[i][j] > matrix[j][i]:
                row.append('<td title="%s" class="green">%s</td>' % (title, matrix[i][j]))
            elif matrix[i][j] == matrix[j][i]:
                row.append('<td title="%s" class="yellow">%s</td>' % (title, matrix[i][j]))
        x.append("<tr><th>%s</th>%s</tr>" % (candidates[i], "".join(row)))

    return ('<script>var electionData = \n%s\n</script><table class="ranking"><caption>%s</caption><thead>%s</thead><tbody>' % (script_data(data, urlencode), info, headers)) + "".join(x) + "</tbody></table>"


def script_data(data, urlencode):
    if not urlencode:
        return json.dumps(data, indent=2)
    else:
        return 'JSON.parse(decodeURIComponent("%s"))' % quote(json.dumps(data))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument('-H', '--html', action='store_true',
            help="Output HTML")
    p.add_argument('-U', '--urlencode', action='store_true')
    p.add_argument('-w', '--winner-only', action='store_true')
    p.add_argument('-s', '--hide-grids', action='store_true')
    p.add_argument('-f', '--first-prefs', action='store_true')
    p.add_argument('--show-errors', action='store_true')
    p.add_argument('--withdraw', nargs='*',
            help="Candidates to withdraw from election")
    p.add_argument('ballots', type=argparse.FileType('r'))
    args = dict(p.parse_args()._get_kwargs())
    ballots = args.get('ballots')
    withdraw = args.get('withdraw') or []

    del args['withdraw']
    del args['ballots']
    run_election(ballots, *withdraw, **args)
