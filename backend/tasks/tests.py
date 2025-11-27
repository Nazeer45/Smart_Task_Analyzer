from django.test import TestCase
from .scoring import TaskScorer
from datetime import datetime, timedelta
from rest_framework.test import APIClient

class ScoringTests(TestCase):
    def setUp(self):
        self.scorer = TaskScorer()

    def test_past_due_urgency(self):
        task = {
            'id': 1,
            'title': 'Overdue Task',
            'due_date': (datetime.now() - timedelta(days=2)).isoformat(),
            'estimated_hours': 2,
            'importance': 5,
            'dependencies': []
        }
        score, breakdown = self.scorer.score_task(task, [task])
        self.assertGreaterEqual(breakdown['urgency'], 10)  # Bonus for overdue

    def test_quick_win(self):
        task = {
            'id': 2,
            'title': 'Quick Win',
            'due_date': (datetime.now() + timedelta(days=2)).isoformat(),
            'estimated_hours': 0.5,
            'importance': 5,
            'dependencies': []
        }
        score, breakdown = self.scorer.score_task(task, [task])
        self.assertEqual(breakdown['effort'], 10)

    def test_circular_dependency(self):
        tasks = [
            {'id': 1, 'dependencies': [2]},
            {'id': 2, 'dependencies': [3]},
            {'id': 3, 'dependencies': [1]},
        ]
        self.assertTrue(TaskScorer.detect_circular_dependencies(tasks))



class SuggestEndpointTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_suggest_returns_top_3_with_explanations(self):
        tasks = [
            {
                "id": 1,
                "title": "A",
                "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
                "estimated_hours": 1,
                "importance": 8,
                "dependencies": []
            },
            {
                "id": 2,
                "title": "B",
                "due_date": (datetime.now() + timedelta(days=2)).isoformat(),
                "estimated_hours": 2,
                "importance": 5,
                "dependencies": []
            },
            {
                "id": 3,
                "title": "C",
                "due_date": (datetime.now() + timedelta(days=3)).isoformat(),
                "estimated_hours": 0.5,
                "importance": 7,
                "dependencies": []
            },
            {
                "id": 4,
                "title": "D",
                "due_date": (datetime.now() + timedelta(days=10)).isoformat(),
                "estimated_hours": 4,
                "importance": 3,
                "dependencies": []
            }
        ]
        resp = self.client.post("/api/tasks/suggest/", {"tasks": tasks}, format="json")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data["suggested_tasks"]), 3)
        self.assertIn("explanation", data["suggested_tasks"][0])
