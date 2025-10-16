from .tdh2 import dealer, serialize, group
import argparse
import pickle

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('players', help='The number of players')
    parser.add_argument('k', help='k')
    parser.add_argument('fname', help='fname')
    args = parser.parse_args()
    players = int(args.players)
    fname = args.fname
    if args.k:
        k = int(args.k)
    else:
        k = players / 2  # N - 2 * t
    PK, SKs = dealer(players=players, k=k)
    content = (PK.l, PK.k, serialize(PK.VK), [serialize(VKp) for VKp in PK.VKs],
               [(SK.i, serialize(SK.SK)) for SK in SKs])
    print(pickle.dumps(content))
    with open(fname, "wb") as f:
        pickle.dump(content, f)

if __name__ == '__main__':
    main()
    