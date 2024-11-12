import streamlit as st
import re
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from langchain_groq import ChatGroq
import cohere

st.set_page_config(
    page_title="Quiz Generator", 
    page_icon="📝", 
    layout="centered"
)

# Summarize function using Cohere's generate API
def summarize(transcript):
    response = co.generate(
        model='command-r-08-2024',  # Cohere's latest model
        prompt=f"Summarize this transcript in about 300 words: {transcript}",
        max_tokens=400,  # Set the token limit
        temperature=0.3  # Control creativity
    )
    return response.generations[0].text  # Return the summary text

co = cohere.Client(api_key=st.secrets["cohere"]["api_key"])

llm = ChatGroq(
    model="llama-3.1-70b-versatile",
    temperature=0,
    groq_api_key=st.secrets["groq"]["groq_api_key"]
)

# Function to get the transcript of the YouTube video
def get_transcript(youtube_url):
    try:
        video_id = youtube_url.split('v=')[-1]  # Extract video ID from URL
        transcript = None
        formatter = TextFormatter()

        # Try to get the Hindi transcript first
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['hi'])
            language = 'hi'
        except:
            # If Hindi is not available, fall back to English
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
                language = 'en'
            except:
                return None, None

        return formatter.format_transcript(transcript), language
    except Exception as e:
        return None, None

# Function to generate summary and quiz based on the transcript
def generate_summary_and_quiz(transcript, num_questions, language):
    prompt = f"""create a quiz with {num_questions} multiple-choice questions based on the content.
    The quiz questions and options should always be in English, regardless of the transcript language.
    Format the output as follows:
    Summary: [Your summary here]
    Quiz:
    Q1. [Question in English]
    A. [Option A in English]
    B. [Option B in English]
    C. [Option C in English]
    D. [Option D in English]
    Correct Answer: [Correct option letter]

    [Repeat for all questions]

    Transcript: {transcript}
    """
    
    response = llm.invoke(prompt)
    return response.content

# Function to parse the generated content into summary and quiz format
def parse_content(content):
    quiz = []
    
    # Extract quiz questions
    questions = re.findall(r"Q\d+\.(.*?)Correct Answer:", content, re.DOTALL | re.IGNORECASE)
    answers = re.findall(r"Correct Answer:\s*(\w)", content, re.IGNORECASE)
    
    for q, a in zip(questions, answers):
        question_parts = q.strip().split('\n')
        question_text = question_parts[0].strip()
        options = [opt.strip() for opt in question_parts[1:5]]
        
        quiz.append({
            "question": question_text,
            "options": options,
            "answer": options[ord(a.upper()) - ord('A')]
        })
    
    return quiz

# Streamlit app starts here
def main():
    
    # App Title with emojis
    st.markdown("<h1 style='text-align: center; color: #4CAF50;'>🎓 YouTube Transcript Quiz Generator 📝</h1>", unsafe_allow_html=True)

    # Add an image above the link input
    st.image("https://github.com/Ommodi07/Flaunch-Internship/blob/main/Quiz_generator/images/demo.png", caption="Your Image Caption", use_column_width=True)


    # Section Header
    st.markdown("### Create a Quiz from Any YouTube Video Transcript")

    # Get YouTube video URL from the user
    youtube_link = st.text_input("🔗 Enter the YouTube video link:")

    # Slider for number of quiz questions with smooth effect
    st.markdown("📋 Select the number of quiz questions:")
    num_questions = st.slider("",
        min_value=1,
        max_value=20,
        value=5,
        step=1,  # Set to 1 for more precise control
        format="%d",  # Show as integer
        help="Use this slider to select the number of quiz questions."
    )

    # Button to trigger quiz generation
    if st.button("Generate Quiz ✨"):
        if youtube_link:
            # Fetch transcript and generate quiz
            with st.spinner("Fetching the transcript and generating the quiz... Please wait!"):
                transcript, language = get_transcript(youtube_link)
                if transcript:
                    st.success("Transcript fetched successfully!")
                    
                    # Generate summary and quiz
                    transcript = summarize(transcript)
                    content = generate_summary_and_quiz(transcript, num_questions, language)
                    if content:
                        quiz = parse_content(content)

                        # Show the quiz in a more structured format
                        st.subheader("📝 Generated Quiz:")
                        for idx, q in enumerate(quiz):
                            st.markdown(f"### Q{idx + 1}: {q['question']}")
                            st.markdown(f"- {q['options'][0]}")
                            st.markdown(f"- {q['options'][1]}")
                            st.markdown(f"- {q['options'][2]}")
                            st.markdown(f"- {q['options'][3]}")
                            st.markdown(f"**Correct Answer:** {q['answer']}")
                            st.markdown("---")
                    else:
                        st.error("Failed to generate content.")
                else:
                    st.error("Failed to fetch the transcript.")
        else:
            st.warning("Please enter a valid YouTube link.")

    # Footer
    st.markdown(
        """
        <hr style='border:1px solid #f5f5f5'>
        <div style='text-align: center;'>
            <p style='color: grey;'>Developed with 💻 by OM MODI</p>
        </div>
        """, unsafe_allow_html=True
    )

# Execute the main function
if __name__ == "__main__":
    main()
