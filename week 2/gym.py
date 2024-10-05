import streamlit as st
from langchain_groq import ChatGroq
import pickle

# Initialize the ChatGroq model
llm = ChatGroq(
    model="llama-3.1-70b-versatile",
    temperature=0,
    groq_api_key="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"
)

model_load = pickle.load(open('trained.sav','rb'))

# Custom CSS for better styling
st.markdown("""
    <style>
        .title {
            color: #4CAF50;
            font-size: 50px;
            font-weight: bold;
        }
        .section-title {
            font-size: 24px;
            margin-top: 30px;
            font-weight: bold;
            color: #48ed07;
        }
        .input-box {
            background-color: #f0f8ff;
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 10px;
        }
        .generate-button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 10px;
            font-size: 18px;
        }
        .gender {
            font-size: 15px;
            font-weight: bold;
            color: #ff0303;
        }
    </style>
""", unsafe_allow_html=True)

# Streamlit UI
st.markdown('<p class="title">🏋️ Training Schedule Maker</p>', unsafe_allow_html=True)
st.write("Provide your height, weight, and training goals to get a personalized gym schedule tailored to your body metrics.")

# Section: Input Fields
st.markdown('<p class="section-title">🔢 Enter Your Information</p>', unsafe_allow_html=True)

#initialization
height = 0
weight =0
sex = ""
interest = ""

# Input fields for height, weight, and interests
with st.container():
    height = st.text_input("Enter your height (in feet)", placeholder="e.g., 5.8", key="height")
    weight = st.text_input("Enter your weight (in kg)", placeholder="e.g., 70", key="weight")
    sex = st.text_input("Enter your Gender ", placeholder="e.g., male or female", key="sex")
    
    # Handling gender input
    if sex.lower() == 'male':
        sex = 1
    elif sex.lower() == 'female':
        sex = 0
    else:
        st.write('<p class="gender">Enter you gender properly(male or female)</p>', unsafe_allow_html=True)

    interest = st.text_input("What are your fitness goals?", placeholder="special notes (none for no interest)", key="interest")

# Ensure height and weight are numeric
try:
    height = float(height)  # Convert height to a float
except ValueError:
    st.write("")

try:
    weight = float(weight)  # Convert weight to a float
except ValueError:
    st.write("")

# Section: Generate Button
st.markdown('<p class="section-title">⚙️ Generate Your Gym Schedule</p>', unsafe_allow_html=True)
# Predicting the weight for the given height and sex
weight_max = 0
weight_min = 0
if isinstance(height, (int, float)) and isinstance(sex, int):
    weight_max = model_load.predict([[height, sex]])
    weight_min = model_load.predict([[height, sex]]) - 10
    
if sex == 0:
        sex = 'female'
elif sex == 1:
        sex = 'male'
# Button to generate the gym schedule
if st.button("Generate Schedule", key="generate", help="Click to get your personalized schedule"):
    if height and weight and interest and sex is not None:
        if weight <= weight_min:
            # Prepare the output string for LLM
            st.write("As per your information generating a schedule for weight gain.")
            output_str = f"Generate the weekly gym schedule with diet plan for a {height} feet tall {sex} with {weight} kg weight and interested in weight gain domain. {interest}"

            # Get the response from the model
            response = llm.invoke(output_str)
        
            # Display the response
            st.markdown('<p class="section-title">🏋️‍♂️ Your Gym Schedule</p>', unsafe_allow_html=True)
            st.success(response.content)
            
        elif weight >= weight_max:
            # Prepare the output string for LLM
            st.write("As per your information generating a schedule for weight loss.")
            output_str = f"Generate the weekly gym schedule with diet plan for a {height} feet tall {sex} with {weight} kg weight and interested in weight loss domain. {interest}"

            # Get the response from the model
            response = llm.invoke(output_str)
        
            # Display the response
            st.markdown('<p class="section-title">🏋️‍♂️ Your Gym Schedule</p>', unsafe_allow_html=True)
            st.success(response.content)

        else:
            # Prepare the output string for LLM
            st.write("As per your information you are completely fit person, Thus generating a schedule for maintain your body.")
            output_str = f"Generate the weekly gym schedule with diet plan for a {height} feet tall {sex} with {weight} kg weight and interested in normal exercise to maintain body. {interest}"

            # Get the response from the model
            response = llm.invoke(output_str)
        
            # Display the response
            st.markdown('<p class="section-title">🏋️‍♂️ Your Gym Schedule</p>', unsafe_allow_html=True)
            st.success(response.content)
    else:
        st.warning("Please fill in all the fields before generating the schedule.")
