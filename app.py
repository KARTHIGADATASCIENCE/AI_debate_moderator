import os
import uuid
import tempfile
import gradio as gr
from dotenv import load_dotenv
from groq import Groq
from gtts import gTTS
import pyglet

# ---------------------------
# 🔐 Load API key from .env
# ---------------------------
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("❌ GROQ_API_KEY not found in .env. Add it like: GROQ_API_KEY=your_key_here")

client = Groq(api_key=GROQ_API_KEY)

# ---------------------------
# 🔊 Voice output (optional)
# ---------------------------
def speak_text(text, lang="en"):
    try:
        tts = gTTS(text=text, lang=lang)
        filename = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}.mp3")
        tts.save(filename)
        music = pyglet.media.load(filename, streaming=False)
        music.play()
        pyglet.app.run()
        os.remove(filename)
    except Exception as e:
        print(f"[TTS Error] {e}")

# ---------------------------
# 🧠 LLaMA-3 Role Response
# ---------------------------
def query_llama(role: str, topic: str, pro: str = "", con: str = "") -> str:
    print(f"[Groq] Calling LLaMA for role: {role}")

    if role == "pro":
        prompt = f"You are a skilled debater arguing in favor of:\n'{topic}'.\nPresent 3 strong logical points."
    elif role == "con":
        prompt = f"You are a skilled debater arguing against:\n'{topic}'.\nPresent 3 strong logical points."
    elif role == "moderator":
        prompt = (
            f"Topic: {topic}\n\n"
            f"✅ Pro Argument:\n{pro}\n\n"
            f"❌ Con Argument:\n{con}\n\n"
            f"As a neutral judge, rate both arguments (1–10) based on logic, clarity, and evidence. Justify your score clearly."
        )
    else:
        raise ValueError("Invalid role!")

    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}]
        )
        print(f"[Groq] ✅ Response OK for {role}")
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ [Groq Error for {role}]: {e}")
        return f"❌ Error: {e}"

# ---------------------------
# 🏛️ Debate Logic
# ---------------------------
def host_debate(topic: str) -> str:
    print(f"\n🧠 Topic Received: {topic}")
    if not topic.strip():
        return "❌ Please enter a valid debate topic."

    try:
        print("→ Generating Pro argument...")
        pro = query_llama("pro", topic)
        print("✅ Pro:\n", pro)

        print("→ Generating Con argument...")
        con = query_llama("con", topic)
        print("✅ Con:\n", con)

        print("→ Moderating...")
        verdict = query_llama("moderator", topic, pro=pro, con=con)
        print("✅ Verdict:\n", verdict)

        # 🗣️ Speak results (optional)
        speak_text(f"Debate Topic: {topic}")
        speak_text(f"Pro says: {pro}")
        speak_text(f"Con says: {con}")
        speak_text(f"Moderator verdict: {verdict}")

        return f"""
## 🏛️ Topic: **{topic}**

---

### ✅ Pro Side  
{pro}

---

### ❌ Con Side  
{con}

---

### ⚖️ Moderator's Verdict  
{verdict}
""".strip()

    except Exception as e:
        print(f"❌ Debate error: {e}")
        return f"❌ Unexpected error: {e}"

# ---------------------------
# 🌐 Gradio Web Interface
# ---------------------------
demo = gr.Interface(
    fn=host_debate,
    inputs=gr.Textbox(label="Enter a Debate Topic", placeholder="e.g. Should AI be regulated?", lines=2),
    outputs="markdown",
    title="🤖 AI Debate Moderator",
    description="Enter any controversial topic. Two LLaMA 3 agents will debate (Pro vs Con), and a moderator will score them based on logic and clarity.",
    allow_flagging="never"
)

if __name__ == "__main__":
    demo.launch()
