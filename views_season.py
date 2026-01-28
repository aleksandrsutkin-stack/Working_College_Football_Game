"""
Season-related view functions: Season End, Selection Sunday, Postseason, Recap for CFB Mogul V27.6
"""

import streamlit as st
import random
import time
from config import TROPHY_ICONS
from models import (
    sync_team_ratings, helper_format_cash, render_news_box, get_season_metrics,
    build_season_summary_dict, calculate_committee_score, safe_int, add_news,
    award_trophy, check_and_award_achievements, BudgetManager, OpponentManager,
    apply_roster_attrition, safe_toast, init_playoff_bracket, get_bowl_name
)
from engine import simulate_ai_regular_season_seeded, engine_play_game_v8

# ============================================================================
# SEASON END
# ============================================================================

def show_season_end():
    """Season end results hub."""
    sync_team_ratings()
    st.title("📊 Season End — Results Hub")
    st.markdown(
        f"<div class='nil-alert'>Regular season complete. Record: <b>{st.session_state.record['w']}-{st.session_state.record['l']}</b> | Budget: <b>{helper_format_cash(st.session_state.budget)}</b></div>",
        unsafe_allow_html=True
    )
    render_news_box()
    
    avg_sos, best_win, worst_loss = get_season_metrics()
    
    st.divider()
    st.subheader("🏆 Your Tournament Resume")
    st.markdown(
        f"<div class='resume-box'>"
        f"<div class='resume-grid'>"
        f"<div><div class='resume-label'>Record</div><div class='resume-val'>{st.session_state.record['w']}-{st.session_state.record['l']}</div></div>"
        f"<div><div class='resume-label'>SOS Score</div><div class='resume-val'>{avg_sos}</div></div>"
        f"<div><div class='resume-label'>Best Win</div><div class='resume-val'>{best_win}</div></div>"
        f"<div><div class='resume-label'>Worst Loss</div><div class='resume-val'>{worst_loss}</div></div>"
        f"</div></div>",
        unsafe_allow_html=True
    )
    
    st.subheader("Game-by-game recap")
    for log in st.session_state.season_logs:
        res = "W" if log["Score"].startswith("W") else "L"
        css = "game-card-win" if res == "W" else "game-card-loss"
        s = log["Stats"]
        st.markdown(
            f"<div class='game-card {css}'>"
            f"<div class='card-header'><span>{log['Score']}</span><span>vs {log['Opponent']} (OVR {log.get('OppOVR','?')})</span></div>"
            f"<div class='stat-grid'>"
            f"<div class='stat-row'><span>🔥 QB Duel</span><span>{s['qb_duel'][0]} vs {s['qb_duel'][1]}</span></div>"
            f"<div class='stat-row'><span>⚔️ OFF vs DEF</span><span>{s['off_vs_def'][0]} vs {s['off_vs_def'][1]}</span></div>"
            f"<div class='stat-row'><span>🛡️ DEF vs OFF</span><span>{s['def_vs_off'][0]} vs {s['def_vs_off'][1]}</span></div>"
            f"<div class='stat-row'><span>🧠 Staff</span><span>{s['staff'][0]} vs {s['staff'][1]}</span></div>"
            f"<div class='stat-row'><span>💪 Raw</span><span>{s['raw_roster']}</span></div>"
            f"</div></div>",
            unsafe_allow_html=True
        )

    st.divider()
    c1, c2 = st.columns(2)
    if c1.button("Enter Selection Sunday (Reveal Rankings) 🏆", type="primary"):
        st.session_state.last_postseason_result = "NONE"
        if not st.session_state.ai_records:
            st.session_state.ai_records = simulate_ai_regular_season_seeded(st.session_state.year)
        
        all_teams = st.session_state.ai_records[:]
        user_score = calculate_committee_score(
            st.session_state.team_name,
            st.session_state.record['w'],
            st.session_state.record['l'],
            st.session_state.team_conf,
            avg_sos
        )
        all_teams.append({
            "Team": st.session_state.team_name,
            "Wins": st.session_state.record['w'],
            "Losses": st.session_state.record['l'],
            "Conf": st.session_state.team_conf,
            "Score": user_score,
            "IsUser": True
        })
        
        for t in all_teams:
            if "Score" not in t:
                t["Score"] = calculate_committee_score(
                    t["Team"], t["Wins"], t["Losses"], t["Conf"], t.get("SOS", 60)
                )
                t["IsUser"] = False
        
        all_teams.sort(key=lambda x: x["Score"], reverse=True)
        st.session_state.selection_sunday_results = all_teams
        st.session_state.game_state = "SELECTION_SUNDAY"
        st.rerun()

