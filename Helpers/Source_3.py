import csv

candidate_name = None
states = {}

with open("election.csv") as f:
    reader = csv.reader(f)

    header = next(reader)
    candidate_name = header[0]

    for row in reader:
        state = row[0].lower()

        vote = float(row[1].replace("%",""))
        margin = float(row[2].replace("%",""))
        approval = float(row[3].replace("%",""))
        election_elo = float(row[4])
        candidate_elo = float(row[5])

        states[state] = (vote, margin, approval, election_elo, candidate_elo)

with open("new_candidates.lua","a") as f:
    f.write("Candidates = {\n")
    f.write(f'  ["{candidate_name}"] = {{\n')

    for state,data in states.items():
        vote,margin,approval,election_elo,candidate_elo = data

        f.write(
            f'    {state} = {{vote = {vote}, margin = {margin}, approval = {approval}, '
            f'election_elo = {election_elo}, candidate_elo = {candidate_elo}}},\n'
        )

    f.write("  }\n")
    f.write("}\n")
