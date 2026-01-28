"""
Core view functions: Setup, Dashboard, Fired, Retirement for CFB Mogul V27.6
"""

import streamlit as st
import random
from config import (
    REAL_WORLD_INIT, ALL_TEAMS, TEAMS_DB, SCHEMES, POSITIONS,
    CONFERENCES, COACH_TRAITS
)
from models import (
    BudgetManager, safe_int, sync_team_ratings, helper_format_cash,
    calculate_saban_score, render_trophy_gallery, render_achievements_panel,
    render_dynasty_timeline, render_news_box, add_news, role_rating,
    get_letter_grade, OpponentManager, get_conference, compute_team_needs,
    get_conferences_map, generate_hotspots
)
from engine import (
    engine_generate_coach, engine_generate_roster, engine_generate_schedule,
    engine_play_game_v8
)
from state import sync_team_ratings

# ============================================================================
# SETUP SCREEN
# ============================================================================

def run_setup():
    """Initial setup screen for new dynasty."""
    st.title("🏆 College Football Mogul V27.6")
    st.markdown("### Dynasty Mode")
    
    c1, c2 = st.columns(2)
    name = c1.text_input("AD Name", st.session_state.get("ad_name", "Coach Prime"))
    diff = c2.selectbox("Difficulty", ["Normal", "Hard", "Easy"])
    
    sorted_teams = sorted(REAL_WORLD_INIT.keys()) + sorted([t for t in ALL_TEAMS if t not in REAL_WORLD_INIT])
    team = st.selectbox("Select Team", sorted_teams)
    
    if team in REAL_WORLD_INIT:
        d = REAL_WORLD_INIT[team]
        tier = d["Tier"]
        budget = 25_000_000 if tier == 1 else (15_000_000 if tier == 2 else 5_000_000)
        conf = get_conference(team)
        rival = d.get("Rival", "Rival")
    else:
        tier, budget, conf, rival = 3, 5_000_000, get_conference(team), "Rival"
    
    expect = 10 if tier == 1 else (8 if tier == 2 else (6 if tier == 3 else 4))
    
    st.info(f"**{team}** | Conf: {conf} | Tier: {tier} | Budget: {helper_format_cash(budget)} | Rival: {rival}")
    st.caption(f"Expectation: {expect}+ Wins")
    
    if st.button("Start Dynasty", type="primary"):
        # Explicit Setup Initialization
        st.session_state.year = 2026
        st.session_state.tenure = 1
        st.session_state.job_security = 75
        st.session_state.ad_name = name
        st.session_state.team_name = team
        st.session_state.team_color = TEAMS_DB.get(team, {}).get("color", "#333333")
        st.session_state.team_conf = conf
        st.session_state.team_rival = rival
        st.session_state.home_region = "South"
        st.session_state.school_tier = tier
        st.session_state.expected_wins = expect
        st.session_state.budget = int(budget * (0.75 if diff == "Hard" else 1.25 if diff == "Easy" else 1.0))
        st.session_state.roster = engine_generate_roster(tier, REAL_WORLD_INIT.get(team, {}).get("Talent"))
        st.session_state.prestige = REAL_WORLD_INIT.get(team, {}).get("Prestige", 60)
        st.session_state.team_needs = compute_team_needs(st.session_state.roster, k=3)
        
        st.session_state.staff = {}
        for r in ["HC", "OC", "DC", "Scout"]:
            st.session_state.staff[r] = engine_generate_coach(r, tier)
        
        val = 10 if tier == 1 else 5
        st.session_state.facilities = {"Marketing": val, "Training": val, "Stadium": val}
        
        st.session_state.opponents_db = {}
        for opp in ALL_TEAMS:
            if opp in REAL_WORLD_INIT:
                data = REAL_WORLD_INIT[opp]
                st.session_state.opponents_db[opp] = {
                    "Prestige": data["Prestige"],
                    "OVR": data["Talent"],
                    "Off": random.choice(SCHEMES["Offense"]),
                    "Def": random.choice(SCHEMES["Defense"]),
                    "Coaches": {"OC": random.randint(5, 9), "DC": random.randint(5, 9)},
                    "Stadium": random.randint(5, 11)
                }
            else:
                pres = 85 if opp in CONFERENCES["SEC"] else 65
                ovr = 82 if opp in CONFERENCES["SEC"] else 70
                st.session_state.opponents_db[opp] = {
                    "Prestige": pres,
                    "OVR": ovr,
                    "Off": "Pro Style",
                    "Def": "Man Coverage",
                    "Coaches": {"OC": 5, "DC": 5},
                    "Stadium": random.randint(4, 10)
                }
        
        if "conferences_map" not in st.session_state:
            st.session_state.conferences_map = {k: list(v) for k, v in CONFERENCES.items()}
        if conf not in st.session_state.conferences_map:
            st.session_state.conferences_map[conf] = []
        if team not in st.session_state.conferences_map[conf]:
            st.session_state.conferences_map[conf].append(team)
        
        st.session_state.hotspots = generate_hotspots()
        st.session_state.schedule = engine_generate_schedule(team, conf, rival)
        st.session_state.week_index = 0
        st.session_state.record = {"w": 0, "l": 0}
        st.session_state.season_logs = []
        st.session_state.season_simulated = False
        st.session_state.season_end_ready = False
        st.session_state.offseason_step = 1
        st.session_state.nil_class = []
        st.session_state.hs_total_spend = 0
        st.session_state.hs_shares = {p: 100.0 / len(POSITIONS) for p in POSITIONS}
        st.session_state.hs_spend_by_pos = {p: 0 for p in POSITIONS}
        st.session_state.hs_alloc_by_pos = {p: 0 for p in POSITIONS}
        st.session_state.top8 = []
        st.session_state.top8_resolved = set()
        st.session_state.trophies = []
        st.session_state.conf_revenue_boost_mult = 1.0
        st.session_state.pending_invite = None
        st.session_state.booster_rating = 50
        st.session_state.ai_records = []
        st.session_state.selection_sunday_results = []
        st.session_state.last_postseason_result = "NONE"
        st.session_state.achievements = []
        st.session_state.milestone_log = []
        
        add_news(f"{team} hires {st.session_state.staff['HC']['name']} as HC.")
        st.session_state.game_state = "DASHBOARD"
        st.rerun()

