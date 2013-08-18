import json
import argparse

def get_ballot(record, words):
    x = record
    if words is not None:
        words = words.split(".")
        for word in words:
            try:
                x = x[word]
            except Exception as e:
                print(record)
                raise e
    return x

def get_csv(data, slug, words=None):
    x = data[slug]

    candidates = list(get_ballot(x[0], words).keys())
    records = []
    records.append(",".join(candidates))

    for record in x:
        o = []
        record = get_ballot(record, words)
        for candidate in candidates:
            o.append(record[candidate])
        records.append(",".join(o))

    print("\n".join(records))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument('--slug', nargs='?')
    p.add_argument('--prefix', nargs='?')
    p.add_argument('ballots', type=argparse.FileType('r'))
    args = p.parse_args()

    ballots = json.load(args.ballots)
    get_csv(ballots, args.slug, args.prefix)

