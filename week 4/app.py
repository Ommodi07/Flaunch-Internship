from dotenv import load_dotenv
import streamlit as st
import os
import sqlite3

# Load environment variables
load_dotenv()

# Import Google Gemini model (assuming you have this setup)
import google.generativeai as genai

# Configure GenAI Key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to Load Google Gemini Model and provide queries as a response
def get_gemini_response(question, prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt[0], question])
    st.write("1",response.text)
    return response.text

# Function to clean the AI-generated query
def clean_sql_query(query):
    st.write("2",query)
    # Remove markdown backticks and unnecessary words like 'sql' or ''
    query = query.replace("sql", "").replace("", "").strip()
    return query

# Function to retrieve a query from the database
def read_sql_query(sql, db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    
    try:
        cur.execute(sql)
        rows = cur.fetchall()
        conn.commit()
        return rows
    except Exception as e:
        conn.rollback()
        st.error(f"SQL query error: {str(e)}")
        return []
    finally:
        conn.close()

# Streamlit App
st.set_page_config(page_title="SQL Query Retriever App")
st.header("Gemini App to Retrieve and Insert SQL Data")

# Connect to the SQLite database (or create one if it doesn't exist)
conn = sqlite3.connect('student.db')
cur = conn.cursor()

# Create the STUDENT table if it doesn't exist
cur.execute('''
    CREATE TABLE IF NOT EXISTS STUDENT (
        NAME TEXT, 
        CLASS TEXT, 
        SECTION TEXT, 
        MARKS INTEGER
    )
''')
conn.commit()

# Function to insert data into the STUDENT table
def insert_student_data(name, student_class, section, marks):
    cur.execute("INSERT INTO STUDENT (NAME, CLASS, SECTION, MARKS) VALUES (?, ?, ?, ?)", 
                (name, student_class, section, marks))
    conn.commit()

# User inputs for inserting student records
st.subheader("Insert New Student Record")
name = st.text_input("Student Name")
student_class = st.text_input("Class")
section = st.text_input("Section")
marks = st.number_input("Marks", min_value=0, max_value=100, step=1)

if st.button("Add Record"):
    if name and student_class and section and marks:
        insert_student_data(name, student_class, section, marks)
        st.success(f"Record inserted: {name} in {student_class}, Section {section} with Marks {marks}")
    else:
        st.error("Please fill in all fields to add a new record.")

# Display all records
st.subheader("Current Records in Database")
if st.button("Show Records"):
    records = read_sql_query("SELECT * FROM STUDENT", 'student.db')
    if records:
        for row in records:
            st.write(f"Name: {row[0]}, Class: {row[1]}, Section: {row[2]}, Marks: {row[3]}")
    else:
        st.write("No records found")

# SQL Query using Gemini AI
st.subheader("Ask SQL Query")
question = st.text_input("Ask a question to generate SQL", key="query_input")
submit = st.button("Get SQL Query")

if submit:
    # Define your prompt
    prompt = [
        """
        You are an expert in converting English questions to SQL query!
        The SQL database has the name STUDENT and has the following columns - NAME, CLASS, 
        SECTION, MARKS. The SQL query should be valid for SQLite.

        Example 1: How many records are there in the table? -> SELECT COUNT(*) FROM STUDENT;
        Example 2: Show me all students in Data Science class -> SELECT * FROM STUDENT WHERE CLASS='Data Science';

        Respond only with the SQL query, no extra text.
        """
    ]
    # Get the AI response for the SQL query
    generated_sql = get_gemini_response(question, prompt)
    
    # Clean the AI-generated SQL query
    clean_query = clean_sql_query(generated_sql)
    st.write(f"Generated SQL Query: {clean_query}")
    
    # Run the cleaned query
    try:
        query_result = read_sql_query(clean_query, 'student.db')
        
        st.subheader("Query Result:")
        # Check if the result is a single aggregate (e.g., AVG, COUNT)
        if len(query_result) == 1 and len(query_result[0]) == 1:
            # Handle scalar result (e.g., AVG(MARKS) returns one value)
            st.write(f"Result: {query_result[0][0]}")
        elif query_result:
            # Handle normal multi-column, multi-row results
            for row in query_result:
                st.write(f"Name: {row[0]}, Class: {row[1]}, Section: {row[2]}, Marks: {row[3]}")
        else:
            st.write("No results found")
    except Exception as e:
        st.error(f"Error executing query: {str(e)}")

# Close the database connection when done
conn.close()