import argparse

parser = argparse.ArgumentParser(description="Generate set of player pairs")
parser.add_argument("--deterministic", action="store_true", help="Keep the order of games and participants")
parser.add_argument("--type",
    action="store",
    choices=["pairs", "round-robin"],
    default="pairs",
    help="Special testing value"
)
parser.add_argument("participants", type=str, nargs="+")
args = parser.parse_args()

if not args.deterministic:
    import random
    random.shuffle(args.participants)

if args.type == "pairs":
    if len(args.participants) % 2 != 0:
        print("Even number of participants required.")
        exit(2)

    matches = [
        [args.participants[i], args.participants[i+1]]
        for i in range(0, len(args.participants), 2)
    ]

elif args.type == "round-robin":
    matches = []
    for i1, p1 in enumerate(args.participants):
        for i2, p2 in enumerate(args.participants[i1:]):
            if i1 != i2:
                matches.append([p1, p2])

if not args.deterministic:
    random.shuffle(matches)

for pair in matches:
    print(" ".join(f"{p:>{2+max(len(q) for q in args.participants)}}" for p in pair))
