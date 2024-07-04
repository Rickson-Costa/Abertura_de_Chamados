from django.urls import path, include
from main import views
from main.views import error_handler
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('SOS/', include('main.urls')),
    path('', views.inicio, name='base'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Adicione a configuração para manipular erros
handler404 = 'main.views.error_handler'  # View que manipulará o erro 404
handler500 = 'main.views.error_handler'  # View que manipulará o erro 500
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)