# Basketball stats converter
# A file I made awhile ago too, it converts raw basketball data from a .csv file into a cleaned lua table file.
# It's one of the main sources I pulled from when building the .txt -> .json converter for this project.

import pandas as pd
from io import StringIO

csv_filename = "nbl_together.csv"
lua_filename = "nbl_players.lua"

# Optional: Map abbreviations to full names if your other scripts require it
team_map = {
    # ABA
    #"ANA": "Anaheim Amigos", "CAR": "Carolina Cougars", "DLC": "Dallas Chaparrals", "DNA": "Denver Nuggets",
    #"DNR": "Denver Rockets", "FLO": "The Floridians", "HSM": "Houston Mavericks", "INA": "Indiana Pacers",
    #"KEN": "Kentucky Colonels", "LAS": "Los Angeles Stars", "MMF": "Miami Floridians", "MMP": "Memphis Pros",
    #"MMS": "Memphis Sounds", "MMT": "Memphis Tams", "MNM": "Minnesota Muskies", "MNP": "Minnesota Pipers",
    #"NJA": "New Jersey Americans", "NOB": "New Orleans Buccaneers", "NYA": "New York Nets", "OAK": "Oakland Oaks",
    #"PTC": "Pittsburgh Condors", "PTP": "Pittsburgh Pipers", "SAA": "San Antonio Spurs", "SDA": "San Diego Conquistadors",
    #"SDS": "San Diego Sails", "SSL": "Spirits of St. Louis", "TEX": "Texas Chaparrals", "UTS": "Utah Stars",
    #"VIR": "Virginia Squires", "WSA": "Washington Capitols",

    # BAA
    #"BLB": "Baltimore Bullets", "BOS": "Boston Celtics", "CHS": "Chicago Stags", "CLR": "Cleveland Rebels", "DTF": "Detriot Falcons",
    #"FTW": "Fort Wayne Pistons", "INJ": "Indianapolis Jets", "MNL": "Minneapolis Lakers", "NYK": "New York Knicks", "PHW": "Philadelphia Warriors",
    #"PIT": "Pittsburgh Ironmen", "PRO": "Providence Steamrollers", "ROC": "Rochester Royals", "STB": "St. Louis Bombers",
    #"TRH": "Toronto Huskies", "WSC": "Washington Capitols",

    # NBL
    "ADP": "Anderson Duffey Packers", "AFN": "Akron Firestone Non-Skids", "AGW": "Akron Goodyear Wingfoots", "BFB": "Buffalo Bison", "CAG": "Chicago American Gears",
    "CAS": "Columbus Athletic Supply", "CAT": "Cleveland Allmen Transfers", "CCB": "Cleveland Chase Brassmen", "CHB": "Chicago Bruins", "CNC": "Cincinnati Comellos", 
    "CSF": "Chicago Studebaker Flyers", "CWH": "Cleveland White Horses", "DNV": "Denver Nuggets", "DTE": "Detroit Eagles", "DTG": "Detroit Gems", "DVK": "Detroit Vagabond Kings", 
    "DYM": "Dayton Metropolitans", "DYR": "Dayton Rens", "FDA": "Flint Dow A.C.'s", "FWG": "Fort Wayne General Electrics", "FWZ": "Fort Wayne Zollner Pistons", "INK": "Indianapolis Kautskys",
    "HCA": "Hammond Ciesar All-Americans", "HCB": "Hammond Calumet Buccaneers", "KGT": "Kankakee Gallagher Trojans", "MNN": "Minneapolis Lakers", "OAS": "Oshkosh All-Stars",
    "PTR": "Pittsburgh Raiders", "PTS": "Pittsburgh Pirates", "RCR": "Rochester Royals", "SHR": "Sheboygan Redskins", "SYN": "Syracuse Nationals", "TCB": "Tri-Cities Blackhawks",
    "TJW": "Toledo Jim White Chevrolets", "TLJ": "Toledo Jeeps", "WRP": "Warren Penns", "WCA": "Whiting Ciesar All-Americans", "WTH": "Waterloo Hawks", "YNB": "Youngstown Bears",

    # WNBA
    #"ATL": "Atlanta Dream", "CHA": "Charlotte Sting", "CHI": "Chicago Sky", "CLE": "Cleveland Rockers",
    #"CON": "Connecticut Sun", "DAL": "Dallas Wings", "DET": "Detriot Shock", "GSV": "Golden State Valkyries",
    #"HOU": "Houston Comets", "IND": "Indiana Fever", "LAS": "Los Angeles Sparks", "LVA": "Las Vegas Aces",
    #"MIA": "Miami Sol", "MIN": "Minnesota Lynx", "NYL": "New York Liberty", "ORL": "Orlando Miracle",
    #"PHO": "Phoenix Mercury", "POR": "Portland Fire", "SAC": "Sacramento Monarchs", "SAS": "San Antonio Silver Stars",
    #"SEA": "Seattle Storm", "TUL": "Tulsa Shock", "UTA": "Utah Starzz", "WAS": "Washington Mystics",

    # NBA
    #"AND": "Anderson Packers", "ATL": "Atlanta Hawks", "BAL": "Baltimore Bullets", "BLB": "Baltimore Bullets", "BOS": "Boston Celtics",
    #"BRK": "Brooklyn Nets", "BUF": "Buffalo Braves", "CAP": "Capital Bullets", "CHA": "Charlotte Bobcats", "CHH": "Charlotte Hornets",
    #"CHI": "Chicago Bulls", "CHO": "Charlotte Hornets", "CHP": "Chicago Packers", "CHS": "Chicago Stags", "CHZ": "Chicago Zephyrs",
    #"CIN": "Cincinnati Royals", "CLE": "Cleveland Cavaliers", "DAL": "Dallas Mavericks", "DEN": "Denver Nuggets", "DET": "Detroit Pistons",
    #"DNN": "Denver Nuggets", "FTW": "Fort Wayne Pistons", "GSW": "Golden State Warriors", "HOU": "Houston Rockets", "IND": "Indiana Pacers",
    #"INO": "Indianapolis Olympians", "KCK": "Kansas City Kings", "KCO": "Kansas City-Omaha Kings", "LAC": "Los Angeles Clippers", "LAL": "Los Angeles Lakers",
    #"MEM": "Memphis Grizzlies", "MIA": "Miami Heat", "MIL": "Milwaukee Bucks", "MIN": "Minnesota Timberwolves", "MLH": "Milwaukee Hawks",
    #"MNL": "Minneapolis Lakers", "NJN": "New Jersey Nets", "NOH": "New Orleans Hornets", "NOJ": "New Orleans Jazz", "NOK": "New Orleans/Oklahoma City Hornets",
    #"NOP": "New Orleans Pelicans", "NYK": "New York Knicks", "NYN": "New York Nets", "OKC": "Oklahoma City Thunder", "ORL": "Orlando Magic",
    #"PHI": "Philadelphia 76ers", "PHO": "Phoenix Suns", "PHW": "Philadelphia Warriors", "POR": "Portland Trail Blazers", "ROC": "Rochester Royals",
    #"SAC": "Sacramento Kings", "SAS": "San Antonio Spurs", "SDC": "San Diego Clippers", "SDR": "San Diego Rockets", "SEA": "Seattle SuperSonics",
    #"SFW": "San Francisco Warriors", "SHE": "Sheboygan Red Skins", "STB": "St. Louis Bombers", "STL": "St. Louis Hawks", "SYR": "Syracuse Nationals",
    #"TOR": "Toronto Raptors", "TRI": "Tri-Cities Blackhawks", "UTA": "Utah Jazz", "VAN": "Vancouver Grizzlies", "WAS": "Washington Wizards",
    #"WAT": "Waterloo Hawks", "WSB": "Washington Bullets", "WSC": "Washington Capitols"
    # The script defaults to the abbreviation if a team isn't listed here
}

