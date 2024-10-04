from flask import Flask, request, render_template, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from langchain_groq import ChatGroq
import re
import json

# Initialize Flask app
app = Flask(__name__)

# Initialize Groq AI
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

# Function to generate the final JSON output
def generate_json(youtube_link, num_questions):
    transcript, language = get_transcript(youtube_link)
    if not transcript:
        return None

    content = generate_summary_and_quiz(transcript, num_questions, language)
    quiz = parse_content(content)

    result = {
        "quiz": quiz
    }

    return json.dumps(result, indent=2, ensure_ascii=False)

# Route for the home page to enter video URL and number of questions
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle quiz generation
@app.route('/generate_quiz', methods=['POST'])
def generate_quiz():
    youtube_link = request.form['youtube_link']
    num_questions = request.form['num_questions']

    try:
        num_questions = int(num_questions)
    except ValueError:
        return jsonify({"error": "Invalid number of questions. Please enter a valid integer."})

    json_output = generate_json(youtube_link, num_questions)

    if json_output:
        return jsonify({"quiz": json.loads(json_output)})
    else:
        return jsonify({"error": "Failed to generate content"})

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