# ============================================================================
# SELECTION SUNDAY
# ============================================================================

def show_selection_sunday():
    """Display final committee rankings and postseason path."""
    sync_team_ratings()
    st.title("🏆 SELECTION SUNDAY")
    st.markdown("The Committee has met. Here are the final rankings.")
    
    results = st.session_state.selection_sunday_results
    user_rank = -1
    for i, t in enumerate(results):
        if t.get("IsUser"):
            user_rank = i + 1
            break
    
    if user_rank == -1:  # Fallback
        for i, t in enumerate(results):
            if t.get("Team") == st.session_state.team_name:
                user_rank = i + 1
                t["IsUser"] = True
                break
    
    if user_rank == -1:
        user_rank = 999
    
    if user_rank <= 4:
        st.success(f"✅ Top-4 Seed (#{user_rank}): You receive a First Round BYE.")
    
    st.write("### 📊 Final Committee Rankings")
    for i, t in enumerate(results[:25]):
        rank = i + 1
        is_user = t.get("IsUser", False)
        bg_class = "rank-row-user" if is_user else "rank-row"
        wins = safe_int(t.get("Wins", 0), 0)
        losses = safe_int(t.get("Losses", 0), 0)
        status = "🏆 CFP" if rank <= 12 else ("🎳 BOWL" if wins >= 6 else "❌ OUT")
        st.markdown(
            f"<div class='{bg_class}'>"
            f"<div class='rank-num'>#{rank}</div>"
            f"<div class='rank-team'>{t['Team']} <span style='font-size:0.8em; color:#666'>({t['Conf']})</span></div>"
            f"<div class='rank-rec'><b>{t['Wins']}-{t['Losses']}</b></div>"
            f"<div style='width:80px; text-align:right; font-weight:bold;'>{status}</div>"
            f"</div>",
            unsafe_allow_html=True
        )
    
    st.divider()
    user_wins = st.session_state.record['w']
    
    if user_wins < 6:
        st.error("❌ You did not qualify for a bowl game (less than 6 wins).")
        st.session_state.last_postseason_result = "NO_BOWL"
        if st.button("End Season -> Offseason", type="primary"):
            st.session_state.history.append({
                "Year": st.session_state.year,
                "Record": f"{user_wins}-{st.session_state.record['l']}",
                "Rank": "NR",
                "Bowl": "None",
                "PostseasonResult": "NO_BOWL"
            })
            st.session_state.game_state = "SEASON_RECAP"
            st.rerun()
    elif user_rank <= 12:
        st.success(f"🎉 You made the COLLEGE FOOTBALL PLAYOFF! (Rank #{user_rank})")
        if st.button("Advance to CFP 🏆", type="primary"):
            st.session_state.postseason_data = init_playoff_bracket(user_rank, st.session_state.team_name)
            st.session_state.game_state = "POSTSEASON"
            st.rerun()
    else:
        st.info(f"🎳 You are invited to a Bowl Game! (Rank #{user_rank})")
        if st.button("Accept Bowl Invite", type="primary"):
            bowl = get_bowl_name(user_rank)
            candidates = [t["Team"] for t in results if not t.get("IsUser")]
            opp = random.choice(candidates) if candidates else "FCS West"
            st.session_state.postseason_data = {
                "Type": "BOWL",
                "Bowl": bowl,
                "Rank": user_rank,
                "Opponent": opp,
                "OppData": OpponentManager.get(opp)
            }
            st.session_state.game_state = "POSTSEASON"
            st.rerun()

# ============================================================================
# POSTSEASON
# ============================================================================

