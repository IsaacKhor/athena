from django.contrib import admin
from django.urls import path, include

from grader import views, file_access

urlpatterns = [
    path(''                                                         , views.home       ,               name='home'),
    path('course/<int:courseid>/add_assgn'                          , views.course,                    name='add_assgn'),
    path('course/<int:courseid>'                                    , views.course,                    name='course'),
    path('add_assgn/<int:courseid>'                                 , views.edit_assgn,                name='add_assgn'),
    path('edit_assgn/<int:courseid>/<int:assgnid>'                  , views.edit_assgn,                name='edit_assgn'),
    path('add_course/'                                              , views.edit_course,               name='add_course'),
    path('edit_course/<int:courseid>'                               , views.edit_course,               name='edit_course'),
    path('assignment/<int:assgnid>'                                 , views.assignment,                name='assignment'),
    path('submissions/<int:assgnid>/<int:userid>'                   , views.submissions,               name='submissions'),
    path('course/<int:courseid>/<str:filename>'                     , file_access.course_file_download,name='course_file_download'),
    path('course/<int:courseid>/delete_file/<str:filename>'         , file_access.course_file_delete,  name='course_file_delete'),
    path('assignment/<int:assgnid>/<str:filename>'                  , file_access.assgn_file_download, name='assgn_file_download'),
    path('assignment/<int:assgnid>/delete_file/<str:filename>'      , file_access.assgn_file_delete,   name='assgn_file_delete'),
    path('download_grades/<int:courseid>'                           , file_access.grades_download,     name='grades_download'),
    path('download_subfile/<int:subid>'                             , file_access.submission_download, name='submission_download'),
    path('download_subfile/<int:subid>/<str:subdir>/<str:filename>' , file_access.submission_download, name='submission_download_subdir'),
    path('delete_subfile/<int:subid>/<str:subdir>/<str:filename>'   , file_access.submission_delete,   name='submission_delete_subdir'),
    path('remove_grade/<int:gradeid>'                               , file_access.remove_grade,        name='remove_grade'),
    path('reset_autograde/<int:gradeid>'                            , file_access.reset_autograde,     name='reset_autograde'),
    path('login/'                                                   , views.login,                     name='login'),
    path('logout/'                                                  , views.logout,                    name='logout'),
]

urlpatterns = patterns('',
)
