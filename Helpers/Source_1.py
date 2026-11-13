# College Football Scorigami Data Cleaner
# This is a file I made awhile ago to sort unclear data from a .csv into a .json
# It's one of the main sources I pulled from when building the .txt -> .json converter for this project.

import csv
import json
import os
import re
import sys
import uuid
from datetime import datetime
from collections import OrderedDict

# File paths
DB_PATH = "games.json"
TEAM_INDEX = "team_index.json"
YEAR_INDEX = "year_index.json"
CONF_INDEX = "conference_index.json"
SCORE_INDEX = "score_index.json"
FINAL_INDEX = "final_index.json"

def load_json(path):
    return json.load(open(path)) if os.path.exists(path) else {}

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def normalize_team(raw_name):
    raw = (raw_name or "").strip()
    rank = None
    if raw.startswith("("):
        parts = raw.split(")", 1)
        try:
            rank = int(parts[0][1:])
        except Exception:
            rank = None
        raw = parts[1].strip() if len(parts) > 1 else raw
    return {"name": raw, "rank": rank}

def slug_name_for_id(name):
    return re.sub(r'[^A-Za-z0-9]', '', name)

def generate_box_url(date_str, team_name):
    team_slug = team_name.lower().strip()
    team_slug = re.sub(r'\s+', '-', team_slug)
    team_slug = re.sub(r'[^a-z0-9-]', '', team_slug)
    team_slug = re.sub(r'-+', '-', team_slug).strip('-')

    return (
        f"https://www.sports-reference.com/cfb/boxscores/"
        f"{date_str}-{team_slug}.html"
    )