def show_postseason():
    """Postseason hub for bowls and CFP."""
    sync_team_ratings()
    st.title("Postseason Hub")
    
    data = st.session_state.postseason_data or {}
    if not data.get("Type"):
        st.warning("Postseason data missing. Returning to Season End.")
        st.session_state.game_state = "SEASON_END"
        st.rerun()

    if data.get("Type") == "BOWL":
        bowl_name = data.get("Bowl", "Bowl Game")
        opponent = data.get("Opponent", "Opponent")
        st.markdown(
            f"<div class='bracket-box'><h3>{bowl_name}</h3><h1>VS {opponent}</h1></div>",
            unsafe_allow_html=True
        )
        
        if st.button("PLAY BOWL GAME 🏈", type="primary"):
            opp_data = OpponentManager.get(opponent)
            res = engine_play_game_v8(
                st.session_state.team_off, st.session_state.team_def,
                int(opp_data.get("OffOVR", 80)), int(opp_data.get("DefOVR", 80)),
                st.session_state.staff,
                st.session_state.my_schemes,
                {"Off": opp_data.get("Off", "Pro Style"), "Def": opp_data.get("Def", "Man Coverage")},
                st.session_state.game_plan,
                opp_data.get("Coaches", {"OC": 5, "DC": 5}),
                is_home=False, is_rival=False,
                my_stadium_level=st.session_state.facilities.get("Stadium", 7),
                opp_stadium_level=opp_data.get("Stadium", 8),
                rng=random.Random()
            )
            st.session_state.postseason_flash = {"res": res, "bowl": bowl_name, "opp": opponent}
            st.rerun()

        if "postseason_flash" in st.session_state:
            flash = st.session_state.postseason_flash
            res = flash["res"]
            css = "game-card-win" if res["result"] == "W" else "game-card-loss"
            s = res["stats"]
            st.markdown(
                f"<div class='game-card {css}'>"
                f"<div class='card-header'><span>{res['score']}</span><span>vs {flash['opp']}</span></div>"
                f"<div class='stat-grid'>"
                f"<div class='stat-row'><span>🔥 QB Duel</span><span>{s['qb_duel'][0]} vs {s['qb_duel'][1]}</span></div>"
                f"<div class='stat-row'><span>⚔️ OFF vs DEF</span><span>{s['off_vs_def'][0]} vs {s['off_vs_def'][1]}</span></div>"
                f"<div class='stat-row'><span>🛡️ DEF vs OFF</span><span>{s['def_vs_off'][0]} vs {s['def_vs_off'][1]}</span></div>"
                f"</div></div>",
                unsafe_allow_html=True
            )
            
            if st.button("Continue to Offseason ->", type="primary"):
                wins = st.session_state.record["w"] + (1 if res["result"] == "W" else 0)
                losses = st.session_state.record["l"] + (1 if res["result"] == "L" else 0)
                
                if res["result"] == "W":
                    st.session_state.last_postseason_result = "BOWL_WIN"
                    BudgetManager.add(2_000_000, "Bowl Win Bonus")
                    st.session_state.career_stats["bowl_w"] += 1
                    add_news(f"{st.session_state.team_name} wins {flash['bowl']}! ({res['score']})")
                    award_trophy(flash['bowl'] if flash['bowl'] in TROPHY_ICONS else "Bowl Win")
                else:
                    st.session_state.last_postseason_result = "BOWL_LOSS"
                    st.session_state.career_stats["bowl_l"] += 1
                    add_news(f"{st.session_state.team_name} falls in {flash['bowl']} ({res['score']})")

                delta = wins - st.session_state.expected_wins
                if delta > 0:
                    BudgetManager.add(delta * 1_000_000, "Performance Bonus")
                elif delta < 0:
                    BudgetManager.spend(abs(delta) * 500_000, "Missed Expectations Penalty")

                st.session_state.history.append({
                    "Year": st.session_state.year,
                    "Record": f"{wins}-{losses}",
                    "Rank": f"#{data.get('Rank','?')}",
                    "Bowl": flash['bowl'],
                    "PostseasonResult": st.session_state.last_postseason_result
                })
                check_and_award_achievements()
                del st.session_state.postseason_flash
                st.session_state.game_state = "SEASON_RECAP"
                st.session_state.offseason_step = 1
                st.rerun()

    elif data.get("Type") == "CFP":
        round_num = int(data.get("Round", 1))
        round_names = ["Opening Rd", "Quarterfinals", "Semifinals", "Championship"]
        label = round_names[round_num - 1] if 1 <= round_num <= 4 else f"Round {round_num}"
        st.header(f"CFP Round: {label}")
        
        st.write("--- Bracket Status ---")
        for m in data.get("Matches", []):
            if m.get("winner"):
                st.markdown(
                    f"<div class='bracket-row'>✅ {m['winner']} advances</div>",
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"<div class='bracket-row'>{m.get('t1','?')} vs {m.get('t2','?')}</div>",
                    unsafe_allow_html=True
                )

        user_match = None
        for m in data.get("Matches", []):
            if m.get("t1") == st.session_state.team_name or m.get("t2") == st.session_state.team_name:
                user_match = m
                break

        if not user_match and data.get("UserAlive") and round_num == 1:
            st.success("✅ FIRST ROUND BYE")
            st.info("You are a Top-4 Seed. You automatically advance to the Quarterfinals.")
            if st.button("Simulate Opening Round & Advance", type="primary"):
                seed_map = st.session_state.postseason_data.get("SeedMap", {})
                next_round_teams = []
                for m in data.get("Matches", []):
                    t1, t2 = m.get("t1"), m.get("t2")
                    o1 = st.session_state.opponents_db.get(t1, {"OVR": 82}).get("OVR", 82)
                    o2 = st.session_state.opponents_db.get(t2, {"OVR": 82}).get("OVR", 82)
                    p = o1 / max(1.0, (o1 + o2))
                    winner = t1 if random.random() < p else t2
                    m["winner"] = winner
                    next_round_teams.append((winner, seed_map.get(winner, 99)))
                
                next_round_teams.sort(key=lambda ts: ts[1], reverse=True)
                winners_only = [ts[0] for ts in next_round_teams]
                seeds = data.get("QF_Seeds", [])
                new_matches = []
                if len(seeds) == 4 and len(winners_only) >= 4:
                    for i in range(4):
                        new_matches.append({"t1": seeds[i], "t2": winners_only[i], "winner": None})
                
                st.session_state.postseason_data["Round"] = 2
                st.session_state.postseason_data["Matches"] = new_matches
                add_news(f"{st.session_state.team_name} advances to Quarterfinals after Bye.")
                st.rerun()

        elif data.get("UserAlive") and user_match:
            opp = user_match["t2"] if user_match["t1"] == st.session_state.team_name else user_match["t1"]
            opp_data = OpponentManager.get(opp)
            st.info(f"Your Matchup: vs {opp} (OVR: {opp_data.get('OVR',88)} | OFF {int(opp_data.get('OffOVR',80))} / DEF {int(opp_data.get('DefOVR',80))})")
            
            if st.button("PLAY PLAYOFF GAME 🏈", type="primary"):
                res = engine_play_game_v8(
                    st.session_state.team_off, st.session_state.team_def,
                    int(opp_data.get("OffOVR", 80)), int(opp_data.get("DefOVR", 80)),
                    st.session_state.staff,
                    st.session_state.my_schemes,
                    {"Off": opp_data.get("Off", "Pro Style"), "Def": opp_data.get("Def", "Man Coverage")},
                    st.session_state.game_plan,
                    opp_data.get("Coaches", {"OC": 5, "DC": 5}),
                    is_home=False, is_rival=False,
                    my_stadium_level=st.session_state.facilities.get("Stadium", 7),
                    opp_stadium_level=opp_data.get("Stadium", 9),
                    rng=random.Random()
                )
                
                next_round_teams = []
                seed_map = st.session_state.postseason_data.get("SeedMap", {})
                
                for m in data.get("Matches", []):
                    if m is user_match:
                        if res["result"] == "W":
                            m["winner"] = st.session_state.team_name
                            next_round_teams.append((st.session_state.team_name, seed_map.get(st.session_state.team_name, 99)))
                            add_news(f"{st.session_state.team_name} advances in the CFP!")
                            safe_toast("VICTORY! Advancing...")
                            BudgetManager.add(5_000_000, "CFP Round Bonus")
                        else:
                            m["winner"] = opp
                            next_round_teams.append((opp, seed_map.get(opp, 99)))
                            st.session_state.postseason_data["UserAlive"] = False
                            st.session_state.last_postseason_result = "CFP_LOSS"
                            add_news(f"{st.session_state.team_name} is eliminated by {opp}.")
                            st.error(f"Eliminated by {opp}")
                    else:
                        t1, t2 = m.get("t1"), m.get("t2")
                        if not t1 or not t2:
                            continue
                        o1 = st.session_state.opponents_db.get(t1, {"OVR": 82}).get("OVR", 82)
                        o2 = st.session_state.opponents_db.get(t2, {"OVR": 82}).get("OVR", 82)
                        p = o1 / max(1.0, (o1 + o2))
                        winner = t1 if random.random() < p else t2
                        m["winner"] = winner
                        next_round_teams.append((winner, seed_map.get(winner, 99)))
                
                time.sleep(0.6)
                
                if st.session_state.postseason_data.get("UserAlive"):
                    if round_num == 4:
                        st.session_state.last_postseason_result = "TITLE"
                        BudgetManager.add(50_000_000, "NATIONAL CHAMPIONSHIP!")
                        st.session_state.career_stats["titles"] += 1
                        st.balloons()
                        st.success("NATIONAL CHAMPIONS!")
                        add_news(f"{st.session_state.team_name} wins the NATIONAL TITLE!")
                        award_trophy("National Title")
                        check_and_award_achievements()
                        st.session_state.history.append({
                            "Year": st.session_state.year,
                            "Record": "CHAMPS",
                            "Rank": "#1",
                            "Bowl": "National Title",
                            "PostseasonResult": "TITLE"
                        })
                        st.session_state.game_state = "SEASON_RECAP"
                        st.session_state.offseason_step = 1
                        st.rerun()
                    else:
                        new_matches = []
                        if round_num == 1:
                            next_round_teams.sort(key=lambda ts: ts[1], reverse=True)
                            winners_only = [ts[0] for ts in next_round_teams]
                            seeds = data.get("QF_Seeds", [])
                            if len(seeds) == 4 and len(winners_only) >= 4:
                                for i in range(4):
                                    new_matches.append({"t1": seeds[i], "t2": winners_only[i], "winner": None})
                        elif round_num == 2:
                            next_round_teams.sort(key=lambda ts: ts[1])
                            if len(next_round_teams) >= 4:
                                new_matches.append({"t1": next_round_teams[0][0], "t2": next_round_teams[3][0], "winner": None})
                                new_matches.append({"t1": next_round_teams[1][0], "t2": next_round_teams[2][0], "winner": None})
                        elif round_num == 3:
                            next_round_teams.sort(key=lambda ts: ts[1])
                            if len(next_round_teams) >= 2:
                                new_matches.append({"t1": next_round_teams[0][0], "t2": next_round_teams[1][0], "winner": None})
                        
                        st.session_state.postseason_data["Round"] = round_num + 1
                        st.session_state.postseason_data["Matches"] = new_matches
                        st.rerun()
                else:
                    st.session_state.history.append({
                        "Year": st.session_state.year,
                        "Record": "Playoff Loss",
                        "Rank": f"#{data.get('Rank','?')}",
                        "Bowl": "CFP",
                        "PostseasonResult": "CFP_LOSS"
                    })
                    st.session_state.game_state = "SEASON_RECAP"
                    st.session_state.offseason_step = 1
                    st.rerun()
        else:
            st.info("You are no longer alive in the bracket.")
            if st.button("Close Season → Recap", type="primary"):
                st.session_state.game_state = "SEASON_RECAP"
                st.session_state.offseason_step = 1
                st.rerun()

