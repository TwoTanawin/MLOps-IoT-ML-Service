from django.db.models import OuterRef, Subquery
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ml_api.services.infer_runner import MLrunner
from .models import MLResult

# Swagger input schema for POST
classify_request_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['serialNumber', 'values'],
    properties={
        'serialNumber': openapi.Schema(type=openapi.TYPE_STRING, description="Sensor serial number"),
        'values': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Items(type=openapi.TYPE_NUMBER),
            minItems=4,
            maxItems=4,
            description="Array of 4 float sensor values: [DO, pH, salinity, temp]"
        ),
    }
)

# Swagger response schema for POST
classify_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'serialNumber': openapi.Schema(type=openapi.TYPE_STRING),
        'class_name': openapi.Schema(type=openapi.TYPE_STRING),
        'confidence': openapi.Schema(type=openapi.TYPE_NUMBER, format='float'),
    }
)

# Swagger response schema for GET
latest_results_response_schema = openapi.Schema(
    type=openapi.TYPE_ARRAY,
    items=openapi.Items(
        type=openapi.TYPE_OBJECT,
        properties={
            'serialNumber': openapi.Schema(type=openapi.TYPE_STRING),
            'result': openapi.Schema(type=openapi.TYPE_STRING),
            'created_at': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
        }
    )
)

class ClassifySensorData(APIView):

    @swagger_auto_schema(
        operation_description="Classify water quality from 4 sensor values (DO, pH, salinity, temp)",
        request_body=classify_request_schema,
        responses={200: classify_response_schema, 400: "Invalid input", 500: "Server error"}
    )
    def post(self, request):
        try:
            serial_number = request.data.get('serialNumber')
            values = request.data.get('values')

            if not serial_number or not isinstance(values, list) or len(values) != 4:
                return Response({"error": "Invalid input format"}, status=status.HTTP_400_BAD_REQUEST)

            runner = MLrunner()
            result = runner.predict(values)

            try:
                MLResult.objects.create(
                    serialNumber=serial_number,
                    result=result["class_name"]
                )
            except Exception as e:
                self.logger.error(f"Database save failed: {e}")
                return Response({"error": f"DB save error: {str(e)}"}, status=500)

            return Response({
                "serialNumber": serial_number,
                "class_name": result["class_name"],
                "confidence": result["confidence"]
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetLatestResult(APIView):

    @swagger_auto_schema(
        operation_description="Get the latest classification result for a specific serial number.",
        manual_parameters=[
            openapi.Parameter(
                'serialNumber', openapi.IN_QUERY,
                description="Device Serial Number",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={200: latest_results_response_schema, 400: "Missing serialNumber", 500: "Server error"}
    )
    def get(self, request):
        serial_number = request.query_params.get('serialNumber')

        if not serial_number:
            return Response({"error": "serialNumber query parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            latest_result = MLResult.objects.filter(serialNumber=serial_number).order_by('-created_at').first()

            if not latest_result:
                return Response({"error": f"No data found for serial number: {serial_number}"}, status=status.HTTP_404_NOT_FOUND)

            data = {
                "serialNumber": latest_result.serialNumber,
                "result": latest_result.result,
                "created_at": latest_result.created_at
            }

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
