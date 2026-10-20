from bot.chatbot import Chatbot
from voice.record_voice import record_audio
from voice.speach_to_text import transcribe
from voice.text_to_speach import speak_file


record_audio("user_sound.wav", samplerate=44100)
print("Audio recording is completed.")

transcribe("user_sound.wav")

bot = Chatbot()

# Try the file first
reply = bot.chat_from_file("user_sound.txt")
if reply is not None:
    with open("bot_answer.txt", "w", encoding="utf-8") as f:
        f.write(reply)
    print("Bot answer saved to bot_answer.txt\n")
    speak_file("bot_answer.txt")
else:
    print("user_sound.txt is empty - using the regular chatbot.\n")

# Regular console chatbot
print("Voice Chatbot (type 'quit' to exit, 'clear' to reset)\n")

while True:
    user_input = input("You: ").strip()

    if not user_input:
        continue
    if user_input.lower() == "quit":
        break
    elif user_input.lower() == "clear":
        bot.clear_history()
        print("History cleared.\n")
    elif user_input.lower() == "history":
        if not bot.history:
            print("No history yet.\n")
        else:
            print("\n--- Chat History ---")
            for i, turn in enumerate(bot.history, 1):
                print(f"{i}. You: {turn['user']}")
                print(f"   Bot: {turn['bot']}")
            print("--------------------\n")
    else:
        reply = bot.chat(user_input)
        print(f"Bot: {reply}\n")