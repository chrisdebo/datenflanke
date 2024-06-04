def get_attributes_summary(position) -> list:
    if position == 'Abwehrspieler':
        a = ['involvement_z', 'progression_z', 'composure_z', 'aerial_threat_z', 'defensive_heading_z',
             'active_defense_z', 'intelligent_defense_z']
    elif position == 'Mittelfeldspieler':
        a = ['involvement_z', 'progression_z', 'passing_quality_z', 'providing_teammates_z', 'box_threat_z',
             'active_defense_z', 'intelligent_defense_z', 'effectiveness_z']
    elif position == 'Angreifer':
        a = ['involvement_z', 'pressing_z', 'run_quality_z', 'finishing_z', 'poaching_z',
             'aerial_threat_z', 'providing_teammates_z', 'hold_up_play_z']
    elif position == 'Flügelspieler':
        a = ['involvement_z', 'passing_quality_z', 'providing_teammates_z', 'dribble_z', 'box_threat_z',
             'finishing_z', 'run_quality_z', 'pressing_z', 'effectiveness_z']
    elif position == 'Außenverteidiger':
        a = ['involvement_z', 'progression_z', 'passing_quality_z', 'providing_teammates_z', 'run_quality_z',
             'active_defense_z', 'intelligent_defense_z']
    return a

def get_attributes_details(attribute) -> list:
    if attribute == 'hold_up_play_z':
        stats = ['link_up_plays_attack_z', 'long_ball_receptions_z', 'aerials_won_z', 'pressure_resistance_z', 'losses_z']
    elif attribute == 'providing_teammates_z':
        stats = ['assists_z', 'xA_z', 'deep_completions_z', 'creative_passes_z', 'second_assists_z', 'vaep_created_with_passes_z']
    elif attribute == 'dribble_z':
        stats = ['dribbles_success_z', 'dribbles_vaep_z', 'xG_created_with_dribbles_z', 'pressure_resistance_z']
    elif attribute == 'involvement_z':
        stats = ['aerials_z', 'defensive_actions_z', 'touches_z', 'vaep_buildup_z']
    elif attribute == 'box_threat_z':
        stats = ['touches_in_box_z', 'box_entries_z', 'goals_z', 'vaep_shots_z', 'penalty_area_receptions_z']
    elif attribute == 'passing_quality_z':
        stats = ['passes_vaep_z', 'crosses_vaep_z', 'passes_into_final_third_z', 'passes_in_final_third_z', 'creative_passes_count_z']
    elif attribute == 'poaching_z':
        stats = ['xG_z', 'vaep_per_shot_z', 'goals_z', 'penalty_area_receptions_z']
    elif attribute == 'run_quality_z':
        stats = ['ball_runs_vaep_z', 'box_entries_z', 'deep_runs_vaep_z', 'carries_offensive_value_z', 'penalty_area_receptions_z']
    elif attribute == 'finishing_z':
        stats = ['goals_z', 'shot_conversion_z', 'goals_vaep_z']
    elif attribute == 'active_defense_z':
        stats = ['defensive_actions_defensive_value_z', 'defensive_actions_z', 'possessions_won_z']
    elif attribute == 'defensive_heading_z':
        stats = ['aerials_won_z', 'aerials_won_defensive_value_z', 'defensive_aerials_won_z', 'defensive_aerials_won_defensive_value_z']
    elif attribute == 'aerial_threat_z':
        stats = ['aerials_won_z', 'aerials_won_offensive_value_z', 'attacking_aerials_won_z', 'attacking_aerials_won_offensive_value_z', 'headed_plays_z']
    elif attribute == 'composure_z':
        stats = ['high_turnovers_z', 'losses_z', 'pressure_resistance_z']
    elif attribute == 'progression_z':
        stats = ['ball_progression_vaep_z', 'passes_into_final_third_vaep_z', 'passes_in_final_third_z']
    elif attribute == 'pressing_z':
        stats = ['defensive_intensity_z', 'counterpressing_recoveries_z', 'counterpressing_interceptions_z']
    elif attribute == 'effectiveness_z':
        stats = ['passes_vaep_z', 'dribbles_vaep_z', 'high_turnovers_z', 'ball_recoveries_z', 'vaep_per_shot_z']
    elif attribute == 'intelligent_defense_z':
        stats = ['ball_recoveries_z', 'counterpressing_recoveries_z', 'interceptions_z']
    else:
        stats = []

    return stats

