"""URL mappings for the user API."""
from django.urls import path
from user import views

# Đặt namespace cho app là user
# định nghĩa namespace cho các url thuộc app này
#  Khi nào dùng namespace:name? Khi có nhiều app trong một project Django, bạn thường dùng namespace để tránh trùng tên route.
# Ví dụ: Nếu bạn có hai app, user và blog, cả hai đều có URL với name='create', thì app_name sẽ giúp Django biết bạn đang muốn tham chiếu đến URL nào.
app_name = 'user'


# Trong file urls.py, mỗi dòng path(...) hoặc re_path(...) chính là một route.
# Một route định nghĩa cách một URL được ánh xạ tới một view
urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('token/', views.CreateTokenView.as_view(), name='token'),
    # ánh xạ /me/ đến ManageUserView
    path('me/', views.ManageUserView.as_view(), name='me'),
]