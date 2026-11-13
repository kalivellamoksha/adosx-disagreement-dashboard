from django.urls import path
from reconciliation.views import disagreements_view

urlpatterns = [
    path("disagreements/", disagreements_view, name="disagreements"),
]