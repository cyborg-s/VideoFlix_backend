from django.http import JsonResponse

def video_list(request):
    return JsonResponse({'message': 'Alle Videos'})

def video_detail(request, id):
    return JsonResponse({'message': f'Video mit ID {id}'})