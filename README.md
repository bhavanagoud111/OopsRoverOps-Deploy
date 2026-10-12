# OopsRoverOps-Deploy

This repository contains a copy of the **RoverOps** mission control simulator that was prepared for deployment. It also contains a small, unrelated Python script.

## Contents

| Path | Description |
|------|-------------|
| `Downloads/RoverOps-Project (1) 2/` | The RoverOps project. It has a FastAPI + LangGraph backend (Planner, Rover, Safety and Reporter agents) and a React + TypeScript + Vite frontend. Both use NASA APIs and stream mission updates over WebSockets. |
| `custom-translator.py` | A command-line script that parses Python code with `ast` and does a simple keyword-based translation to JavaScript, C, C++ or Java. |

## RoverOps

For features, setup steps and the required environment variables, see the project's own docs:

- [`README.md`](Downloads/RoverOps-Project%20(1)%202/README.md)
- [`SETUP_INSTRUCTIONS.md`](Downloads/RoverOps-Project%20(1)%202/SETUP_INSTRUCTIONS.md)

The backend reads its keys from `backend/.env`, starting from `backend/.env.example`. The frontend uses `frontend/.env`, starting from `frontend/.env.example`.

## custom-translator.py

```bash
python3 custom-translator.py
```

The script asks for a target language and one line of Python code, then prints the translated output.