# ============================================================================
# SEASON RECAP
# ============================================================================

def show_season_recap():
    """Season recap with booster meter and offseason transition."""
    sync_team_ratings()
    st.title(f"SEASON RECAP: {st.session_state.year}")
    
    summary = build_season_summary_dict()
    result_flag = st.session_state.get("last_postseason_result", "NONE")
    
    if result_flag == "TITLE":
        headline = "DYNASTY! NATIONAL CHAMPIONS!"
        subhead = f"{st.session_state.team_name} shocks the world!"
    elif summary["Delta"] >= 3:
        headline = "Exceeding All Expectations!"
        subhead = "Fans are ecstatic."
    elif summary["Delta"] <= -3:
        headline = "Disaster in the Making?"
        subhead = "Boosters grow restless."
    else:
        headline = "Season Concludes"
        subhead = f"The {st.session_state.team_name} finish with a record of {summary['Record']}."
    
    st.markdown(
        f"<div class='newspaper-head'>{headline}</div><div class='newspaper-sub'>{subhead}</div>",
        unsafe_allow_html=True
    )
    
    st.subheader("📌 Season Summary")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Record", summary["Record"])
    c2.metric("Final Rank", summary["FinalRank"])
    c3.metric("SOS", summary["SOS"])
    c4.metric("Postseason", summary["Postseason"])
    
    st.markdown(
        f"<div class='resume-box'>"
        f"<div class='resume-grid'>"
        f"<div><div class='resume-label'>Best Win</div><div class='resume-val'>{summary['BestWin']}</div></div>"
        f"<div><div class='resume-label'>Worst Loss</div><div class='resume-val'>{summary['WorstLoss']}</div></div>"
        f"<div><div class='resume-label'>Expectation</div><div class='resume-val'>{summary['ExpectedWins']} wins</div></div>"
        f"<div><div class='resume-label'>Result vs Expectation</div><div class='resume-val'>{('+' if summary['Delta']>=0 else '') + str(summary['Delta'])}</div></div>"
        f"</div></div>",
        unsafe_allow_html=True
    )
    
    st.divider()
    
    current_boost = st.session_state.booster_rating
    booster_change = summary["Delta"] * 5
    if result_flag == "TITLE":
        booster_change += 25
    elif result_flag == "BOWL_WIN":
        booster_change += 8
    elif result_flag == "CFP_LOSS":
        booster_change += 12
    elif result_flag == "BOWL_LOSS":
        booster_change += 3
    elif result_flag == "NO_BOWL":
        booster_change -= 8
    
    new_boost = max(0, min(100, current_boost + booster_change))
    meter_color = "#28a745" if new_boost > 60 else ("#dc3545" if new_boost < 40 else "#ffc107")
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("💰 Booster Confidence")
        st.markdown(
            f"<div class='booster-meter-container'>"
            f"<div class='booster-meter-fill' style='width: {new_boost}%; background-color: {meter_color};'></div>"
            f"</div>"
            f"<div style='text-align:center; font-weight:bold; margin-top:5px;'>{new_boost}/100</div>",
            unsafe_allow_html=True
        )
        if new_boost > 80:
            st.success("Boosters are happy! Budget bonus incoming.")
        elif new_boost < 30:
            st.error("Boosters are angry. Job security at risk.")
    
    with c2:
        st.subheader("🏆 Legacy Growth")
        try:
            wins_added = int(st.session_state.record.get("w", 0))
        except:
            wins_added = 0
        added_titles = 1 if result_flag == "TITLE" else 0
        st.write(f"Wins Added: +{wins_added}")
        st.write(f"Titles Added: +{added_titles}")
    
    st.divider()
    
    if st.button("Close the Book on " + str(st.session_state.year) + " -> Go to Offseason", type="primary"):
        st.session_state.booster_rating = new_boost
        if new_boost >= 80:
            BudgetManager.add(3_000_000, "Booster Performance Bonus")
        elif new_boost <= 20:
            st.session_state.job_security -= 10
            safe_toast("Booster Pressure: Security -10")
        
        # V27.6 FIX: Apply attrition/graduation here so players don't stack infinitely
        apply_roster_attrition()
        
        check_and_award_achievements()
        st.session_state.game_state = "OFFSEASON"
        st.session_state.offseason_step = 1
        st.rerun()

    # V27.6: RETIRE BUTTON IN SEASON RECAP
    st.divider()
    if st.button("🚪 Retire from Coaching (End Career)", type="secondary"):
        st.session_state.game_state = "RETIREMENT"
        st.rerun()
