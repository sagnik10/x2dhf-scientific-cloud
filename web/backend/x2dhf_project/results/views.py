from rest_framework import viewsets,status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter,OrderingFilter
from django.http import FileResponse
import csv,json
from .models import ComputationResult,ResultVisualization,Export
from .serializers import ComputationResultSerializer,ResultVisualizationSerializer,ExportSerializer
class ComputationResultViewSet(viewsets.ModelViewSet):
    serializer_class=ComputationResultSerializer
    permission_classes=[IsAuthenticated]
    filter_backends=[DjangoFilterBackend,SearchFilter,OrderingFilter]
    filterset_fields=['computation__theory','computation__status']
    search_fields=['computation__title']
    ordering_fields=['created_at']
    ordering=['-created_at']
    def get_queryset(self):
        return ComputationResult.objects.filter(user=self.request.user)
    @action(detail=True,methods=['get'])
    def download_raw(self,request,pk=None):
        result=self.get_object()
        if result.result_file:
            return FileResponse(result.result_file.open('rb'),as_attachment=True,filename=f"result_{result.id}.dat")
        return Response({'error':'No file available'},status=status.HTTP_404_NOT_FOUND)
    @action(detail=True,methods=['post'])
    def export(self,request,pk=None):
        result=self.get_object()
        format_type=request.data.get('format','csv')
        if format_type=='csv':
            export_file=Export.objects.create(result=result,user=request.user,format='csv')
            return Response({'id':export_file.id,'format':'csv'},status=status.HTTP_201_CREATED)
        elif format_type=='json':
            export_data=ComputationResultSerializer(result).data
            return Response(export_data)
        return Response({'error':'Unsupported format'},status=status.HTTP_400_BAD_REQUEST)
class ResultVisualizationViewSet(viewsets.ModelViewSet):
    serializer_class=ResultVisualizationSerializer
    permission_classes=[IsAuthenticated]
    def get_queryset(self):
        result_id=self.request.query_params.get('result_id')
        if result_id:
            return ResultVisualization.objects.filter(result_id=result_id,result__user=self.request.user)
        return ResultVisualization.objects.filter(result__user=self.request.user)
    def perform_create(self,serializer):
        serializer.save()
class ExportViewSet(viewsets.ModelViewSet):
    serializer_class=ExportSerializer
    permission_classes=[IsAuthenticated]
    def get_queryset(self):
        return Export.objects.filter(user=self.request.user)
    @action(detail=True,methods=['get'])
    def download(self,request,pk=None):
        export=self.get_object()
        if export.file:
            return FileResponse(export.file.open('rb'),as_attachment=True,filename=f"export_{export.id}.{export.format.lower()}")
        return Response({'error':'File not found'},status=status.HTTP_404_NOT_FOUND)
