"""Core URL configuration."""

from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path("", RedirectView.as_view(url="/dashboard/", permanent=False)),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("reports/", views.reports_view, name="reports"),
    path("export/csv/", views.export_csv_view, name="export_csv"),
    path("export/pdf/", views.export_pdf_view, name="export_pdf"),
]
