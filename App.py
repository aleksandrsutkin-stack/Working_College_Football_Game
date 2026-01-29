"""
Build the Program: College Football CEO
VERSION 4.2 (The Ultimate UI Update)

Audit Log:
- MERGE: Combined V3.0 Logic (Hard Mode, Scheduling, Bug Fixes) with V2.9 UI Suite.
- VISUALS: Added Trading Cards (NIL), Interest Meters (Top 8), 3D Trophy Case, and Mount Rushmore.
- STABILITY: Preserved V3.0 Native Column fixes for Game Results to prevent rendering errors.
- DATA: Retained V2.3 Expanded Team Database (65+ teams).
"""

import streamlit as st
import random
import time
import json
import datetime
import math
import pandas as pd
import copy
from typing import List, Dict, Optional, Set

# ============================================================================== 
# CONFIGURATION & CONSTANTS 
# ============================================================================== 

STATE_VERSION = 4.0

class GameState:
    """Game state constants representing different screens/phases of the game."""
    SETUP = "SETUP"
    DASHBOARD = "DASHBOARD"
    SEASON_END = "SEASON_END"
    SELECTION_SUNDAY = "SELECTION_SUNDAY"
    POSTSEASON = "POSTSEASON"
    SEASON_RECAP = "SEASON_RECAP"
    OFFSEASON = "OFFSEASON"
    RECRUITING_WRAP = "RECRUITING_WRAP"
    FIRED = "FIRED"
    RETIREMENT = "RETIREMENT"

