from rest_framework import serializers

class TaskSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    title = serializers.CharField(max_length=255)
    due_date = serializers.DateTimeField()
    estimated_hours = serializers.FloatField(min_value=0.01)
    importance = serializers.IntegerField(min_value=1, max_value=10)
    dependencies = serializers.ListField(child=serializers.IntegerField(), required=False, default=list)

class TaskListSerializer(serializers.Serializer):
    tasks = TaskSerializer(many=True)
    strategy = serializers.ChoiceField(
        choices=['smart_balance', 'fastest_wins', 'high_impact', 'deadline_driven'],
        required=False, default='smart_balance'
    )
