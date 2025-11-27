from datetime import datetime
from django.utils import timezone
import math

class TaskScorer:
    SMART_BALANCE = {
        'urgency': 0.35, 
        'importance': 0.35, 
        'effort': 0.2, 
        'dependency': 0.1
        }
    
    STRATEGIES = {
        'smart_balance': SMART_BALANCE,
        'fastest_wins': {'urgency': 0.1, 'importance': 0.1, 'effort': 0.7, 'dependency': 0.1},
        'high_impact':   {'urgency': 0.2, 'importance': 0.6, 'effort': 0.1, 'dependency': 0.1},
        'deadline_driven': {'urgency': 0.6, 'importance': 0.2, 'effort': 0.1, 'dependency': 0.1}
    }

    def __init__(self, weights=None):
        self.weights = weights or self.SMART_BALANCE
        if not (0.99 <= sum(self.weights.values()) <= 1.01):
            raise ValueError("Weights must sum to 1.0")

    @staticmethod
    def detect_circular_dependencies(tasks):
        task_map = {task.get('id'): task.get('dependencies', []) for task in tasks}
        def visit(node, visited, stack):
            visited.add(node)
            stack.add(node)
            for neighbor in task_map.get(node, []):
                if neighbor in stack:
                    return True
                if neighbor not in visited and visit(neighbor, visited, stack):
                    return True
            stack.remove(node)
            return False
        visited = set()
        for task_id in task_map:
            if task_id not in visited:
                if visit(task_id, visited, set()):
                    return True
        return False

    def calculate_urgency(self, due_date):
        now = timezone.now()
        if timezone.is_naive(due_date):
            due_date = timezone.make_aware(due_date, timezone.get_current_timezone())
        days_until_due = (due_date - now).days

        if days_until_due < 0:
            return 10  # overdue → max urgency
        elif days_until_due <= 1:
            return 10
        elif days_until_due <= 3:
            return 9 - (days_until_due - 1)
        elif days_until_due <= 7:
            return 7 - ((days_until_due - 3) / 4)
        else:
            return max(0, 5 - math.log(days_until_due - 6))


    def calculate_effort(self, hours):
        if hours <= 0:
            return 0
        elif hours < 1:
            return 10
        elif hours <= 2:
            return 10 - hours * 1.5
        elif hours <= 4:
            return 7 - (hours - 2) / 2
        else:
            return max(0, 5 - math.log(hours - 3))

    def calculate_dependency(self, task_id, tasks):
        count = sum([task_id in t.get('dependencies', []) for t in tasks])
        return min(10, count * 2)

    def score_task(self, task, tasks):
        due_raw = task['due_date']
        
        if isinstance(due_raw, str):
            due_date = datetime.fromisoformat(due_raw)
        else:
            due_date = due_raw
            
        urgency = self.calculate_urgency(due_date)
        importance = task['importance']
        effort = self.calculate_effort(task['estimated_hours'])
        dependency = self.calculate_dependency(task.get('id', 0), tasks)
        score = (
            urgency * self.weights['urgency'] +
            importance * self.weights['importance'] +
            effort * self.weights['effort'] +
            dependency * self.weights['dependency']
        ) * 10  # scale to 0-100
        return round(score, 2), {'urgency': urgency, 'importance': importance, 'effort': effort, 'dependency': dependency}

    def score_all_tasks(self, tasks):
        scored = []
        for task in tasks:
            score, breakdown = self.score_task(task, tasks)
            explanation = self._generate_explanation(task, breakdown)
            scored.append({**task, 'priority_score': score, 'score_breakdown': breakdown, 'explanation': explanation})
        scored.sort(key=lambda x: x['priority_score'], reverse=True)
        return scored

    def _generate_explanation(self, task, breakdown):
        parts = []

        # Urgency-based messages
        if breakdown['urgency'] >= 9:
            parts.append("High urgency (due very soon)")
        elif breakdown['urgency'] >= 7:
            parts.append("Moderate urgency")

        # Importance-based messages
        if breakdown['importance'] >= 8:
            parts.append("Very important task")
        elif breakdown['importance'] >= 6:
            parts.append("Important task")

        # Effort-based messages
        if breakdown['effort'] >= 8:
            parts.append("Quick win (low effort)")
        elif breakdown['effort'] <= 3:
            parts.append("High effort")

        # Dependency-based messages
        if breakdown['dependency'] >= 4:
            parts.append("Blocks other tasks")

        if not parts:
            return "Moderate priority based on current factors"

        return " • ".join(parts)