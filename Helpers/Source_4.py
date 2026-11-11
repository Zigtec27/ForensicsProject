import csv

with open("ev.csv") as f:
    reader = csv.DictReader(f)

    states = {}

    for row in reader:
        state = row["state"].lower()

        states[state] = {}

        for column, value in row.items():

            if column == "state":
                continue

            if value == "" or value is None:
                continue

            states[state][f"ev{column}"] = int(value)


with open("states.lua", "w") as out:

    out.write("States = {\n")

    for state, data in states.items():

        out.write(f'  {state} = {{')

        for key, val in data.items():
            out.write(f'{key} = {val}, ')

        out.write("},\n")

    out.write("}\n")
