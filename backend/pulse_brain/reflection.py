import os
from datetime import datetime

class ReflectionEngine:
    def __init__(self, soul_file=".pulse/soul.md"):
        self.soul_file = soul_file
        self._ensure_file()

    def _ensure_file(self):
        os.makedirs(os.path.dirname(self.soul_file), exist_ok=True)
        if not os.path.exists(self.soul_file):
            with open(self.soul_file, "w") as f:
                f.write("# Identity\nYou are Pulse.AI, an advanced, autonomous AI assistant.\n\n# Core Values\n- Privacy first. Keep all data local when possible.\n- Never execute destructive shell commands without explicit human approval.\n\n# User Preferences\n- General: Prefers concise answers.\n\n# Lessons Learned\n")

    def analyze_execution_trace(self, client, goal_title, history_trace, success):
        """
        Takes the trace of a completed or failed goal and extracts lessons.
        """
        print(f"Reflecting on Goal: {goal_title} (Success: {success})")
        
        prompt = f"""
You are the Reflection Engine for Pulse.AI.
Analyze the following execution trace for the goal: "{goal_title}".
Did it succeed? {success}

Trace:
{history_trace}

Identify ONE critical new lesson learned or a persistent user preference discovered.
Respond ONLY with the single sentence to add to the soul.md file. If nothing useful was learned, respond with "NONE".
"""
        try:
            response = client.chat.completions.create(
                model="auto",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            lesson = response.choices[0].message.content.strip()
            
            if lesson and lesson.upper() != "NONE":
                self._append_to_soul(lesson)
                return lesson
        except Exception as e:
            print(f"Error during reflection: {e}")
        return None

    def _append_to_soul(self, lesson):
        try:
            with open(self.soul_file, "a") as f:
                date_str = datetime.now().strftime("%Y-%m-%d")
                f.write(f"\n- [{date_str}]: {lesson}")
            print(f"Appended lesson to soul.md: {lesson}")
        except Exception as e:
            print(f"Error appending to soul.md: {e}")
