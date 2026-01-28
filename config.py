"""
Configuration constants and setup for CFB Mogul V27.6
"""

import streamlit as st

# ============================================================================
# VERSION & SAVE STATE
# ============================================================================

STATE_VERSION = 27.6

ALLOWED_SAVE_KEYS = {
    "state_version", "game_state", "year", "budget", "prestige", "job_security",
    "expected_wins", "tenure", "roster", "active_transfers", "stars", "staff",
    "facilities", "history", "record", "opponents_db", "my_schemes",
    "career_stats", "season_logs", "schedule", "season_simulated",
    "hotspots", "candidates", "postseason_data", "revenue_report", "inflation",
    "team_needs", "game_plan", "week_index", "news", "offseason_step",
    "nil_class", "hs_total_spend", "hs_shares", "hs_spend_by_pos",
    "hs_alloc_by_pos", "top8", "top8_resolved", "trophies", "conf_revenue_boost_mult",
    "pending_invite", "season_end_ready", "booster_rating", "ai_records",
    "selection_sunday_results", "ad_name", "team_name", "team_color",
    "team_conf", "team_rival", "home_region", "school_tier",
    "team_off", "team_def", "team_rating", "last_postseason_result",
    "achievements", "milestone_log", "conferences_map",
    "hs_last_results", "recruiting_summary", "postseason_flash",
    "last_known_team_name", "last_known_team_color"
}

# ============================================================================
# STREAMLIT SETUP
# ============================================================================

def setup_page_config():
    """Initialize Streamlit page configuration."""
    try:
        st.set_page_config(
            page_title="CFB Mogul V27.6",
            page_icon="🏈",
            layout="wide"
        )
    except Exception:
        pass

