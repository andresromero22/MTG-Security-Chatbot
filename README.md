# MTG-Security-Chatbot

This project contains a mining security chatbot implemented in Python. The bot can be used from the terminal or through a simple web interface.

## Configuration

Create a `.env` file in the project root containing your OpenAI API key:

```bash
OPEN_AI_KEY=your-openai-key
```

## Running the CLI bot

```bash
pip install -r requirements.txt
python -m scripts.chatbot
```

## Running the web interface

1. Start the FastAPI backend:
python -m scripts.web_server

The API will be available on `http://localhost:8000`. A production instance is deployed at `https://mtg-security-chatbot.onrender.com`.

2. In another terminal start the Next.js frontend:

```bash
cd frontend
npm install
npm run dev
```

Then open `http://localhost:3000` in your browser or visit the deployed frontend at `https://mtg-security-chatbot.vercel.app/`. The interface uses Kaltire's colours (black `#000000`, orange `#ff6900`, and white).

The frontend is built with Next.js and tRPC as a lightweight example of the Next + tRPC + Prisma + PostgreSQL stack, although no database is required for local usage.