# ============================================================================
# DASHBOARD SCREEN
# ============================================================================

def show_dashboard():
    """Main dashboard screen with tabs for strategy, staff, facilities, season, legacy."""
    from models import apply_conference_move, safe_toast, end_regular_season_and_stay_on_results
    from engine import compute_team_unit_ratings
    
    sync_team_ratings()
    
    # Job security check
    thresh = 0 if st.session_state.tenure <= 2 else 30
    if st.session_state.job_security < thresh:
        st.session_state.game_state = "FIRED"
        st.rerun()

    # V27.6: CONFERENCE INVITE POPUP
    if st.session_state.get("pending_invite"):
        inv = st.session_state.pending_invite
        st.markdown(f"""
        <div style="background: #2c3e50; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; border: 2px solid #f1c40f;">
            <h3>📨 Conference Invite: {inv['to_conf']}</h3>
            <p>The {inv['to_conf']} formally invites {st.session_state.team_name} to join the conference.</p>
            <p><i>"{inv['note']}"</i></p>
            <p><b>Effect:</b> Revenue boost (x{inv['boost_mult']}), Prestige Boost, but Harder Schedule.</p>
        </div>
        """, unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        if c1.button("✅ Accept Invitation", type="primary"):
            apply_conference_move(inv['to_conf'], inv['boost_mult'])
            st.session_state.pending_invite = None
            safe_toast(f"Welcome to the {inv['to_conf']}!")
            st.rerun()
        if c2.button("❌ Decline (Stay)", type="secondary"):
            st.session_state.pending_invite = None
            add_news(f"{st.session_state.team_name} declines invitation to {inv['to_conf']}.")
            st.rerun()

    if st.session_state.season_end_ready:
        st.markdown("""<div style="background:#ffcccb; padding:10px; border-radius:5px; text-align:center; border:2px solid #e00; color: #333;"><h3>🚨 SEASON COMPLETE</h3><p>The regular season is over. Go to results/postseason.</p></div>""", unsafe_allow_html=True)
        if st.button("Resume Postseason / Season End", type="primary"):
            st.session_state.game_state = "SEASON_END"
            st.rerun()

    if st.session_state.revenue_report:
        st.markdown(f"<div class='finance-alert'>💰 FINANCIAL REPORT<br>{st.session_state.revenue_report}</div>", unsafe_allow_html=True)

    sec = st.session_state.job_security
    sec_cls = "security-safe" if sec > 75 else ("security-warm" if sec > 40 else "security-hot")
    st.markdown(f"<div class='security-box'>Year {st.session_state.tenure} | Security: <span class='{sec_cls}'>{sec}%</span></div>", unsafe_allow_html=True)
    st.markdown(f"<div style='background-color: {st.session_state.team_color}; padding: 10px; border-radius: 5px; color: white;'><h2>{st.session_state.team_name}</h2></div>", unsafe_allow_html=True)

    try:
        rv = st.session_state.get("roster", {}) or {}
        raw_roster_val = int(sum(int(v) for v in rv.values()) / max(1, len(rv)))
    except Exception:
        raw_roster_val = 75

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Budget", helper_format_cash(st.session_state.budget))
    ovr_val = safe_int(st.session_state.get("team_rating", 75), 75)
    off_val = safe_int(st.session_state.get("team_off", 75), 75)
    def_val = safe_int(st.session_state.get("team_def", 75), 75)

    c2.metric("OVR", ovr_val)
    c3.metric("OFF", off_val, f"Raw: {raw_roster_val}")
    c4.metric("DEF", def_val)
    saban = calculate_saban_score(st.session_state.career_stats, st.session_state.prestige)
    c5.metric("Legacy", saban, f"Titles: {st.session_state.career_stats['titles']}")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Strategy", "Staff", "Facilities", "Season (Weekly)", "Legacy"])

    with tab1:
        c1, c2 = st.columns(2)
        st.session_state.my_schemes["Off"] = c1.selectbox(
            "Offense",
            SCHEMES["Offense"],
            index=SCHEMES["Offense"].index(st.session_state.my_schemes.get("Off", "Pro Style"))
        )
        st.session_state.my_schemes["Def"] = c2.selectbox(
            "Defense",
            SCHEMES["Defense"],
            index=SCHEMES["Defense"].index(st.session_state.my_schemes.get("Def", "Man Coverage"))
        )
        st.write("Unit Strength")
        for p, v in st.session_state.roster.items():
            lab = f"{p}: {int(v)}" + (" (RENTAL)" if st.session_state.active_transfers.get(p) else "")
            st.progress(min(1.0, v / 100.0), text=lab)
        st.caption("V8 engine uses OFF vs DEF matchups + coaching + scheme + home-field tiers.")

    with tab2:
        from models import generate_ga_coach
        
        st.markdown("### 🧢 Current Staff")
        cols = st.columns(4)
        roles = ["HC", "OC", "DC", "Scout"]
        for i, role in enumerate(roles):
            with cols[i]:
                if role in st.session_state.staff:
                    c = st.session_state.staff[role]
                    rtg = role_rating(c, role)
                    badge_cls = "badge-tier-s" if rtg >= 8 else ("badge-tier-a" if rtg >= 5 else "badge-tier-f")
                    st.markdown(
                        f"<div class='staff-card'>"
                        f"<div class='staff-role'>{role}</div>"
                        f"<div class='staff-name'>{c['name']}</div>"
                        f"<div>"
                        f"<span class='badge {badge_cls}'>RATING: {rtg}</span>"
                        f"<span class='badge badge-trait'>Trait: {c.get('trait','None')}</span>"
                        f"</div>"
                        f"<div class='small-muted'>{helper_format_cash(c.get('salary',0))}</div>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                    if st.button("Fire", key=f"fire_{role}"):
                        add_news(f"{st.session_state.team_name} parts ways with {c['name']} ({role}).")
                        del st.session_state.staff[role]
                        st.rerun()
                else:
                    st.warning(f"{role} VACANT")

        st.divider()
        st.markdown("### 📋 Job Market")
        vacancies = [r for r in roles if r not in st.session_state.staff]
        if vacancies:
            for role in vacancies:
                if role not in st.session_state.candidates:
                    st.session_state.candidates[role] = [
                        engine_generate_coach(role, random.randint(1, 3)) for _ in range(3)
                    ]
                cols = st.columns(3)
                for j, cand in enumerate(st.session_state.candidates[role]):
                    with cols[j]:
                        rr = role_rating(cand, role)
                        vis_rate = f"{rr}" if cand.get("scouted") else f"{get_letter_grade(rr)}"
                        vis_trait = cand.get("trait") if cand.get("scouted") else "???"
                        st.markdown(
                            f"<div class='staff-card'>"
                            f"<div class='staff-name'>{cand['name']}</div>"
                            f"<div class='small-muted'>{cand.get('history','')}</div>"
                            f"<div style='margin:5px 0'>"
                            f"<span class='badge badge-trait'>{role} OVR: {vis_rate}</span>"
                            f"<span class='badge badge-trait'>Trait: {vis_trait}</span>"
                            f"</div>"
                            f"<div style='font-weight:bold'>{helper_format_cash(cand['salary'])}</div>"
                            f"</div>",
                            unsafe_allow_html=True
                        )
                        b1, b2 = st.columns(2)
                        if b1.button("Hire", key=f"hire_{role}_{j}"):
                            if BudgetManager.spend(cand["salary"], f"hire {role}"):
                                st.session_state.staff[role] = cand
                                add_news(f"{st.session_state.team_name} hires {cand['name']} as {role}.")
                                if role in st.session_state.candidates:
                                    del st.session_state.candidates[role]
                                st.rerun()
                        if not cand.get("scouted") and b2.button("Scout ($25k)", key=f"sc_{role}_{j}"):
                            if BudgetManager.spend(25_000, "scout candidate"):
                                cand["scouted"] = True
                                st.rerun()
                if st.button(f"Promote GA (Free)", key=f"ga_{role}"):
                    ga = generate_ga_coach(role)
                    st.session_state.staff[role] = ga
                    add_news(f"{st.session_state.team_name} promotes {ga['name']} to {role}.")
                    if role in st.session_state.candidates:
                        del st.session_state.candidates[role]
                    st.rerun()
        else:
            st.info("No vacancies. Fire someone to shop the market.")

    with tab3:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Marketing", st.session_state.facilities["Marketing"], delta="Rev: +$2M/yr")
            if st.button("Upgrade ($1M)", key="um"):
                if BudgetManager.spend(1_000_000, "upgrade marketing"):
                    st.session_state.facilities["Marketing"] += 1
                    add_news("Marketing upgraded. Boosters are pleased.")
                    st.rerun()
        with c2:
            st.metric("Training", st.session_state.facilities["Training"], delta="OFF/DEF Boost")
            if st.button("Upgrade ($3M)", key="ut"):
                if BudgetManager.spend(3_000_000, "upgrade training"):
                    st.session_state.facilities["Training"] += 1
                    add_news("Training upgraded. Player development improves.")
                    st.rerun()
        with c3:
            st.metric("Stadium", st.session_state.facilities["Stadium"], delta="Home Field (Tiered)")
            st.caption("Tier: <7 none, 7–8 small, 9+ big.")
            if st.button("Upgrade ($10M)", key="us"):
                if BudgetManager.spend(10_000_000, "upgrade stadium"):
                    st.session_state.facilities["Stadium"] += 1
                    st.session_state.prestige = min(99, st.session_state.prestige + 1)
                    add_news("Stadium upgraded. Home field advantage grows.")
                    st.rerun()

    with tab4:
        if len(st.session_state.staff) < 4:
            st.error("Fill Staff First!")
            return
        if not st.session_state.schedule:
            st.session_state.schedule = engine_generate_schedule(
                st.session_state.team_name,
                st.session_state.team_conf,
                st.session_state.team_rival
            )

        st.session_state.game_plan = st.selectbox(
            "Weekly Gameplan",
            ["Conservative", "Normal", "Aggressive"],
            index=["Conservative", "Normal", "Aggressive"].index(st.session_state.game_plan)
        )

        c1, c2 = st.columns(2)
        sched = st.session_state.schedule or []
        sched_len = len(sched)
        
        with c1:
            st.caption("Weeks 1–6")
            for i in range(min(6, sched_len)):
                opp = sched[i]
                played = next((x for x in st.session_state.season_logs if x["Week"] == i + 1), None)
                is_rival = opp == st.session_state.team_rival
                if played:
                    res = "W" if played["Score"].startswith("W") else "L"
                    css = "game-card-win" if res == "W" else "game-card-loss"
                    st.markdown(
                        f"<div class='game-card {css}'>Week {i+1}: {played['Score']} vs {opp}</div>",
                        unsafe_allow_html=True
                    )
                else:
                    css = "game-card-rival" if is_rival else "game-card-pending"
                    st.markdown(
                        f"<div class='game-card {css}'>Week {i+1} vs {opp}</div>",
                        unsafe_allow_html=True
                    )
        
        with c2:
            st.caption("Weeks 7–12")
            for i in range(6, min(12, sched_len)):
                opp = sched[i]
                played = next((x for x in st.session_state.season_logs if x["Week"] == i + 1), None)
                is_rival = opp == st.session_state.team_rival
                if played:
                    res = "W" if played["Score"].startswith("W") else "L"
                    css = "game-card-win" if res == "W" else "game-card-loss"
                    st.markdown(
                        f"<div class='game-card {css}'>Week {i+1}: {played['Score']} vs {opp}</div>",
                        unsafe_allow_html=True
                    )
                else:
                    css = "game-card-rival" if is_rival else "game-card-pending"
                    st.markdown(
                        f"<div class='game-card {css}'>Week {i+1} vs {opp}</div>",
                        unsafe_allow_html=True
                    )

        st.divider()
        render_news_box()
        st.divider()

        if not st.session_state.season_simulated:
            wk = int(st.session_state.get("week_index", 0) or 0)
            if wk >= len(sched):
                end_regular_season_and_stay_on_results()
                st.rerun()

            opp = sched[wk]
            opp_data = OpponentManager.get(opp)
            is_riv = (opp == st.session_state.team_rival)
            opp_off = int(opp_data["OffOVR"])
            opp_def = int(opp_data["DefOVR"])

            st.subheader(f"Next Game: Week {wk+1} vs {opp}")
            my_off_val = off_val
            my_def_val = def_val
            st.caption(f"Matchup: Your OFF {my_off_val} vs Opp DEF {opp_def} | Your DEF {my_def_val} vs Opp OFF {opp_off}")
            st.caption(f"Stadiums: Yours {st.session_state.facilities['Stadium']} | Opp {opp_data.get('Stadium',7)}")

            if is_riv:
                st.warning("RIVALRY WEEK: More chaos, bigger stakes!")

            colA, colB = st.columns(2)

            def play_one_week():
                try:
                    is_home = (wk % 2 == 0)
                    loc_str = "HOME" if is_home else "@AWAY"
                    res = engine_play_game_v8(
                        my_off_val, my_def_val, opp_off, opp_def,
                        st.session_state.staff,
                        st.session_state.my_schemes,
                        {"Off": opp_data.get("Off", "Pro Style"), "Def": opp_data.get("Def", "Man Coverage")},
                        st.session_state.game_plan,
                        opp_data.get("Coaches", {"OC": 5, "DC": 5}),
                        is_home, is_riv,
                        st.session_state.facilities["Stadium"],
                        opp_data.get("Stadium", 7),
                        rng=random.Random()
                    )
                except Exception as e:
                    st.error(f"⚠️ Game simulation error: {str(e)}")
                    st.warning("Generating fallback result to preserve your save...")
                    loc_str = "HOME" if (wk % 2 == 0) else "@AWAY"
                    res = {
                        "result": "L",
                        "score": "0-7",
                        "stats": {
                            "qb_duel": [75, 80],
                            "off_vs_def": [75, 80],
                            "def_vs_off": [75, 80],
                            "staff": ["5/5", "5/5"],
                            "raw_roster": 75
                        },
                        "explain": {
                            "my_off": my_off_val, "my_def": my_def_val,
                            "opp_off": opp_off, "opp_def": opp_def,
                            "my_edge": 0.0, "opp_edge": 0.0,
                            "scheme_my": 0.0, "scheme_opp": 0.0,
                            "coach_my": 0.0, "coach_opp": 0.0,
                            "home_field": 0.0, "plan": st.session_state.game_plan
                        }
                    }
                
                st.session_state.season_logs.append({
                    "Week": wk + 1,
                    "Opponent": opp,
                    "Score": f"{res['result']} {res['score']}",
                    "Stats": res["stats"],
                    "Explain": res["explain"],
                    "OppOVR": int(opp_data.get("OVR", 80)),
                    "Loc": loc_str
                })
                
                if res["result"] == "W":
                    st.session_state.record["w"] += 1
                    st.session_state.career_stats["w"] += 1
                    st.session_state.job_security = min(100, st.session_state.job_security + (5 if is_riv else 2))
                    add_news(f"{st.session_state.team_name} wins Week {wk+1} vs {opp} ({res['score']}).")
                else:
                    st.session_state.record["l"] += 1
                    st.session_state.career_stats["l"] += 1
                    pen = 2 if st.session_state.tenure <= 2 else 5
                    st.session_state.job_security = max(0, st.session_state.job_security - pen)
                    add_news(f"{st.session_state.team_name} loses Week {wk+1} vs {opp} ({res['score']}).")
                
                st.session_state.week_index += 1
                if st.session_state.week_index >= 12:
                    end_regular_season_and_stay_on_results()

            if colA.button("🏈 PLAY WEEK", type="primary"):
                play_one_week()
                st.rerun()

            if colB.button("⏩ SIM REST OF SEASON"):
                while not st.session_state.season_simulated:
                    wk2 = st.session_state.week_index
                    sched2 = st.session_state.schedule or []
                    if wk2 >= len(sched2) or wk2 >= 12:
                        break
                    
                    opp2 = sched2[wk2]
                    opp_data2 = OpponentManager.get(opp2)
                    is_riv2 = (opp2 == st.session_state.team_rival)
                    is_home2 = (wk2 % 2 == 0)
                    loc_str2 = "HOME" if is_home2 else "@AWAY"
                    
                    res2 = engine_play_game_v8(
                        my_off_val, my_def_val,
                        int(opp_data2["OffOVR"]), int(opp_data2["DefOVR"]),
                        st.session_state.staff,
                        st.session_state.my_schemes,
                        {"Off": opp_data2.get("Off", "Pro Style"), "Def": opp_data2.get("Def", "Man Coverage")},
                        st.session_state.game_plan,
                        opp_data2.get("Coaches", {"OC": 5, "DC": 5}),
                        is_home=is_home2, is_rival=is_riv2,
                        my_stadium_level=st.session_state.facilities["Stadium"],
                        opp_stadium_level=opp_data2.get("Stadium", 7),
                        rng=random.Random()
                    )
                    
                    st.session_state.season_logs.append({
                        "Week": wk2 + 1,
                        "Opponent": opp2,
                        "Score": f"{res2['result']} {res2['score']}",
                        "Stats": res2["stats"],
                        "Explain": res2["explain"],
                        "OppOVR": int(opp_data2.get("OVR", 80)),
                        "Loc": loc_str2
                    })
                    
                    if res2["result"] == "W":
                        st.session_state.record["w"] += 1
                        st.session_state.career_stats["w"] += 1
                        st.session_state.job_security = min(100, st.session_state.job_security + (5 if is_riv2 else 2))
                    else:
                        st.session_state.record["l"] += 1
                        st.session_state.career_stats["l"] += 1
                        pen = 2 if st.session_state.tenure <= 2 else 5
                        st.session_state.job_security = max(0, st.session_state.job_security - pen)
                    
                    st.session_state.week_index += 1
                
                end_regular_season_and_stay_on_results()
                st.rerun()

    with tab5:
        st.subheader("🏛️ Trophy Case (Quick View)")
        cs = st.session_state.career_stats
        st.write(f"**Titles:** {cs['titles']}  |  **Bowl W-L:** {cs['bowl_w']}-{cs['bowl_l']}  |  **Career W-L:** {cs['w']}-{cs['l']}")
        st.write(f"**Current Prestige:** {st.session_state.prestige}")
        st.write(f"**Legacy (Saban) Score:** {calculate_saban_score(cs, st.session_state.prestige)}")
        st.divider()
        render_trophy_gallery("🏆 Trophy Case Gallery")
        st.divider()
        render_achievements_panel()
        st.divider()
        render_dynasty_timeline()
        
        # V27.6: RETIREMENT BUTTON IN LEGACY TAB
        st.divider()
        if st.button("🚪 Retire from Coaching", type="secondary"):
            st.session_state.game_state = "RETIREMENT"
            st.rerun()

# ============================================================================
# END STATES
# ============================================================================

def show_fired():
    """Display fired screen."""
    st.error("FIRED! Your tenure has ended.")
    saban = calculate_saban_score(st.session_state.career_stats, st.session_state.prestige)
    st.write(f"Final Legacy (Saban) Score: **{saban}**")
    render_trophy_gallery("🏛️ Your Trophy Gallery (Career)")
    if st.button("Restart Career"):
        st.session_state.clear()
        st.rerun()

def show_retirement():
    """Display retirement screen."""
    st.title("Retirement")
    st.write("Thanks for playing!")
    saban = calculate_saban_score(st.session_state.career_stats, st.session_state.prestige)
    st.write(f"Final Legacy (Saban) Score: **{saban}**")
    render_trophy_gallery("🏛️ Your Trophy Gallery (Career)")
    if st.button("Restart Career"):
        st.session_state.clear()
        st.rerun()
