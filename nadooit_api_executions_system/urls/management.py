from django.urls import path,include


from nadooit_api_executions_system.views.management import index_management,create_api_key,login_user,logout_user

urlpatterns = [
    path('login_user', login_user, name="login-user"),
    path('logout_user', logout_user, name="logout-user"),
    path('', index_management, name="manage"),
    path('', include('django.contrib.auth.urls'), name="manage"),
    path('create-api-key', create_api_key, name="create-api-key"),
]
