from django.urls import path



from . import views

urlpatterns = [
     
    path('', views.course_search_view, name='course_search'),
    ]