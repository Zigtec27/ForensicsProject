# Casey Perlinger-Jett
# SpeechWire .txt -> .json converter
#
# Converts the finals results from a raw .txt file from
# SpeechWire to a sorted .json file.

import json
import re

# Inputted file (At the top for easy access.)
file_path = "CUNE_Fall_R.txt"

# Open the file and read it.
with open(file_path, "r", encoding="utf-8") as file:
    raw_data = file.read()

# EVENT TYPES
# Initial the event mapping.
pointer_event = None
# Event abbreviations for storage. (This'll eliminate spaces in stored names too.)
EVENT_DICT = {
    "After Dinner Speaking": "ADS",
    "Communication Analysis": "CA",
    "Dramatic Interpretation": "DI",
    "Duo Interpretation": "DUO",
    "Extemporaneous Speaking": "EXTEMP",
    "Impromptu Speaking": "IMP",
    "Informative Speaking": "INFO",
    "Parliamentary Debate": "PARLI",
    "JV Parliamentary Debate": "JV_PARLI",
    "Open Parliamentary Debate": "OPEN_PARLI",
    "Persuasive Speaking": "PERS",
    "Poetry Interpretation": "POE",
    "Program Oral Interpretation": "POI",
    "Prose Interpretation": "PROSE"
}

# .json file initial outline.
structured_json = {}

# Get rid of white space, while also separating all the data by said white space.
lines = [line.strip() for line in raw_data.split("\n") if line.strip()]

# The actual loop that goes through every event and converts it to json.
# We're using enumerate today because otherwise it tries to read everything.
for i, line in enumerate(lines):
    # If the code finds an event line
    # (I found out that instead of doing all 11 events, I could do the one
    #  placement line and then utilize [i-1] to get event type.)
    if "Place" in line and "Competitor" in line and "Team" in line:
        full_event_name = lines[i-1]
        pointer_event = EVENT_DICT.get(full_event_name, full_event_name)
        if pointer_event not in structured_json:
            structured_json[pointer_event] = []
        continue

    # Skip the inbetween line of the tables that got included when copying from SpeechWire.
    if "Click here to return to the main" in line:
        continue

    if pointer_event:
        # Split the indiviual line of each event placement.
        parts = [p.strip() for p in re.split(r'\t|\s{2,}', line) if p.strip()]

        # Create the entries for each of the finalists.
        # Make sure it is a finalist first though.
        if parts[0].isdigit() or parts[0] == "Fin.": 
            entry = {
                "Place":  parts[0],
                "Name":   parts[1],
                "School": parts[2]
                }
                # Add each entry into the .json file under the event header.
            structured_json[pointer_event].append(entry)



# Output getting molded together
json_output = json.dumps(structured_json, indent=4)

# Create the new output file and put it in said file.
with open("CUNE_Fall_results.json", "w", encoding="utf-8") as f:
    f.write(json_output)

# Print so that I see in the terminal that it completed and can move on.
print("Done!")
