import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# VO2 max percentile data for men and women based on provided table
percentile_data_men = {
    20: [55.4, 51.1, 45.4, 41.7, 37.1],
    30: [54.0, 48.3, 44.0, 40.5, 35.9],
    40: [52.5, 46.4, 42.4, 38.5, 33.6],
    50: [48.9, 43.4, 39.2, 35.6, 31.0],
    60: [45.7, 39.5, 35.5, 32.3, 28.1],
    70: [42.1, 36.7, 32.3, 29.4, 25.9]
}

percentile_data_women = {
    20: [49.6, 43.9, 39.5, 36.1, 32.2],
    30: [47.4, 42.4, 37.8, 34.4, 30.9],
    40: [45.3, 39.7, 36.3, 33.0, 29.5],
    50: [41.1, 36.7, 33.0, 30.1, 26.9],
    60: [37.8, 33.0, 30.0, 27.5, 24.4],
    70: [36.7, 30.9, 28.1, 25.9, 23.1]
}

def interpolate_vo2(age, percentiles):
    if age <= 20:
        return percentiles[20]
    elif age >= 70:
        return percentiles[70]
    
    lower_age = (age // 10) * 10
    upper_age = lower_age + 10
    
    lower_values = percentiles[lower_age]
    upper_values = percentiles[upper_age]
    
    interpolated_values = [
        lower + (upper - lower) * (age - lower_age) / (upper_age - lower_age)
        for lower, upper in zip(lower_values, upper_values)
    ]
    
    return interpolated_values

def calculate_exact_percentile(vo2_max, age, sex):
    try:
        percentiles = percentile_data_men if sex == "Male" else percentile_data_women
        interpolated_values = interpolate_vo2(age, percentiles)
        
        # Define the percentile boundaries based on given categories
        percentiles_boundaries = [95, 80, 60, 40, 20]
        
        # Add lower and upper bounds for interpolation
        interpolated_values = [interpolated_values[0] * 1.2] + interpolated_values + [interpolated_values[-1] * 0.8]
        percentiles_boundaries = [100] + percentiles_boundaries + [0]
        
        # Reverse the lists for proper interpolation (higher VO2 max should correspond to higher percentile)
        interpolated_values = interpolated_values[::-1]
        percentiles_boundaries = percentiles_boundaries[::-1]
        
        exact_percentile = np.interp(vo2_max, interpolated_values, percentiles_boundaries)
        
        return exact_percentile
    except Exception as e:
        st.error(f"An error occurred while calculating the percentile: {str(e)}")
        return None

def get_fitness_category(percentile):
    if percentile >= 95:
        return "Superior"
    elif percentile >= 80:
        return "Excellent"
    elif percentile >= 60:
        return "Good"
    elif percentile >= 40:
        return "Fair"
    else:
        return "Poor"

def calculate_vo2_decline(vo2_max, age, decline_rate=0.7):
    ages = np.arange(age, 91)
    vo2_values = vo2_max * (1 - decline_rate / 100) ** (ages - age)
    return ages, vo2_values

def calculate_target_vo2max(age, sex):
    percentiles = percentile_data_men if sex == "Male" else percentile_data_women
    interpolated_values = interpolate_vo2(age, percentiles)
    # The 75th percentile would be between the 80th and 60th percentile values
    target_vo2max = interpolated_values[1] + (interpolated_values[2] - interpolated_values[1]) * 0.25
    return round(target_vo2max, 1)

def suggest_workout(vo2_max, target_vo2max):
    if vo2_max >= target_vo2max:
        return "Maintain: 3-4 HIIT sessions per week, 2-3 moderate cardio sessions"
    elif vo2_max >= target_vo2max * 0.9:
        return "Almost there: 4-5 HIIT sessions per week, 2-3 longer cardio sessions"
    else:
        return "Improvement needed: Start with 2-3 HIIT sessions, gradually increase intensity and duration of cardio workouts"

# Streamlit app
st.title("VO2 Max Analysis Dashboard")

st.markdown("""
This app helps you analyze your VO2 max, which is a measure of your cardiorespiratory fitness.
You can input your VO2 max, age, and sex to find out your exact percentile compared to others in your demographic.
Additionally, the app provides an estimate of how your VO2 max may decline with age and compares it to various activity levels.

### Activity Level Examples
- **Resting (3.5 ml/kg/min)**: Sitting quietly
- **Light activities (10 ml/kg/min)**: Slow walking
- **Moderate activities (20 ml/kg/min)**: Brisk walking, carrying things up a flight of stairs
- **Vigorous activities (35 ml/kg/min)**: Hiking, running
- **High-intensity activities (50 ml/kg/min)**: Intense cycling, swimming
- **Elite endurance athletes (70 ml/kg/min)**: Competitive marathon running, professional cycling
""")

vo2_max = st.number_input("Enter your current VO2 max (ml/kg/min):", min_value=0.0, format="%.1f")
age = st.number_input("Enter your age:", min_value=20, max_value=70, value=39)
sex = st.selectbox("Select your sex:", ("Male", "Female"))

# Additional Streamlit input for decline rate
decline_rate = st.slider("Select your VO2 max decline rate (% per year):", min_value=0.1, max_value=1.5, value=0.7, step=0.1)

if vo2_max and age and sex:
    exact_percentile = calculate_exact_percentile(vo2_max, age, sex)
    target_vo2max = calculate_target_vo2max(age, sex)
    
    if exact_percentile is not None:
        fitness_category = get_fitness_category(exact_percentile)
        st.write(f"Your VO2 max: {vo2_max:.1f} ml/kg/min")
        st.write(f"Percentile for a {age}-year-old {sex}: {exact_percentile:.1f}th percentile")
        st.write(f"Fitness Category: {fitness_category}")
        
        st.write(f"\nTarget VO2 max (75th percentile): {target_vo2max} ml/kg/min")
        
        progress = min(vo2_max / target_vo2max, 1.0)
        st.progress(progress)
        st.write(f"You've achieved {progress*100:.1f}% of the target VO2 max")
        
        if vo2_max >= target_vo2max:
            st.success(f"Great job! Your VO2 max is at or above the 75th percentile for your age and sex.")
            st.write("It's important to maintain this level of fitness. Consider these tips:")
            st.write("- Continue with your current exercise routine")
            st.write("- Focus on maintaining overall health through balanced nutrition")
            st.write("- Include variety in your workouts to prevent plateaus")
        else:
            st.warning(f"Your VO2 max is below the 75th percentile target for your age and sex.")
            st.write("Here are some tips to improve your VO2 max:")
            st.write("1. Incorporate High-Intensity Interval Training (HIIT) into your routine")
            st.write("2. Gradually increase the duration and intensity of your cardio workouts")
            st.write("3. Include a mix of cardio exercises (running, cycling, swimming)")
            st.write("4. Ensure proper rest and recovery between workouts")
            st.write("5. Maintain a balanced diet rich in nutrients to support your training")

        workout_suggestion = suggest_workout(vo2_max, target_vo2max)
        st.write(f"\nPersonalized Workout Suggestion: {workout_suggestion}")
        
        # Calculate VO2 max decline
        ages, vo2_decline = calculate_vo2_decline(vo2_max, age, decline_rate)

        # Activity levels
        activity_levels = {
            "Run 10 MPH on Flat Ground": 60,
            "Jog 6 MPH Up Steep Hill": 50,
            "Carry Heavy Object Upstairs": 45,
            "Jog 6 MPH on Flat Ground": 40,
            "Briskly Climb Stairs": 35,
            "Walk 3 MPH Up Steep Hill": 30,
            "Walk 3 MPH Up Slight Incline": 25,
            "Walk 3 MPH on Flat Ground": 20,
            "Walk 1 MPH on Flat Ground": 10,
            "Resting": 3.5
        }

        try:
            # Plot
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.plot(ages, vo2_decline, label='VO2 Max Decline')

            # Plot activity level lines
            for activity, level in activity_levels.items():
                ax.axhline(y=level, linestyle='--', color='gray', alpha=0.7)
                ax.text(90.5, level, f'{activity}: {level} ml/kg/min', va='center', ha='left', backgroundcolor='white', fontsize=8)

            # Adding labels and title
            ax.set_xlabel('Age')
            ax.set_ylabel('VO2 Max (ml/kg/min)')
            ax.set_title('Estimated VO2 Max Decline with Age and Activity Levels')
            ax.grid(True, alpha=0.3)
            ax.set_ylim(0, max(80, vo2_max * 1.1))

            # Remove legend
            ax.legend().set_visible(False)

            # Display plot
            st.pyplot(fig)
        except Exception as e:
            st.error(f"An error occurred while generating the plot: {str(e)}")

        st.write("\n### Why VO2 Max is Important")
        st.write("VO2 max is a measure of your body's maximum oxygen uptake capacity. It's an indicator of cardiovascular fitness and can predict overall health and longevity. Improving your VO2 max can lead to better endurance, reduced risk of cardiovascular diseases, and improved overall quality of life.")
