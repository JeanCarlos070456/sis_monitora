from django.conf import settings
def app_settings(request):
 return {'demo_mode':settings.SIS_DEMO_MODE}
