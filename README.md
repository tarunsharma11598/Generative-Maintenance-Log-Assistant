# Generative Maintenance Log Assistant

This project was built as part of my learning in applied Artificial Intelligence.  
The goal is to explore how Generative AI and NLP techniques can be used to work with real-world industrial maintenance logs.

## Project Motivation
In many industries, maintenance logs are written in free-text format.  
These logs are challenging to analyze, summarize, or reuse for reporting purposes.  
This project explores the use of AI to convert unstructured maintenance logs into structured summaries and actionable insights.

## What This Project Does
- Takes raw maintenance log data (CSV format)
- Cleans and preprocesses the text data
- Extracts important information using NLP
- Generates structured summaries using a language model
- Displays results using a simple Streamlit interface

## Technologies Used
- Python
- Pandas
- OpenAI API (for text summarization)
- Streamlit (for UI)
- Basic NLP preprocessing

## Folder Structure
app/        - Streamlit application

src/        - Core preprocessing and NLP logic

data/       - Raw and processed maintenance logs 

(Note: The dataset used is synthetically generated to mimic real maintenance logs and is intended for learning and demonstration purposes.)

outputs/    - Generated summaries and structured results

## How to Run
1. Install dependencies:
pip install -r requirements.txt

2. Run the app:
streamlit run app/app.py

