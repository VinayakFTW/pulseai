import json
import os
import uuid
from enum import Enum

class GoalStatus(Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Goal:
    def __init__(self, title, description, priority="medium", parent_id=None, goal_id=None, status=GoalStatus.PENDING.value, child_ids=None, checkpoints=None):
        self.id = goal_id or f"goal_{uuid.uuid4().hex[:8]}"
        self.title = title
        self.description = description
        self.priority = priority
        self.parent_id = parent_id
        self.status = status if isinstance(status, str) else status.value
        self.child_ids = child_ids or []
        self.checkpoints = checkpoints or []

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "parent_id": self.parent_id,
            "status": self.status,
            "child_ids": self.child_ids,
            "checkpoints": self.checkpoints
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            title=data["title"],
            description=data["description"],
            priority=data.get("priority", "medium"),
            parent_id=data.get("parent_id"),
            goal_id=data["id"],
            status=data.get("status", GoalStatus.PENDING.value),
            child_ids=data.get("child_ids", []),
            checkpoints=data.get("checkpoints", [])
        )

class GoalManager:
    def __init__(self, goals_file=".pulse/goals.json"):
        self.goals_file = goals_file
        self.goals = {}
        self._ensure_file()
        self.load_goals()

    def _ensure_file(self):
        os.makedirs(os.path.dirname(self.goals_file), exist_ok=True)
        if not os.path.exists(self.goals_file):
            with open(self.goals_file, "w") as f:
                json.dump([], f)

    def load_goals(self):
        try:
            with open(self.goals_file, "r") as f:
                data = json.load(f)
                for item in data:
                    goal = Goal.from_dict(item)
                    self.goals[goal.id] = goal
        except Exception as e:
            print(f"Error loading goals: {e}")

    def save_goals(self):
        try:
            with open(self.goals_file, "w") as f:
                data = [g.to_dict() for g in self.goals.values()]
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving goals: {e}")

    def create_goal(self, title, description, parent_id=None):
        goal = Goal(title, description, parent_id=parent_id)
        self.goals[goal.id] = goal
        if parent_id and parent_id in self.goals:
            self.goals[parent_id].child_ids.append(goal.id)
        self.save_goals()
        return goal

    def update_status(self, goal_id, new_status):
        if goal_id in self.goals:
            if isinstance(new_status, GoalStatus):
                new_status = new_status.value
            self.goals[goal_id].status = new_status
            self.save_goals()

    def get_pending_goals(self):
        return [g for g in self.goals.values() if g.status == GoalStatus.PENDING.value]

    def get_active_goal(self):
        # returns the deepest active goal (a goal that is IN_PROGRESS and has no IN_PROGRESS children)
        in_progress = [g for g in self.goals.values() if g.status == GoalStatus.IN_PROGRESS.value]
        if not in_progress:
            # Pick highest priority pending goal
            pending = self.get_pending_goals()
            if pending:
                return pending[0]
            return None
        
        # simple resolution for now: return the first in-progress
        return in_progress[-1]