def load_conf_map(conf_file):
    mapping = {}
    if not conf_file or not os.path.exists(conf_file):
        return mapping

    # Detect extension
    _, ext = os.path.splitext(conf_file)
    if ext.lower() == ".json":
        return load_json(conf_file)

    # Assume CSV if not JSON
    with open(conf_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            team_raw = row.get("Team") or row.get("team") or ""
            conf_raw = row.get("Conference") or row.get("Conf") or row.get("conference") or ""
            if not team_raw:
                continue
            team = normalize_team(team_raw)["name"]
            mapping[team] = conf_raw.strip() if conf_raw else "Undetermined"
    return mapping

def load_nicknames(nick_csv):
    mapping = {}
    if not nick_csv or not os.path.exists(nick_csv):
        return mapping
    with open(nick_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            team_raw = row.get("Team") or row.get("team") or ""
            if not team_raw:
                continue
            key = normalize_team(team_raw)["name"]
            nickname = (row.get("Nickname") or row.get("Nick") or row.get("Short") or row.get("Abbrev") or "").strip()
            mapping[key] = nickname if nickname else key
    return mapping

def sort_indexes(games, team_index, year_index, conf_index, score_index, final_index):
    games = OrderedDict(sorted(games.items(), key=lambda x: x[1]["date"]))
    team_index = OrderedDict(sorted(team_index.items(), key=lambda x: x[1]["teamName"].lower()))

    year_index = OrderedDict(sorted(year_index.items(), key=lambda x: int(x[0])))
    for year, g_list in year_index.items():
        year_index[year] = sorted(g_list, key=lambda gid: games.get(gid, {}).get("date", ""))

    conf_index = OrderedDict(sorted(conf_index.items(), key=lambda x: x[0].lower()))
    for conf, g_list in conf_index.items():
        conf_index[conf] = sorted(g_list, key=lambda gid: games.get(gid, {}).get("date", ""))

    def score_key(s):
        w, l = map(int, s.split("-"))
        return (w, l)
    score_index = OrderedDict(sorted(score_index.items(), key=lambda x: score_key(x[0])))
    final_index = OrderedDict(sorted(final_index.items(), key=lambda x: score_key(x[0])))
    for s, g_list in final_index.items():
        final_index[s] = sorted(list(dict.fromkeys(g_list)), key=lambda gid: games.get(gid, {}).get("date", ""))

    return games, team_index, year_index, conf_index, score_index, final_index

def bulk_import(input_csv="john.csv", conf_file="team_conferences.csv", nick_csv="nickname.csv"):
    games = load_json(DB_PATH)
    team_index = load_json(TEAM_INDEX)
    year_index = load_json(YEAR_INDEX)
    conf_index = load_json(CONF_INDEX)
    score_index = load_json(SCORE_INDEX)
    final_index = load_json(FINAL_INDEX)

    # Load conference map
    conf_map = load_conf_map(conf_file)

    # Load nickname map
    nick_map = load_nicknames(nick_csv)

    # Existing game checks
    existing_signatures = {
        (g["date"], g["winner"]["name"], g["loser"]["name"], int(g["winScore"]), int(g["loseScore"]))
        for g in games.values()
    }
    existing_game_ids = set(games.keys())

    new_scores = []  # track newly added unique scores

    with open(input_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:

            date_obj = datetime.strptime(row["Date"], "%b %d %Y")
            date_str = date_obj.strftime("%Y-%m-%d")
            year = str(date_obj.year)

            winner_norm = normalize_team(row["WinningTeam"])
            loser_norm = normalize_team(row["LosingTeam"])
            canonical_winner = winner_norm["name"]
            canonical_loser = loser_norm["name"]

            # Generate or override box score URL
            location = (row.get("VS/@/N") or "").strip().upper()

            # Check for manually supplied URL
            box_url = (
                row.get("BoxUrl")
                or row.get("BoxURL")
                or row.get("https://www.sports-reference.com/cfb/boxscores/{DATE}-{TEAM}.html")
                or ""
            ).strip()

            if not box_url:
                if location == "N":
                    print(
                        f"Skipping neutral-site game on {date_str}: "
                        f"{canonical_winner} vs {canonical_loser} "
                        f"(missing manual URL)"
                    )
                    continue

                # @ means losing team is home
                # Blank or VS means winning team is home
                home_team = canonical_loser if location == "@" else canonical_winner

                box_url = generate_box_url(date_str, home_team)

            display_winner = nick_map.get(canonical_winner, canonical_winner)
            display_loser = nick_map.get(canonical_loser, canonical_loser)

            win_score = int(row["WinningScore"])
            lose_score = int(row["LosingScore"])

            game_id = f"{date_str}-{slug_name_for_id(canonical_winner)}-{slug_name_for_id(canonical_loser)}"
            sig = (date_str, canonical_winner, canonical_loser, win_score, lose_score)
            if sig in existing_signatures or game_id in existing_game_ids:
                continue

            existing_signatures.add(sig)
            existing_game_ids.add(game_id)

            games[game_id] = {
                "week": int(row["Week"]),
                "date": date_str,
                "dayOfWeek": row["DayOfWeek"],
                "winner": {"name": display_winner, "rank": winner_norm["rank"]},
                "loser": {"name": display_loser, "rank": loser_norm["rank"]},
                "winScore": win_score,
                "loseScore": lose_score,
                "location": (row.get("VS/@/N") or "VS"),
                "confWin": conf_map.get(canonical_winner, ""),
                "confLose": conf_map.get(canonical_loser, ""),
                "margin": win_score - lose_score,
                "totalPoints": win_score + lose_score,
                "bowlGame": (row.get("BowlGame") or "").strip()
            }

            # Score index (with URL)
            score_key = f"{win_score}-{lose_score}"
            if score_key not in score_index:
                score_index[score_key] = {
                    "first": {"id": game_id, "boxUrl": box_url},
                    "last": {"id": game_id, "boxUrl": box_url}
                }
                new_scores.append(score_key)
            else:
                cur_first = score_index[score_key]["first"]["id"]
                cur_last = score_index[score_key]["last"]["id"]
                if date_str < games[cur_first]["date"]:
                    score_index[score_key]["first"] = {"id": game_id, "boxUrl": box_url}
                if date_str > games[cur_last]["date"]:
                    score_index[score_key]["last"] = {"id": game_id, "boxUrl": box_url}

            # Final index
            final_index.setdefault(score_key, [])
            if game_id not in final_index[score_key]:
                final_index[score_key].append(game_id)

            # Team index
            for team in (canonical_winner, canonical_loser):
                tid = str(uuid.uuid5(uuid.NAMESPACE_DNS, team))
                if tid not in team_index:
                    team_index[tid] = {"teamName": team, "games": []}
                team_index[tid]["games"].append(game_id)

            # Year index
            year_index.setdefault(year, []).append(game_id)

            # Conference index
            confs_for_game = {conf_map.get(canonical_winner, "Undetermined"),
                              conf_map.get(canonical_loser, "Undetermined")}

            for conf in confs_for_game:
                conf_index.setdefault(conf, []).append(game_id)

    games, team_index, year_index, conf_index, score_index, final_index = sort_indexes(
        games, team_index, year_index, conf_index, score_index, final_index
    )

    save_json(DB_PATH, games)
    save_json(TEAM_INDEX, team_index)
    save_json(YEAR_INDEX, year_index)
    save_json(CONF_INDEX, conf_index)
    save_json(SCORE_INDEX, score_index)
    save_json(FINAL_INDEX, final_index)

    print(f"Imported {len(games)} total games.")
    print(f"Added {len(new_scores)} brand new unique scores to score_index.json.")

    if new_scores:
        print("\nNew unique scores:")
        for score in sorted(new_scores, key=lambda s: tuple(map(int, s.split("-")))):
            print(f"  {score}")
    else:
        print("\nNo new unique scores were added.")

if __name__ == "__main__":
    bulk_import("john.csv", "team_conferences.csv", "nickname.csv")
