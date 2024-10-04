import streamlit as st
import json
import re
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from langchain_groq import ChatGroq

# Groq AI API setup
llm = ChatGroq(
    model="llama-3.1-70b-versatile",
    temperature=0,
    groq_api_key="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"
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
    prompt = f"""Summarize the following transcript in about 200 words.
    Then create a quiz with {num_questions} multiple-choice questions based on the content.
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
    # Customizing the page layout
    st.set_page_config(
        page_title="Quiz Generator", 
        page_icon="📝", 
        layout="centered"
    )

    # App Title with emojis
    st.markdown("<h1 style='text-align: center; color: #4CAF50;'>🎓 YouTube Transcript Quiz Generator 📝</h1>", unsafe_allow_html=True)

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
                    content = generate_summary_and_quiz(transcript, num_questions, language)
                    if content:
                        quiz = parse_content(content)

                        # Display Summary and Quiz
                        st.subheader("📄 Summary:")
                        st.markdown(f"<p style='color: #333; background-color: #F9F9F9; padding: 10px; border-radius: 10px;'>{content[:300]}...</p>", unsafe_allow_html=True)

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
