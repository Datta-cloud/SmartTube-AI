# utils/ai_helper.py
import requests
import json
import re
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GROK_API_KEY")
GROK_URL = "https://api.groq.com/openai/v1/chat/completions"

def ask_ai(prompt):
    try:
        headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
        body = {
            "model": "openai/gpt-oss-120b",
            "messages": [{"role": "user", "content": prompt}],
            "reasoning_effort": "low",
            "max_completion_tokens": 4096
        }
        response = requests.post(GROK_URL, headers=headers, json=body, timeout=60)
        data = response.json()
        if "choices" not in data:
            print("API error:", data)
            return ""
        content = data["choices"][0]["message"]["content"]
        if not content:
            print("Empty content returned. Raw response:", data)
        return content
    except Exception as e:
        print(f"AI Error: {e}")
        return ""

def ask_ai_chat(messages):
    """Multi-turn chat with message history."""
    try:
        headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
        body = {
            "model": "openai/gpt-oss-120b",
            "messages": messages,
            "reasoning_effort": "low",
            "max_completion_tokens": 2048
        }
        response = requests.post(GROK_URL, headers=headers, json=body, timeout=60)
        data = response.json()
        if "choices" not in data:
            return "Sorry, I couldn't process that."
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {e}"

def get_context(transcript):
    if "::TITLE::" in transcript:
        parts = transcript.replace("YOUTUBE_URL::", "").split("::TITLE::")
        url, title = parts[0], parts[1]
        return f'a YouTube video titled "{title}"', title
    url = transcript.replace("YOUTUBE_URL::", "")
    return f"a YouTube video at {url}", ""

def lang_instruction(language):
    if language == "Hindi":
        return "Respond in Hindi (Devanagari script)."
    elif language == "Marathi":
        return "Respond in Marathi (Devanagari script)."
    return "Respond in English."

def generate_summary(transcript, language="English"):
    context, _ = get_context(transcript)
    prompt = f"""The user is studying from {context}.
{lang_instruction(language)}
Generate a detailed educational summary. Write exactly 8 key points, one per line.
Each must be a complete informative sentence about this specific topic.
No bullet points, numbers, asterisks or markdown — just plain text, one point per line."""
    return ask_ai(prompt)

def generate_quiz(transcript, language="English", difficulty="Medium"):
    context, _ = get_context(transcript)
    diff_guide = {
        "Easy": "simple recall and basic understanding questions",
        "Medium": "application and concept understanding questions",
        "Hard": "analytical, reasoning and advanced concept questions"
    }
    prompt = f"""The user is studying from {context}.
{lang_instruction(language)}
Create exactly 10 {difficulty} level multiple choice questions ({diff_guide[difficulty]}).
Return ONLY a valid JSON array. No markdown, no backticks, no extra text.
[{{"question":"?","options":["A","B","C","D"],"answer":"A","topic":"topic"}}]
Rules: answer must exactly match one of the 4 options. Questions must be {difficulty} level."""
    raw = ask_ai(prompt)
    raw = re.sub(r"```json|```", "", raw).strip()
    match = re.search(r'\[.*\]', raw, re.DOTALL)
    if match: raw = match.group(0)
    try:
        return json.loads(raw)
    except:
        print("Quiz parse failed:", raw[:200])
        return []

def generate_notes(transcript, language="English"):
    context, _ = get_context(transcript)
    prompt = f"""The user is studying from {context}.
{lang_instruction(language)}
Create comprehensive study notes organized in 4 sections.
Return ONLY a valid JSON array. No markdown, no backticks, no extra text.
[{{"section":"Section Heading","points":["Point 1","Point 2","Point 3"]}}]
Each section must have 3-4 detailed, complete sentences as points."""
    raw = ask_ai(prompt)
    raw = re.sub(r"```json|```", "", raw).strip()
    match = re.search(r'\[.*\]', raw, re.DOTALL)
    if match: raw = match.group(0)
    try:
        return json.loads(raw)
    except:
        print("Notes parse failed:", raw[:200])
        return []

def generate_applications(transcript, language="English"):
    context, _ = get_context(transcript)
    prompt = f"""The user is studying from {context}.
{lang_instruction(language)}
Suggest 5 real-world applications of this topic.
Return ONLY a JSON array. No markdown, no backticks.
[{{"title":"Title","description":"2-3 sentence description."}}]"""
    raw = ask_ai(prompt)
    raw = re.sub(r"```json|```", "", raw).strip()
    match = re.search(r'\[.*\]', raw, re.DOTALL)
    if match: raw = match.group(0)
    try:
        return json.loads(raw)
    except:
        return []

def generate_flashcards(transcript, language="English"):
    context, _ = get_context(transcript)
    prompt = f"""The user is studying from {context}.
{lang_instruction(language)}
Create 8 flashcards for quick revision.
Return ONLY a JSON array. No markdown, no backticks.
[{{"question":"Short question?","answer":"Short answer."}}]"""
    raw = ask_ai(prompt)
    raw = re.sub(r"```json|```", "", raw).strip()
    match = re.search(r'\[.*\]', raw, re.DOTALL)
    if match: raw = match.group(0)
    try:
        return json.loads(raw)
    except:
        return []

def chat_with_video(transcript, chat_history, language="English"):
    """Multi-turn chat about the video topic."""
    context, title = get_context(transcript)

    # Build system message
    system_msg = f"""You are a helpful study assistant. The student is studying from {context}.
{lang_instruction(language)}
Answer questions clearly and educationally about this specific topic.
Keep answers concise but informative. Use simple language."""

    # Build messages list for API
    messages = [{"role": "system", "content": system_msg}]
    for msg in chat_history:
        messages.append({"role": msg["role"], "content": msg["content"]})

    return ask_ai_chat(messages)
