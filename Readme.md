# 🧠 Self-Healing Playwright Test Suite

A Playwright + pytest test suite that automatically detects and fixes broken CSS selectors at runtime using **Groq AI (LLaMA 3.3)**.

## 🚀 How It Works
1. Test runs with intentionally broken CSS selectors
2. When a selector fails, the AI analyzes the page DOM
3. Groq AI suggests the correct selector
4. Test continues automatically with the healed selector
5. A full HTML report is generated showing all heals

## 📁 Project Structure