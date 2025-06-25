import json, os
from django.conf import settings
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from decouple import config



from .utils.fuel import load_fuel_data
from .utils.route import fetch_route, decode_route_geometry, plan_fuel_stops

FUEL_PATH = config('FUEL_PATH')
ORS_API_KEY = config('ORS_API_KEY')

FUEL_CSV_PATH = os.path.join(settings.BASE_DIR, FUEL_PATH)

@method_decorator(csrf_exempt, name='dispatch')
class RouteFuelView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            start = data.get('start')
            end = data.get('end')

            if not (start and end and isinstance(start, list) and isinstance(end, list)):
                return JsonResponse({'error': 'Both start and end must be provided as [lat, lon]'}, status=400)

            try:
                route_data = fetch_route(start, end, ORS_API_KEY)
            except requests.RequestException as e:
                return JsonResponse({'error': f'Routing API failed: {str(e)}'}, status=500)

            try:
                coords, distance_meters = decode_route_geometry(route_data)
            except Exception as e:
                return JsonResponse({'error': f'Failed to decode geometry: {str(e)}'}, status=500)

            stations = load_fuel_data(FUEL_CSV_PATH)
            result = plan_fuel_stops(coords, distance_meters, stations)

            return JsonResponse({
                'start': start,
                'end': end,
                **result
            })

        except Exception as e:
            return JsonResponse({'error': f'Invalid request: {str(e)}'}, status=400)
