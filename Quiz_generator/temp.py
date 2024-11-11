import json
import re
import sys
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

GOOGLE_API_KEY = "AIzaSyAC1OLrVT3QooZay0B8x3hPoBYLqcT3oNE"
genai.configure(
    api_key=GOOGLE_API_KEY
    )

def get_transcript(youtube_url):
    try:
        video_id = youtube_url.split('v=')[-1]
        transcript = None
        formatter = TextFormatter()

        # Try to get Hindi transcript first
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['hi'])
            language = 'hi'
        except:
            # If Hindi is not available, fall back to English
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
                language = 'en'
            except:
                print(json.dumps({"error": "Neither Hindi nor English transcript is available."}))
                return None, None

        return formatter.format_transcript(transcript), language
    except Exception as e:
        print(json.dumps({"error": f"Error fetching transcript: {str(e)}"}))
        return None, None

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
    
    model = genai.GenerativeModel(model_name="gemini-1.5-pro")
    response = model.generate_content(prompt)
    return response.text

def parse_content(content):
    summary = ""
    quiz = []
    
    # Extract summary
    summary_match = re.search(r"Summary:(.*?)Quiz:", content, re.DOTALL | re.IGNORECASE)
    if summary_match:
        summary = summary_match.group(1).strip()
    
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
    
    return summary, quiz

def generate_json(youtube_link, num_questions):
    transcript, language = get_transcript(youtube_link)
    if not transcript:
        return None

    content = generate_summary_and_quiz(transcript, num_questions, language)
    summary, quiz = parse_content(content)

    result = {
        "summary": summary,
        "quiz": quiz
    }

    return json.dumps(result, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(json.dumps({"error": "Invalid number of arguments. Usage: python script.py <youtube_link> <num_questions>"}))
        sys.exit(1)

    youtube_link = sys.argv[1]
    try:
        num_questions = int(sys.argv[2])
    except ValueError:
        print(json.dumps({"error": "Number of questions must be an integer"}))
        sys.exit(1)

    json_output = generate_json(youtube_link, num_questions)

    if json_output:
        print(json_output)
    else:
        print(json.dumps({"error": "Failed to generate content"}))