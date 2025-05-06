# chứa Python 3.9 chạy trên Alpine Linux 3.13
# Alpine là phiên bản Linux nhẹ, tối ưu cho container vì chỉ chứa các thành phần tối thiểu, giảm kích thước image và tăng hiệu suất
FROM python:3.9-alpine3.13

# Định nghĩa thông tin người duy trì
# Giúp người dùng khác biết ai chịu trách nhiệm duy trì image, đặc biệt khi dự án được chia sẻ hoặc sử dụng bởi đội nhóm
LABEL maintainer="xungmi1909@gmail.com"

# Output của Python (log, print) được gửi trực tiếp đến console thay vì lưu vào buffer.
ENV PYTHONUNBUFFERED=1

# Sao chép tệp chứa danh sách dependencies cần thiết cho dự án vào thư mục tạm /tmp trong container.
# /tmp được chọn vì đây là thư mục tạm, sẽ xóa sau khi cài đặt để giữ image nhẹ.
COPY ./requirements.txt /tmp/requirements.txt

# Tệp này chứa dependencies bổ sung cho môi trường phát triển (VD: công cụ testing, linting).
# Được sao chép vào /tmp để sử dụng tạm thời
COPY ./requirements.dev.txt /tmp/requirements.dev.txt

# Được sao chép vào /tmp để sử dụng tạm thời
# Sao chép vào /scripts trong container để sử dụng sau này
# COPY ./scripts /scripts

# Thư mục app chứa toàn bộ mã nguồn của dự án Django
# Sao chép vào /app trong container, nơi ứng dụng sẽ được chạy.
COPY ./app /app

# Đặt /app làm thư mục mặc định cho các lệnh tiếp theo (VD: chạy lệnh Django, pip).
WORKDIR /app

# Công bố cổng 8000 mà container sẽ sử dụng.
EXPOSE 8000

# Định nghĩa biến build-time DEV với giá trị mặc định là false.
# Biến này kiểm soát việc cài đặt dependencies phát triển (requirements.dev.txt).
# Mặc định false, chỉ thay đổi thành true khi build cho phát triển.
ARG DEV=false

# Tạo virtual environment tại /py để cô lập dependencies Python của dự án.
# Giảm xung đột với dependencies của base image
RUN python -m venv /py && \
# Cập nhật pip lên phiên bản mới nhất để đảm bảo tương thích và hiệu suất khi cài đặt gói.
    /py/bin/pip install --upgrade pip && \
    # Thêm dòng cài đặt PostgreSQL client (cần cho kết nối)
    apk add --update --no-cache postgresql-client jpeg-dev && \
    # Thêm nhóm gói tạm thời để build psycopg2
    # --virtual .tmp-build-deps: nhóm các gói build lại thành một tên tạm để dễ xóa sau.
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev zlib zlib-dev linux-headers && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    # Kiểm tra biến DEV. Nếu true, cài đặt các gói từ requirements.dev.txt (VD: pytest, flake8)
    # Chỉ áp dụng trong môi trường phát triển, không cài trong production để Tăng bảo mật và giảm dung lượng Docker image production.
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    # Xóa thư mục tạm /tmp
    # Xóa các tệp tạm (requirements.txt, requirements.dev.txt) để giảm kích thước image
    # Tuân thủ nguyên tắc giữ image nhẹ nhất có thể
    rm -rf /tmp && \
    # Sau khi cài xong gói Python, Xóa nhóm gói .tmp-build-deps để giảm kích thước image
    # Đảm bảo image chỉ chứa những gì cần thiết để chạy ứng dụng.
    # apk del .tmp-build-deps && \
    # Tạo người dùng django-user
    # Tránh chạy ứng dụng với quyền root (có toàn quyền), giảm rủi ro bảo mật nếu ứng dụng bị xâm nhập
    # django-user chỉ có quyền hạn chế, không tạo home directory để giữ image nhẹ
    adduser --disabled-password --no-create-home django-user
    #  && \
    # 
    # mkdir -p /vol/web/media && \
    # mkdir -p /vol/web/static && \
    # chown -R django-user:django-user /vol && \
    # chmod -R 755 /vol && \
    # chmod -R +x /scripts

# Thêm virtual environment vào PATH, cho phép chạy lệnh Python mà không cần chỉ định đường dẫn đầy đủ.
ENV PATH="/scripts:/py/bin:$PATH"

# Chuyển sang người dùng django-user ở cuối Dockerfile, đảm bảo container chạy với quyền hạn chế, không phải root.
USER django-user

# Chỉ định lệnh mặc định khi container khởi động.
# Chạy script run.sh (trong /scripts) khi container bắt đầu để khởi động ứng dụng
CMD ["run.sh"]