class GameConfig:
    """Central configuration class containing all game constants and settings."""
    POSITIONS = ["QB", "RB", "WR", "OL", "DL", "LB", "DB"]
    REGION_STRENGTH = {"South": 1.08, "Midwest": 1.05, "West": 1.05, "North": 1.02}
    
    SCHEMES = {
        "Offense": ["Air Raid", "Smashmouth", "Pro Style"], 
        "Defense": ["3-3-5 Cloud", "4-4 Heavy", "Man Coverage"]
    }
    
    OFF_COUNTERED_BY = {"Air Raid": "3-3-5 Cloud", "Smashmouth": "4-4 Heavy", "Pro Style": "Man Coverage"}
    DEF_COUNTERS = {"3-3-5 Cloud": "Smashmouth", "4-4 Heavy": "Air Raid", "Man Coverage": "Pro Style"}

    TRAITS = ["❄️ Clutch", "🚀 Speedster", "🧠 General", "😤 Enforcer"]
    
    COACH_TRAITS = {
        "None": "None", "Recruiter": "+10% Recruiting", "Tactician": "+3 Game Boost", 
        "Air Raid": "+2 Scheme", "Smashmouth": "+2 Scheme", "Pro Style": "+2 Scheme"
    }

    BOWL_MAPPING = {
        "Elite": ["Rose Bowl", "Sugar Bowl", "Orange Bowl", "Cotton Bowl", "Peach Bowl", "Fiesta Bowl"],
        "High": ["Citrus Bowl", "Alamo Bowl", "Pop-Tarts Bowl", "Gator Bowl"],
        "Mid": ["Liberty Bowl", "Music City Bowl", "Las Vegas Bowl"],
        "Low": ["Gasparilla Bowl", "Boca Raton Bowl", "Potato Bowl"]
    }

    # TROPHY TRACKING CONFIG
    TROPHY_CATEGORIES = {
        "National Championships": {"icon": "🏆", "color": "#FFD700", "empty_text": "Win the CFP", "track_key": "titles"},
        "CFP Appearances": {"icon": "⚔️", "color": "#C0C0C0", "empty_text": "Make the Playoff", "track_key": "cfp_appearances"},
        "Perfect Seasons": {"icon": "💯", "color": "#4CAF50", "empty_text": "Go 12-0", "track_key": "perfect_seasons"},
        "Bowl Victories": {"icon": "🎳", "color": "#2196F3", "empty_text": "Win a Bowl Game", "track_key": "bowl_wins"},
        "10+ Win Seasons": {"icon": "🔟", "color": "#9C27B0", "empty_text": "Win 10+ Games", "track_key": "ten_win_seasons"},
        "Conference Titles": {"icon": "🏅", "color": "#FF9800", "empty_text": "Win Your Conference", "track_key": "conf_titles"},
        "Rivalry Wins": {"icon": "⚡", "color": "#F44336", "empty_text": "Beat Your Rival", "track_key": "rivalry_wins"},
        "Top-5 Finishes": {"icon": "⭐", "color": "#00BCD4", "empty_text": "Finish in Top 5", "track_key": "top5_finishes"},
    }

    TROPHY_ICONS = {k: v["icon"] for k, v in TROPHY_CATEGORIES.items()}
    TROPHY_ICONS["Bowl Win"] = "🎳"
    TROPHY_ICONS["National Title"] = "🏆"

    LEGENDS = [
        {"Name": "Nick Saban", "Titles": 7, "Wins": 292, "Losses": 71, "BowlWins": 19},
        {"Name": "Bear Bryant", "Titles": 6, "Wins": 323, "Losses": 85, "BowlWins": 15},
        {"Name": "Bernie Bierman", "Titles": 5, "Wins": 153, "Losses": 65, "BowlWins": 8},
        {"Name": "Howard Jones", "Titles": 5, "Wins": 194, "Losses": 64, "BowlWins": 9},
        {"Name": "Frank Leahy", "Titles": 4, "Wins": 107, "Losses": 13, "BowlWins": 6},
        {"Name": "John McKay", "Titles": 4, "Wins": 127, "Losses": 40, "BowlWins": 10},
        {"Name": "Urban Meyer", "Titles": 3, "Wins": 187, "Losses": 32, "BowlWins": 12},
        {"Name": "Tom Osborne", "Titles": 3, "Wins": 255, "Losses": 49, "BowlWins": 12},
        {"Name": "Kirby Smart", "Titles": 2, "Wins": 94, "Losses": 16, "BowlWins": 9},
        {"Name": "Dabo Swinney", "Titles": 2, "Wins": 170, "Losses": 43, "BowlWins": 12},
    ]

    TEAMS_DB = {
        "Georgia": {"color": "#BA0C2F"}, "Alabama": {"color": "#9E1B32"}, "Ohio State": {"color": "#BB0000"},
        "Michigan": {"color": "#00274C"}, "Texas": {"color": "#BF5700"}, "Oklahoma": {"color": "#841617"},
        "Oregon": {"color": "#154733"}, "Washington": {"color": "#4B2E83"}, "Florida St": {"color": "#782F40"},
        "Miami": {"color": "#005030"}, "Penn State": {"color": "#041E42"}, "Notre Dame": {"color": "#0C2340"},
        "LSU": {"color": "#461D7C"}, "Ole Miss": {"color": "#CE1126"}, "Tennessee": {"color": "#FF8200"},
        "Auburn": {"color": "#0C2340"}, "Indiana": {"color": "#990000"}, "Purdue": {"color": "#CEB888"},
        "Colorado": {"color": "#CFB87C"}, "USC": {"color": "#990000"}, "Boise State": {"color": "#0033A0"},
        "San Jose State": {"color": "#0055A2"}, "Navy": {"color": "#00205B"}, "Army": {"color": "#D4BF91"},
        "Tulane": {"color": "#006747"}, "App State": {"color": "#FFCC00"}, "Toledo": {"color": "#15397F"}
    }

    # V2.3 HARD MODE RATINGS PRESERVED
    REAL_WORLD_INIT = {
        # TIER 1 (BOSSES) - Base 98
        "Georgia": {"Prestige": 99, "Talent": 98, "Tier": 1, "Rival": "Florida"},
        "Ohio State": {"Prestige": 98, "Talent": 98, "Tier": 1, "Rival": "Michigan"},
        "Texas": {"Prestige": 97, "Talent": 98, "Tier": 1, "Rival": "Oklahoma"},
        "Oregon": {"Prestige": 96, "Talent": 97, "Tier": 1, "Rival": "Washington"},
        
        # TIER 2 (CONTENDERS) - Base 90-95
        "Alabama": {"Prestige": 94, "Talent": 95, "Tier": 1, "Rival": "Auburn"},
        "Notre Dame": {"Prestige": 93, "Talent": 93, "Tier": 1, "Rival": "USC"},
        "Penn State": {"Prestige": 91, "Talent": 92, "Tier": 1, "Rival": "Ohio State"},
        "Michigan": {"Prestige": 90, "Talent": 91, "Tier": 1, "Rival": "Ohio State"},
        "LSU": {"Prestige": 89, "Talent": 91, "Tier": 2, "Rival": "Alabama"},
        "Ole Miss": {"Prestige": 88, "Talent": 90, "Tier": 2, "Rival": "Mississippi St"},
        
        # TIER 3 (TRAPS) - Base 85-90
        "Miami": {"Prestige": 87, "Talent": 89, "Tier": 2, "Rival": "Florida St"},
        "Florida St": {"Prestige": 85, "Talent": 88, "Tier": 2, "Rival": "Miami"},
        "Tennessee": {"Prestige": 86, "Talent": 89, "Tier": 2, "Rival": "Alabama"},
        "Clemson": {"Prestige": 87, "Talent": 88, "Tier": 2, "Rival": "South Carolina"},
        "USC": {"Prestige": 84, "Talent": 88, "Tier": 2, "Rival": "Notre Dame"},
        "Oklahoma": {"Prestige": 85, "Talent": 89, "Tier": 2, "Rival": "Texas"},
        "Texas A&M": {"Prestige": 84, "Talent": 89, "Tier": 2, "Rival": "Texas"},
        "Indiana": {"Prestige": 88, "Talent": 86, "Tier": 2, "Rival": "Purdue"},
        "Utah": {"Prestige": 80, "Talent": 85, "Tier": 2, "Rival": "BYU"},
        "Kansas State": {"Prestige": 79, "Talent": 84, "Tier": 2, "Rival": "Kansas"},
        "Missouri": {"Prestige": 79, "Talent": 85, "Tier": 2, "Rival": "Kansas"},
        "Iowa": {"Prestige": 79, "Talent": 83, "Tier": 2, "Rival": "Iowa State"},
        "SMU": {"Prestige": 78, "Talent": 84, "Tier": 2, "Rival": "TCU"},
        "Boise State": {"Prestige": 78, "Talent": 84, "Tier": 2, "Rival": "Fresno St"},
        "Colorado": {"Prestige": 77, "Talent": 82, "Tier": 2, "Rival": "Nebraska"},
        "Arizona": {"Prestige": 76, "Talent": 83, "Tier": 3, "Rival": "Arizona State"},
        "Virginia Tech": {"Prestige": 75, "Talent": 80, "Tier": 3, "Rival": "UVA"},
        "Tulane": {"Prestige": 74, "Talent": 81, "Tier": 3, "Rival": "LSU"},
        "App State": {"Prestige": 72, "Talent": 79, "Tier": 3, "Rival": "Georgia Southern"},
        "UNLV": {"Prestige": 70, "Talent": 78, "Tier": 3, "Rival": "Nevada"},
    }

    CONFERENCES = {
        "SEC": ["Georgia", "Alabama", "Texas", "LSU", "Tennessee", "Oklahoma", "Auburn", "Ole Miss", "Florida", "Texas A&M", "Missouri", "Kentucky", "Vanderbilt", "Mississippi St", "South Carolina", "[...]"
        "Big Ten": ["Ohio State", "Oregon", "Penn State", "Michigan", "USC", "Wisconsin", "Iowa", "Washington", "Nebraska", "Michigan St", "UCLA", "Indiana", "Purdue", "Minnesota", "Illinois", "Rutger[...]"
        "ACC": ["Florida St", "Clemson", "Miami", "Louisville", "UNC", "Virginia Tech", "SMU", "Pitt", "NC State", "Stanford", "Cal", "Georgia Tech", "Duke", "Syracuse", "Wake Forest", "Boston College[...]"
        "Big 12": ["Utah", "Kansas State", "Oklahoma St", "Arizona", "Colorado", "Texas Tech", "Baylor", "TCU", "BYU", "West Virginia", "Arizona State", "Iowa State", "Kansas", "UCF", "Houston", "Cinc[...]"
        "Pac-12": ["Boise State", "Fresno St", "San Diego St", "Colorado St", "Oregon St", "Wash State"],
        "Indep": ["Notre Dame", "UConn", "UMass"],
        "MAC": ["Toledo", "Miami (OH)", "Ohio", "Northern Illinois", "Western Michigan", "Bowling Green", "Buffalo"],
        "G5": ["Tulane", "Memphis", "Navy", "Army", "USF", "Liberty", "App State", "James Madison", "San Jose State", "Wyoming", "Air Force", "Nevada", "UNLV", "Rice", "North Texas", "UTSA", "Texas St[...]"
    }
    
    ALL_TEAMS = [t for c in CONFERENCES.values() for t in c]

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
    "last_known_team_name", "last_known_team_color", "retention_data", "trophy_stats"
}