import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

res = client.chat.completions.create(
    model="llama3-70b-8192",
    messages=[{"role": "user", "content": "Say one benefit of AI in education"}]
)
print(res.choices[0].message.content.strip())
