from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("courses/", views.courses, name="courses"),
    path("labs/", views.labs, name="labs"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("courses/javascript/", views.course_javascript, name="course_javascript"),
    path("lesson/javascript/<slug:slug>/", views.lesson_javascript, name="lesson_javascript"),
    path("courses/python/", views.course_python, name="course_python"),
    path("lesson/python/<slug:slug>/", views.lesson_python, name="lesson_python"),
    path("courses/c/", views.course_c, name="course_c"),
    path("lesson/c/<slug:slug>/", views.lesson_c, name="lesson_c"),
    path("courses/arduino/", views.course_arduino, name="course_arduino"),
    path("lesson/arduino/<slug:slug>/", views.lesson_arduino, name="lesson_arduino"),
]
