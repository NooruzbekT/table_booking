from rest_framework import viewsets
from .models import Table
from .serializers import TableSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly

class TableViewSet(viewsets.ModelViewSet):
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