# Helper function to return a numeric value or an unquoted 'nil' string
def clean_num(val, precision=1, is_pct=False):
    if pd.isna(val) or str(val).strip() == "" or val == "N/A":
        return "nil"
    try:
        num = float(val)
        if is_pct:
            num = num * 100
        return f"{num:.{precision}f}".rstrip('0').rstrip('.') if precision > 1 else f"{num:.{precision}f}"
    except ValueError:
        return "nil"

try:
    df = pd.read_csv(csv_filename)
    
    with open(lua_filename, "w", encoding="utf-8") as f:
        f.write("Players = {\n")
        
        for _, row in df.iterrows():
            # 1. HANDLE TEXT FIELDS (Empty fields become a Lua string "N/A" or "nil" depending on preference)
            raw_team = str(row.get('team', '')).strip()
            team_name = team_map.get(raw_team, raw_team).replace('"', '\\"')
            
            safe_name = str(row.get('name', '')).replace('"', '\\"').strip()
            safe_pos = str(row.get('position', '')).lower().strip()
            safe_season = str(row.get('season', '')).strip()
            safe_age = str(row.get('Age', '')).strip()
            
            # Text safety check
            pos_val = f'"{safe_pos}"' if safe_pos and safe_pos != "nan" else '"nil"'
            season_val = f'"{safe_season}"' if safe_season and safe_season != "nan" else '"nil"'
            age_val = f'"{safe_age}"' if safe_age and safe_age != "nan" else '"nil"'

            # 2. INT FIELDS
            height_raw = row.get('Height')
            height = int(float(height_raw)) if pd.notna(height_raw) and str(height_raw).strip() != "" else "nil"
            
            games_raw = row.get('games')
            games = int(float(games_raw)) if pd.notna(games_raw) and str(games_raw).strip() != "" else "nil"
            
            # 3. BOX SCORE PER-GAME METRICS
            minutes = clean_num(row.get('minutes'), 1)
            points = clean_num(row.get('points'), 1)
            rebounds = clean_num(row.get('rebounds'), 1)
            offreb = clean_num(row.get('offreb'), 1)
            defreb = clean_num(row.get('defreb'), 1)
            assists = clean_num(row.get('assists'), 1)
            steals = clean_num(row.get('steals'), 1)
            blocks = clean_num(row.get('blocks'), 1)
            turnovers = clean_num(row.get('turnovers'), 1)
            fouls = clean_num(row.get('fouls'), 1)
            fga = clean_num(row.get('fga'), 1)
            t3pta = clean_num(row.get('t3pta'), 1)
            
            # 4. PERCENTAGES (Decimals transformed to % scales)
            fgpercent = clean_num(row.get('fgpercent'), 1, is_pct=True)
            t2ptpercent = clean_num(row.get('t2ptpercent'), 1, is_pct=True)
            t3ptpercent = clean_num(row.get('t3ptpercent'), 1, is_pct=True)
            ftpercent = clean_num(row.get('ftpercent'), 1, is_pct=True)
            
            # 5. ADVANCED METRICS
            mp = clean_num(row.get('MP'), 1)
            ws = clean_num(row.get('WS'), 1)
            ows = clean_num(row.get('OWS'), 1)
            dws = clean_num(row.get('DWS'), 1)
            per = clean_num(row.get('PER'), 2)
            ws = clean_num(row.get('WS'), 2)
            ows = clean_num(row.get('OWS'), 2)
            dws = clean_num(row.get('DWS'), 2)
            ws48 = clean_num(row.get('ws48'), 3)
            offws48 = clean_num(row.get('offws48'), 3)
            defws48 = clean_num(row.get('defws48'), 3)
            pace = clean_num(row.get('pace'), 1)
            poss_pace = clean_num(row.get('poss_pace'), 2)

            # 6. PRINT EXACT ROW
            lua_line = (
                f'    {{name = "{safe_name}", team = "{team_name}", position = "{safe_pos}", '
                f'season = "{safe_season}", height = {height}, age = "{safe_age}", games = {games}, '
                f'minutes = {minutes}, points = {points}, rebounds = {rebounds}, offreb = {offreb}, defreb = {defreb}, '
                f'assists = {assists}, steals = {steals}, blocks = {blocks}, turnovers = {turnovers}, fouls = {fouls}, '
                f'fga = {fga}, fgpercent = {fgpercent}, t2ptpercent = {t2ptpercent}, t3pta = {t3pta}, t3ptpercent = {t3ptpercent}, ftpercent = {ftpercent}, '
                f'per = {per}, ws = {ws}, ows = {ows}, dws = {dws}, ws48 = {ws48}, '
                f'offws48 = {offws48}, defws48 = {defws48}, pace = {pace}, poss_pace = {poss_pace}}},\n'
            )
            f.write(lua_line)
            
        f.write("}\n\nreturn Players\n")
        
    print(f"Success! Converted data with custom nil-checking rules into '{lua_filename}'.")

except FileNotFoundError:
    print(f"Error: Could not find '{csv_filename}'. Ensure it is located in the same directory.")
