import time
from pulse_brain.goal_manager import GoalManager, GoalStatus
from pulse_brain.planner import generate_plan
from pulse_brain.memory_manager import memory
from pulse_brain.llm_interface import generate_response, tool_dispatcher
from pulse_config.prompts import tool_system_prompt
from pulse_ear.speech_handler import speak

def execute_autonomous_loop(client, initial_query=None):
    """
    The main autonomous state machine for Pulse.AI
    """
    goal_manager = GoalManager()
    
    if initial_query:
        # Check if it needs planning or just a quick action
        # For simplicity, if query contains "plan", we plan. 
        # In a real system, an LLM router would decide.
        if "/plan" in initial_query.lower() or "plan" in initial_query.lower() and len(initial_query) > 20:
            print("Complex task detected. Entering Planning Mode.")
            main_goal, plan_data = generate_plan(initial_query, client)
            if not main_goal:
                print("Failed to generate plan.")
                return
            print(f"Plan Created: {plan_data.get('goal_title')}")
            for stage in plan_data.get("stages", []):
                print(f" - {stage.get('title')}")
            
            # Start executing goals
            goal_manager.update_status(main_goal.id, GoalStatus.IN_PROGRESS)
            
        else:
            # Simple query, create a single goal
            main_goal = goal_manager.create_goal("User Request", initial_query)
            goal_manager.update_status(main_goal.id, GoalStatus.IN_PROGRESS)

    while True:
        # 1. OBSERVE: Get next active goal
        active_goal = goal_manager.get_active_goal()
        if not active_goal:
            print("No active goals. Waiting for user.")
            break
            
        print(f"\n--- Executing Goal: {active_goal.title} ---")
        
        # 2. UNDERSTAND & SELECT TOOL
        history = memory.load_working_memory()
        history.append({"role": "system", "content": tool_system_prompt})
        history.append({"role": "user", "content": f"Current Goal: {active_goal.description}"})
        
        response_text, _ = generate_response(active_goal.description, history, client, is_tool_check=True)
        
        # 3. ACT
        tool_name, tool_result = tool_dispatcher(response_text, client)
        
        if tool_name:
            if tool_name == "[CHAT]":
                # It's just a chat response
                print(f"PulseAI: {response_text}")
                speak("I have processed that request.")
                goal_manager.update_status(active_goal.id, GoalStatus.COMPLETED)
                memory.save_working_memory(history)
            else:
                print(f"Executed tool: {tool_name}")
                speak(f"Executed {tool_name}")
                
                # 4. VALIDATE & REFLECT (stubbed for now, normally would check tool_result against goal)
                print(f"Result: {tool_result}")
                
                # Update history
                actual_history = memory.load_working_memory()
                actual_history.append({"role": "user", "content": f"Goal: {active_goal.title}"})
                actual_history.append({"role": "assistant", "content": f"Used tool {tool_name}. Result: {tool_result}"})
                memory.save_working_memory(actual_history)
                
                # Mark goal complete
                goal_manager.update_status(active_goal.id, GoalStatus.COMPLETED)
                time.sleep(1)
        else:
            print("Failed to select a tool or invalid format.")
            goal_manager.update_status(active_goal.id, GoalStatus.FAILED)
            break
            
    print("Autonomous loop finished.")
