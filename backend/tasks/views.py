from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .scoring import TaskScorer
from .serializers import TaskListSerializer

@api_view(['POST'])
def analyze_tasks(request):
    serializer = TaskListSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    data = serializer.validated_data
    strategy = data.get('strategy', 'smart_balance')
    scorer = TaskScorer(weights=TaskScorer.STRATEGIES.get(strategy))
    scored_tasks = scorer.score_all_tasks(data['tasks'])
    return Response({'tasks': scored_tasks, 'strategy': strategy, 'count': len(scored_tasks)})

@api_view(['POST'])
def suggest_tasks(request):
    serializer = TaskListSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    data = serializer.validated_data
    scorer = TaskScorer()
    all_scored = scorer.score_all_tasks(data['tasks'])
    top_tasks = all_scored[:3]
    return Response({
        'suggested_tasks': top_tasks,
        'reason': 'Top 3 tasks picked for today based on their urgency, importance, effort and dependencies.'
    },
    status=status.HTTP_200_OK
    )
