from django.contrib import admin
from django.urls import path, include

from grader import views, file_access

app_name = 'grader'
urlpatterns = [
    path('course/<int:courseid>/edit'                               , views.edit_course,               name='edit_course'),
    path('course/<int:courseid>/add_assgn'                          , views.edit_assgn,                name='add_assgn'),
    path('course/<int:courseid>/download_grades'                    , file_access.grades_download,     name='grades_download'),
    path('course/<int:courseid>/<str:filename>/delete'              , file_access.course_file_delete,  name='course_file_delete'),
    path('course/<int:courseid>/<str:filename>'                     , file_access.course_file_download,name='course_file_download'),
    path('course/<int:courseid>'                                    , views.course,                    name='course'),

    path('edit_assgn/<int:courseid>/<int:assgnid>'                  , views.edit_assgn,                name='edit_assgn'),

    path('assignment/<int:assgnid>/submissions/<int:userid>'        , views.submissions,               name='submissions'),
    path('assignment/<int:assgnid>/<str:filename>/delete'           , file_access.assgn_file_delete,   name='assgn_file_delete'),
    path('assignment/<int:assgnid>/<str:filename>'                  , file_access.assgn_file_download, name='assgn_file_download'),
    path('assignment/<int:assgnid>'                                 , views.assignment,                name='assignment'),

    path('submissions/<int:subid>/download'                         , file_access.submission_download, name='submission_download'),
    path('submissions/<int:subid>/<str:subdir>/<str:filename>/download', file_access.submission_download, name='submission_download_subdir'),
    path('submissions/<int:subid>/<str:subdir>/<str:filename>/delete', file_access.submission_download, name='submission_download_subdir'),

    path('grades/<int:gradeid>/remove'                              , file_access.remove_grade,        name='remove_grade'),
    path('grades/<int:gradeid>/reset_autograde'                     , file_access.reset_autograde,     name='reset_autograde'),

    path('login/'                                                   , views.login,                     name='login'),
    path('logout/'                                                  , views.logout,                    name='logout'),
    path(''                                                         , views.home       ,               name='home'),
]