def inject_custom_css():
    """Inject custom CSS styles."""
    st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; font-weight: bold; }
    .game-card, .staff-card, .news-box, .security-box, .trophy-tile, .rank-row, .resume-box { color: #111111 !important; }
    .security-box { background: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #ddd; text-align: center; margin-bottom: 10px; }
    .security-safe { color: #28a745; font-weight: bold; }
    .security-warm { color: #fd7e14; font-weight: bold; }
    .security-hot { color: #dc3545; font-weight: bold; }
    .finance-alert { background-color: #d1e7dd; color: #0f5132 !important; border: 1px solid #badbcc; padding: 15px; border-radius: 8px; margin-bottom: 16px; text-align: center; font-weight: bold; }
    .nil-alert { background-color: #cff4fc; color: #055160 !important; border: 1px solid #b6effb; padding: 18px; border-radius: 8px; margin-bottom: 16px; text-align: center; font-size: 1.1em; font-weight: bold; }
    .game-card { padding: 10px; border-radius: 8px; margin-bottom: 10px; border: 1px solid #ddd; background: white !important; box-shadow: 0 2px 4px rgba(0,0,0,0.05); color: #111111 !important; }
    .game-card-win { border-left: 5px solid #28a745; background: #f8fff9 !important; }
    .game-card-loss { border-left: 5px solid #dc3545; background: #fff8f8 !important; }
    .game-card-pending { border-left: 5px solid #6c757d; background: #f8f9fa !important; }
    .game-card-rival { border-left: 5px solid #fd7e14; background: #fff4e6 !important; }
    .card-header { display: flex; justify-content: space-between; font-weight: bold; border-bottom: 1px solid #eee; padding-bottom: 5px; margin-bottom: 8px; color: #111111 !important; }
    .stat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 0.85em; color: #111111 !important; }
    .stat-row { display: flex; justify-content: space-between; padding: 4px 0; border-bottom: 1px dotted #eee; color: #111111 !important; }
    .staff-card { background: white; border: 1px solid #e0e0e0; border-radius: 10px; padding: 10px; margin-bottom: 10px; }
    .staff-role { font-size: 0.8em; color: #666; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; }
    .staff-name { font-size: 1.1em; font-weight: 800; color: #333; }
    .badge { padding: 2px 6px; border-radius: 4px; font-size: 0.75em; font-weight: bold; margin-right: 5px; display: inline-block;}
    .badge-tier-s { background: #fff3cd; color: #856404; border: 1px solid #ffeeba; }
    .badge-tier-a { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
    .badge-tier-f { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    .badge-trait { background: #e2e3e5; color: #383d41; }
    .recruiting-intel { background-color: #e0f7fa; color: #006064 !important; border-left: 5px solid #006064; padding: 12px; margin-bottom: 10px; border-radius: 4px; }
    .bracket-box { 
        background-color: #2c3e50; 
        color: white !important; 
        padding: 20px; 
        border-radius: 8px; 
        text-align: center; 
        margin-bottom: 10px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .bracket-box h3 { margin: 0; color: #cbd5e0; font-size: 1.1em; text-transform: uppercase; letter-spacing: 2px;}
    .bracket-box h1 { margin: 10px 0; color: white; font-size: 2.5em; font-weight: 900; line-height: 1.1; }
    .bracket-row { display: flex; justify-content: space-between; padding: 6px; border-bottom: 1px solid #444; width: 100%; }
    .news-box { background: #fff; border: 1px solid #eee; border-radius: 10px; padding: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .news-item { padding: 6px 0; border-bottom: 1px solid #f1f1f1; }
    .trophy-tile { background: #fff; border: 1px solid #eee; border-radius: 10px; padding: 10px; }
    .newspaper-head { font-family: 'Georgia', serif; font-size: 2em; text-align: center; border-bottom: 3px double #333; padding-bottom: 10px; margin-bottom: 20px; color: #2c3e50; background: #fdfbf7; padding-top: 20px; }
    .newspaper-sub { font-family: 'Georgia', serif; font-style: italic; text-align: center; color: #555; margin-bottom: 20px; }
    .booster-meter-container { background: #eee; height: 20px; border-radius: 10px; margin-top: 5px; overflow: hidden; border: 1px solid #ccc; }
    .booster-meter-fill { height: 100%; transition: width 0.5s; }
    .rank-row { background: white; padding: 8px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; }
    .rank-row-user { background: #e3f2fd !important; border-left: 5px solid #2196f3; font-weight: bold; }
    .rank-num { width: 40px; font-weight: bold; color: #555; }
    .rank-team { flex-grow: 1; }
    .rank-rec { width: 80px; text-align: right; }
    .resume-box { background-color: #fff; border: 2px solid #333; border-radius: 8px; padding: 15px; margin-bottom: 15px; }
    .resume-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; text-align: center; }
    .resume-label { font-size: 0.8em; text-transform: uppercase; color: #666; letter-spacing: 1px; }
    .resume-val { font-size: 1.2em; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# GAME CONSTANTS
# ============================================================================

POSITIONS = ["QB", "RB", "WR", "OL", "DL", "LB", "DB"]

REGION_STRENGTH = {
    "South": 1.08,
    "Midwest": 1.05,
    "West": 1.05,
    "North": 1.02
}

SCHEMES = {
    "Offense": ["Air Raid", "Smashmouth", "Pro Style"],
    "Defense": ["3-3-5 Cloud", "4-4 Heavy", "Man Coverage"]
}

OFF_COUNTERED_BY = {
    "Air Raid": "3-3-5 Cloud",
    "Smashmouth": "4-4 Heavy",
    "Pro Style": "Man Coverage"
}

DEF_COUNTERS = {
    "3-3-5 Cloud": "Smashmouth",
    "4-4 Heavy": "Air Raid",
    "Man Coverage": "Pro Style"
}

TRAITS = ["❄️ Clutch", "🚀 Speedster", "🧠 General", "😤 Enforcer"]

COACH_TRAITS = {
    "None": "None",
    "Recruiter": "+10% Recruiting",
    "Tactician": "+3 Game Boost",
    "Air Raid": "+2 Scheme",
    "Smashmouth": "+2 Scheme",
    "Pro Style": "+2 Scheme"
}

BOWL_MAPPING = {
    "Elite": ["Rose Bowl", "Sugar Bowl", "Orange Bowl", "Cotton Bowl", "Peach Bowl", "Fiesta Bowl"],
    "High": ["Citrus Bowl", "Alamo Bowl", "Pop-Tarts Bowl", "Gator Bowl"],
    "Mid": ["Liberty Bowl", "Music City Bowl", "Las Vegas Bowl"],
    "Low": ["Gasparilla Bowl", "Boca Raton Bowl", "Potato Bowl"]
}

TROPHY_ICONS = {
    "National Title": "🏆", "CFP": "🏆",
    "Rose Bowl": "🌹", "Sugar Bowl": "🍬", "Orange Bowl": "🍊",
    "Cotton Bowl": "🤠", "Peach Bowl": "🍑", "Fiesta Bowl": "🎉",
    "Citrus Bowl": "🍋", "Alamo Bowl": "🏰", "Pop-Tarts Bowl": "🍪",
    "Gator Bowl": "🐊", "Liberty Bowl": "🗽", "Music City Bowl": "🎸",
    "Las Vegas Bowl": "🎰", "Gasparilla Bowl": "🏴‍☠️", "Boca Raton Bowl": "🌴",
    "Potato Bowl": "🥔", "Bowl Win": "🎳"
}

TEAMS_DB = {
    "Georgia": {"color": "#BA0C2F"}, "Alabama": {"color": "#9E1B32"},
    "Ohio State": {"color": "#BB0000"}, "Michigan": {"color": "#00274C"},
    "Texas": {"color": "#BF5700"}, "Oklahoma": {"color": "#841617"},
    "Oregon": {"color": "#154733"}, "Washington": {"color": "#4B2E83"},
    "Florida St": {"color": "#782F40"}, "Miami": {"color": "#005030"},
    "Penn State": {"color": "#041E42"}, "Notre Dame": {"color": "#0C2340"},
    "LSU": {"color": "#461D7C"}, "Ole Miss": {"color": "#CE1126"},
    "Tennessee": {"color": "#FF8200"}, "Auburn": {"color": "#0C2340"},
    "Indiana": {"color": "#990000"}, "Purdue": {"color": "#CEB888"},
    "Colorado": {"color": "#CFB87C"}, "USC": {"color": "#990000"},
    "Boise State": {"color": "#0033A0"}, "San Jose State": {"color": "#0055A2"},
    "Navy": {"color": "#00205B"}, "Army": {"color": "#D4BF91"},
    "Tulane": {"color": "#006747"}, "App State": {"color": "#FFCC00"},
    "Toledo": {"color": "#15397F"}
}

REAL_WORLD_INIT = {
    "Indiana": {"Prestige": 99, "Talent": 86, "Tier": 1, "Rival": "Purdue"},
    "Ohio State": {"Prestige": 95, "Talent": 94, "Tier": 1, "Rival": "Michigan"},
    "Miami": {"Prestige": 94, "Talent": 89, "Tier": 1, "Rival": "Florida St"},
    "Oregon": {"Prestige": 93, "Talent": 92, "Tier": 1, "Rival": "Washington"},
    "Georgia": {"Prestige": 92, "Talent": 96, "Tier": 1, "Rival": "Florida"},
    "Ole Miss": {"Prestige": 91, "Talent": 88, "Tier": 1, "Rival": "Mississippi St"},
    "Texas Tech": {"Prestige": 90, "Talent": 84, "Tier": 2, "Rival": "Baylor"},
    "Texas A&M": {"Prestige": 89, "Talent": 91, "Tier": 2, "Rival": "Texas"},
    "Alabama": {"Prestige": 85, "Talent": 95, "Tier": 1, "Rival": "Auburn"},
    "Notre Dame": {"Prestige": 92, "Talent": 93, "Tier": 1, "Rival": "USC"},
    "BYU": {"Prestige": 86, "Talent": 82, "Tier": 2, "Rival": "Utah"},
    "Texas": {"Prestige": 84, "Talent": 97, "Tier": 1, "Rival": "Oklahoma"},
    "Oklahoma": {"Prestige": 83, "Talent": 90, "Tier": 2, "Rival": "Texas"},
    "Utah": {"Prestige": 82, "Talent": 85, "Tier": 2, "Rival": "BYU"},
    "Vanderbilt": {"Prestige": 80, "Talent": 78, "Tier": 3, "Rival": "Tennessee"},
    "USC": {"Prestige": 79, "Talent": 89, "Tier": 2, "Rival": "Notre Dame"},
    "Michigan": {"Prestige": 78, "Talent": 91, "Tier": 2, "Rival": "Ohio State"},
    "Penn State": {"Prestige": 77, "Talent": 88, "Tier": 2, "Rival": "Ohio State"},
    "LSU": {"Prestige": 76, "Talent": 92, "Tier": 2, "Rival": "Alabama"},
    "Florida St": {"Prestige": 70, "Talent": 87, "Tier": 3, "Rival": "Miami"},
    "Colorado": {"Prestige": 75, "Talent": 85, "Tier": 2, "Rival": "Nebraska"},
    "Boise State": {"Prestige": 76, "Talent": 82, "Tier": 2, "Rival": "Fresno St"},
    "Tulane": {"Prestige": 74, "Talent": 77, "Tier": 3, "Rival": "LSU"}
}

CONFERENCES = {
    "SEC": ["Georgia", "Alabama", "Texas", "LSU", "Tennessee", "Oklahoma", "Auburn", "Ole Miss", "Florida", "Texas A&M", "Missouri", "Kentucky", "Vanderbilt", "Mississippi St"],
    "Big Ten": ["Ohio State", "Oregon", "Penn State", "Michigan", "USC", "Wisconsin", "Iowa", "Washington", "Nebraska", "Michigan St", "UCLA", "Indiana", "Purdue"],
    "ACC": ["Florida St", "Clemson", "Miami", "Louisville", "UNC", "Virginia Tech", "SMU", "Pitt", "NC State", "Stanford", "Cal"],
    "Big 12": ["Utah", "Kansas State", "Oklahoma St", "Arizona", "Colorado", "Texas Tech", "Baylor", "TCU", "BYU", "West Virginia", "Arizona State"],
    "Pac-12": ["Boise State", "Fresno St", "San Diego St", "Colorado St", "Oregon St", "Wash State"],
    "Indep": ["Notre Dame", "UConn", "UMass"],
    "MAC": ["Toledo", "Miami (OH)", "Ohio", "Northern Illinois", "Western Michigan", "Bowling Green"],
    "G5": ["Tulane", "Memphis", "Navy", "Army", "USF", "Liberty", "App State", "James Madison", "San Jose State", "Wyoming", "Air Force", "Nevada"]
}

ALL_TEAMS = [t for c in CONFERENCES.values() for t in c]

CONF_POWER = {
    "SEC": 1.10,
    "Big Ten": 1.08,
    "ACC": 1.04,
    "Big 12": 1.03,
    "G5": 0.95,
    "Indep": 1.05,
    "Pac-12": 0.98,
    "MAC": 0.90
}
