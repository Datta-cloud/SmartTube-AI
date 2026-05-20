<<<<<<< HEAD
# 🎓 YouTube AI Study Tool

Turn any YouTube video into a complete study kit using AI!

---

## 📁 Project Structure

```
youtube_ai_project/
│
├── app.py                  ← Main Streamlit app (run this)
├── requirements.txt        ← All libraries needed
├── .env                    ← Your secret API key goes here
│
└── utils/
    ├── __init__.py         ← Makes utils a package
    ├── youtube_helper.py   ← Fetches transcript from YouTube
    └── ai_helper.py        ← Talks to Gemini AI
```

---

## 🚀 How to Run (Step by Step)

### Step 1 — Install Python
Make sure Python 3.9+ is installed.
Check by typing in terminal: `python --version`

### Step 2 — Open VS Code
Open the `youtube_ai_project` folder in VS Code.

### Step 3 — Open Terminal in VS Code
Press: `Ctrl + `` ` (backtick key)

### Step 4 — Install all libraries
```
pip install -r requirements.txt
```

### Step 5 — Get your FREE Gemini API Key
1. Go to: https://aistudio.google.com/app/apikey
2. Sign in with Google
3. Click "Create API Key"
4. Copy the key

### Step 6 — Add API Key to .env file
Open the `.env` file and replace `your_gemini_api_key_here` with your actual key:
```
GEMINI_API_KEY=AIzaSy....your_actual_key_here
```

### Step 7 — Run the app!
```
streamlit run app.py
```

Your browser will open automatically at http://localhost:8501

---

## ✨ Features

| Tab | What it does |
|-----|-------------|
| 📋 Summary | AI-written summary of the video |
| 🧠 Quiz | 10 MCQ questions + score + improvement areas |
| 📒 Notes | Key points in bullet format |
| 💡 Applications | Real-world use cases of the topic |
| 🎯 Flashcards | Quick revision cards (click to reveal answer) |

---

## ⚠️ Note
- Only works on YouTube videos that have **English captions/subtitles** enabled
- Most educational videos (Khan Academy, Kurzgesagt, etc.) work great!
=======
# SmartTube-AI
An AI-driven platform that analyzes YouTube videos and generates summaries, notes, and key insights instantly.
>>>>>>> 00e511b91d631249378d311ae18e62c2493aa2b7
