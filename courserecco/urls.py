from django.urls import path
from .views import employee_recommendation, trend_analysis, base_page
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', base_page, name='base_page'),  # Root URL (base page for HR/Employee selection)
    path('employee-recommendation/', employee_recommendation, name='employee_recommendation'),  # Employee recommendation page
    path('trend-analysis/', trend_analysis, name='trend_analysis'),  # HR trend analysis page
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
