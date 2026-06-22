import os
import json
import importlib.util
import inspect

class SkillManager:
    def __init__(self, skills_dir="skills"):
        self.skills_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), skills_dir)
        self.skills = {}
        self.tool_map = {} # Maps tool_name to the actual python function
        self.load_skills()

    def load_skills(self):
        if not os.path.exists(self.skills_dir):
            os.makedirs(self.skills_dir, exist_ok=True)
            return

        for skill_folder in os.listdir(self.skills_dir):
            skill_path = os.path.join(self.skills_dir, skill_folder)
            if os.path.isdir(skill_path):
                json_path = os.path.join(skill_path, "skill.json")
                if os.path.exists(json_path):
                    try:
                        with open(json_path, "r") as f:
                            skill_meta = json.load(f)
                        
                        self.skills[skill_meta["name"]] = skill_meta
                        
                        # Load handlers
                        handler_path = os.path.join(skill_path, "handler.py")
                        if os.path.exists(handler_path):
                            spec = importlib.util.spec_from_file_location(f"skill_{skill_folder}", handler_path)
                            module = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(module)
                            
                            for tool_name in skill_meta.get("tools", []):
                                if hasattr(module, tool_name):
                                    self.tool_map[tool_name] = getattr(module, tool_name)
                    except Exception as e:
                        print(f"Error loading skill {skill_folder}: {e}")

    def execute_tool(self, tool_name, params):
        if tool_name in self.tool_map:
            func = self.tool_map[tool_name]
            sig = inspect.signature(func)
            
            # Simple parameter mapping (assuming kwargs match)
            # This is a naive implementation for the migration
            try:
                if len(sig.parameters) == 0:
                    return func()
                elif len(sig.parameters) == 1 and isinstance(params, dict) and len(params) == 1:
                    # Just pass the single value if it's not a direct kwarg match
                    return func(list(params.values())[0])
                else:
                    return func(**params)
            except Exception as e:
                return f"Error executing tool {tool_name}: {e}"
        else:
            return f"Tool {tool_name} not found in any loaded skill."

    def get_tools_prompt(self):
        """Generates the prompt addition for available tools dynamically."""
        prompt = ""
        for skill in self.skills.values():
            prompt += f"\n**{skill.get('name', 'Skill')}**\n"
            for tool_desc in skill.get("tool_descriptions", []):
                prompt += f"- {tool_desc}\n"
        return prompt
