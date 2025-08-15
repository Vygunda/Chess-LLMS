♟️ The Chess Paradox: Can LLMs Think or Just Imitate?

This project evaluates Google Gemini 1.5 Flash against the Stockfish chess engine to explore whether Large Language Models (LLMs) demonstrate strategic reasoning or merely imitate patterns. Using 9M+ PGN games, it measures move quality, analyzes deviations from optimal play, and visualizes insights into AI decision-making.

🔍 Features

Data Pipeline: Parses and preprocesses millions of PGN games with python-chess and Pandas

Engine Integration: Interfaces with Stockfish for optimal move evaluation

LLM Analysis: Generates Gemini’s moves via API and compares against engine suggestions

Database Design: Optimized SQLite schema for fast PGN indexing and retrieval

Performance: Efficient batch processing and caching to handle large datasets

Visualization: Move accuracy statistics, blunder rates, and strategic divergence graphs

🛠️ Tech Stack

Languages: Python

Libraries: python-chess, Pandas, SQLite3, Requests

APIs: Google Gemini API, Stockfish UCI

Data: 9M+ PGN games from public chess databases

🚀 How It Works

PGN Processing – Reads and stores games in an indexed SQLite database

Move Evaluation – Queries both Gemini and Stockfish for candidate moves

Comparison Metrics – Calculates accuracy, centipawn loss, and divergence rates

Visualization – Outputs insights into where LLM and engine thinking align or differ

📈 Key Insight

LLMs can mimic strong moves in familiar patterns, but struggle in unseen, highly tactical positions — revealing the limits of purely language-based reasoning in complex strategic games.
