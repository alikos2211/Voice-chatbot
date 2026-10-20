# Voice Chatbot

A voice chatbot that listens to you, answers, and speaks the answer back.

```
microphone → speech-to-text (Whisper) → chatbot (LLM) → text-to-speech (Piper) → speakers
```

The project has two versions of the same flow:

| Version | Folder | Interface                                                                                                                     |
|---|---|-------------------------------------------------------------------------------------------------------------------------------|
| Local | `local_flow/` | FastAPI backend (`api.py`) + HTML/JavaScript frontend (`frontend/index.html`), opened in the browser at http://localhost:8080 |
| Streamlit | `streamlit_flow/` | Streamlit web app (`run.py`), opened in the browser at http://localhost:8501                                                  |

Both versions let you record with the browser microphone or type a message, show the conversation as a chat, and play the spoken answer.
Both use the same three model servers, which run in Docker.

---

Files created while the Streamlit app runs (in the folder you start it from):
`user_sound.wav` (your recording), `user_sound.txt` (transcript),
`bot_answer.txt` (bot reply), `output.wav` (spoken reply).

---

## Services

Both versions need three servers running before you start the app:

| Service | What it does | Port | Docker container |
|---|---|---|---|
| LLM | Generates the chatbot answers (`Qwen/Qwen3.5-0.8B`, OpenAI-compatible API, started by `serve.py`) | 8000 | `inspiring_moore` (image `voicebot_image`) |
| Whisper | Speech-to-text (Speaches, `Systran/faster-whisper-small`) | 8001 | `voice_chatbot-whisper-1` |
| Piper | Text-to-speech | 5000 | `piper-tts` |

> The container names above are the ones on the development machine.
> Check yours with `docker ps -a` and use your own names in the commands below.

---

## 1. Start the Docker containers

Open Docker Desktop and wait until it is running.

### Check what exists

```powershell
docker ps -a
```

Look for the three containers from the table above. `Up` means running, `Exited` means stopped.

### Start existing containers

If the containers already exist but are stopped (for example after a restart):

```powershell
docker start inspiring_moore
docker start voice_chatbot-whisper-1
docker start piper-tts
```

### Create them from docker-compose

If a container does not exist yet, start the services defined in `serve/docker-compose.yml`:

```powershell
cd serve
docker compose up -d
cd ..
```

To start only one service, add its name from the compose file, for example `docker compose up -d whisper`.

### Check that everything is up

```powershell
docker ps
```

You should see these ports published: `8000`, `8001` and `5000`.
The first start can take a few minutes while the models load.

Useful checks:

```powershell
docker logs --tail 30 voice_chatbot-whisper-1    # last log lines of a container
curl.exe http://localhost:8001/health            # Whisper health check
```

### Stop the containers

```powershell
docker stop inspiring_moore voice_chatbot-whisper-1 piper-tts
```

---

## 3. Run the app

### Local version (FastAPI + HTML)

```powershell
cd local_flow
uvicorn api:app --host 0.0.0.0 --port 8080
```

Then open http://localhost:8080 in Chrome, Edge or Firefox.

- **Voice:** press 🎤 Speak, talk, press ⏹ Stop. Your words and the bot's answer appear in the chat and the answer is played.
- **Text:** type a message and press Send.
- **Clear history:** button in the top right.

### Streamlit version

```powershell
cd streamlit_flow
streamlit run run.py
```

Open http://localhost:8501 if the browser does not open by itself.

- **Voice:** click the microphone, speak, click stop. The answer appears in the chat and is played automatically.
- **Text:** type in the box at the bottom.
- **Clear history:** button in the top right.

Run it from inside `streamlit_flow/`, because the app writes its temporary files to the current folder.

---

## Configuration

The services use these defaults. Override them with environment variables (for example in `.env` or docker-compose) if a server runs somewhere else.

| Variable | Default | Used for |
|---|---|---|
| `WHISPER_URL` | `http://localhost:8001/v1/audio/transcriptions` | Speech-to-text server |
| `WHISPER_MODEL` | `Systran/faster-whisper-small` | Whisper model name |
| `LLM_BASE_URL` | `http://localhost:8000/v1` | Chatbot server |
| `LLM_API_KEY` | `not needed` | Chatbot API key |
| `LLM_MODEL` | `Qwen/Qwen3.5-0.8B` | Chatbot model name |
| `PIPER_URL` | `http://localhost:5000/synthesize` | Text-to-speech server |


---
