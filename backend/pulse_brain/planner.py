import json
from pulse_brain.goal_manager import GoalManager

PLANNER_PROMPT = """
You are the PulseAI Planner Agent. Your job is to break down a high-level task into a sequence of smaller, actionable sub-goals.

You MUST respond ONLY with a valid JSON object representing the plan.

RESPONSE FORMAT:
{
  "goal_title": "Short title of the main goal",
  "goal_description": "Detailed description of the main goal",
  "assumptions": ["Assumption 1", "Assumption 2"],
  "risks": ["Risk 1", "Risk 2"],
  "stages": [
    {
      "title": "Stage 1 title",
      "description": "What to do in stage 1"
    },
    {
      "title": "Stage 2 title",
      "description": "What to do in stage 2"
    }
  ]
}
"""

def generate_plan(task_description, client):
    """
    Calls the LLM to generate a plan for the task, then registers the goals.
    """
    print(f"Generating plan for: {task_description}")
    
    history = [
        {"role": "system", "content": PLANNER_PROMPT},
        {"role": "user", "content": f"Task: {task_description}"}
    ]
    
    try:
        response = client.chat.completions.create(
            model="auto",
            messages=history,
            temperature=0.4
        )
        response_text = response.choices[0].message.content
        
        # Parse JSON
        json_str = response_text.strip()
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0].strip()
        elif "```" in json_str:
            json_str = json_str.split("```")[1].split("```")[0].strip()
            
        plan_data = json.loads(json_str)
        
        print("Plan generated successfully.")
        
        # Register in GoalManager
        gm = GoalManager()
        main_goal = gm.create_goal(
            title=plan_data.get("goal_title", "Main Task"),
            description=plan_data.get("goal_description", task_description)
        )
        
        for stage in plan_data.get("stages", []):
            gm.create_goal(
                title=stage.get("title", "Stage"),
                description=stage.get("description", ""),
                parent_id=main_goal.id
            )
            
        return main_goal, plan_data
        
    except Exception as e:
        print(f"Error generating plan: {e}")
        return None, None
