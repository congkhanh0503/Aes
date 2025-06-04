# Ứng dụng Secure Chat

## Tổng quan
Secure Chat là một ứng dụng trò chuyện dựa trên web, cung cấp tính năng nhắn tin mã hóa đầu cuối bằng AES. Người dùng có thể tham gia các phòng trò chuyện, gửi tin nhắn công khai và riêng tư, đồng thời tùy chỉnh hồ sơ với ảnh đại diện. Ứng dụng được xây dựng bằng Flask, SocketIO và JavaScript, tập trung vào bảo mật và giao tiếp thời gian thực.

## Tính năng
- **Mã hóa đầu cuối**: Tin nhắn được mã hóa bằng AES (chế độ ECB) với khóa mã hóa do người dùng cung cấp (16, 24 hoặc 32 ký tự).
- **Nhắn tin thời gian thực**: Sử dụng Flask-SocketIO để gửi tin nhắn theo thời gian thực trong các phòng công khai và trò chuyện riêng tư.
- **Ảnh đại diện tùy chỉnh**: Người dùng có thể tải lên hình ảnh hoặc sử dụng biểu tượng cảm xúc mặc định làm ảnh đại diện.
- **Quản lý phòng**: Tạo hoặc tham gia phòng trò chuyện với ID Phòng và khóa mã hóa duy nhất.
- **Trạng thái người dùng**: Hiển thị danh sách người dùng trực tuyến và chỉ báo đang nhập văn bản theo thời gian thực.
- **Tin nhắn riêng tư**: Gửi tin nhắn riêng đã mã hóa đến người dùng cụ thể trong cùng phòng.
- **Giao diện đáp ứng**: Giao diện hiện đại và thân thiện, sử dụng Tailwind CSS để định kiểu.

## Yêu cầu trước khi cài đặt
Để chạy ứng dụng Secure Chat, đảm bảo bạn đã cài đặt:
- Python 3.8 trở lên
- Node.js và npm (cho các phụ thuộc JavaScript)
- Trình duyệt web hiện đại (Chrome, Firefox, Safari, v.v.)

## Hướng dẫn cài đặt

1. **Sao chép kho lưu trữ**:
   ```bash
   git clone <repository-url>
   cd secure-chat
   ```

2. **Thiết lập môi trường ảo**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Trên Windows: venv\Scripts\activate
   ```

3. **Cài đặt các phụ thuộc Python**:
   ```bash
   pip install flask flask-socketio pycryptodome
   ```

4. **Cài đặt các phụ thuộc JavaScript**:
   Điều hướng đến thư mục dự án và cài đặt phụ thuộc giao diện:
   ```bash
   npm install
   ```

5. **Cấu hình ứng dụng**:
   - Cập nhật `SECRET_KEY` trong `server.py` thành một giá trị an toàn:
     ```python
     app.config['SECRET_KEY'] = 'your-secret-key-here'
     ```
   - Đảm bảo file `index.html` nằm trong thư mục `templates`.

6. **Chạy server**:
   ```bash
   python server.py
   ```
   Server sẽ khởi động tại `http://localhost:5000`.

## Hướng dẫn sử dụng
1. **Truy cập ứng dụng**:
   Mở trình duyệt web và truy cập `http://localhost:5000`.

2. **Tham gia phòng**:
   - Nhập tên của bạn, chọn ảnh đại diện (biểu tượng cảm xúc hoặc hình ảnh tải lên), cung cấp ID Phòng và khóa mã hóa (16, 24 hoặc 32 ký tự).
   - Nhấn "Tham gia phòng" để vào trò chuyện.

3. **Các tính năng trò chuyện**:
   - **Tin nhắn công khai**: Nhập tin nhắn vào ô nhập liệu và nhấn "Gửi" để gửi đến toàn bộ phòng.
   - **Tin nhắn riêng tư**: Chọn một người dùng từ danh sách trực tuyến để gửi tin nhắn riêng.
   - **Chỉ báo đang nhập**: Hiển thị khi người dùng khác đang nhập văn bản.
   - **Đăng xuất**: Nhấn nút "Đăng xuất" để rời phòng.

4. **Mã hóa**:
   - Tất cả tin nhắn được mã hóa phía client bằng khóa mã hóa cung cấp.
   - Server xử lý tin nhắn đã mã hóa mà không truy cập được văn bản gốc.

## Cấu trúc thư mục
- `server.py`: Backend Flask với SocketIO cho giao tiếp thời gian thực và các endpoint mã hóa/giải mã AES.
- `templates/index.html`: Mẫu HTML giao diện với Tailwind CSS và JavaScript cho giao diện trò chuyện.
- `static/`: Chứa các tài nguyên tĩnh (CSS, JavaScript, hình ảnh).
- `package.json`: Cấu hình Node.js cho các phụ thuộc giao diện.

## Lưu ý bảo mật
- **Mã hóa**: Sử dụng AES chế độ ECB để đơn giản. Trong môi trường sản phẩm, nên sử dụng chế độ bảo mật hơn như GCM.
- **Quản lý khóa**: Người dùng cần chia sẻ khóa mã hóa một cách an toàn bên ngoài ứng dụng.
- **Bảo mật phiên**: Sử dụng quản lý phiên của Flask; đảm bảo `SECRET_KEY` an toàn trong môi trường sản phẩm.
- **CORS**: SocketIO được cấu hình với `cors_allowed_origins="*"` cho phát triển. Hạn chế điều này trong sản phẩm.

## Hạn chế đã biết
- Sử dụng chế độ AES-ECB, không lý tưởng cho sản phẩm do thiếu bảo mật ngữ nghĩa.
- Không lưu trữ tin nhắn lâu dài; tin nhắn sẽ mất khi server khởi động lại.
- Tải lên tệp chỉ giới hạn ở hình ảnh cho ảnh đại diện.
- Không có xác thực người dùng; tên người dùng chỉ được kiểm tra tính duy nhất trong phòng.

## Phát triển
- **Chế độ gỡ lỗi**: Server chạy ở chế độ gỡ lỗi (`debug=True`) cho phát triển. Vô hiệu hóa trong sản phẩm.
- **Kiểm thử**: Đảm bảo tất cả phụ thuộc được cài đặt và chạy server để kiểm tra cục bộ.
- **Mở rộng tính năng**:
  - Thêm lưu trữ tin nhắn lâu dài (ví dụ: tích hợp cơ sở dữ liệu).
  - Thực hiện xác thực người dùng để tăng cường bảo mật.
  - Hỗ trợ thêm loại tệp cho tải lên.

## Khắc phục sự cố
- **Server không khởi động**: Kiểm tra phụ thuộc Python và đảm bảo cổng `5000` trống.
- **Lỗi SocketIO**: Xác minh rằng `flask-socketio` và script SocketIO phía client tương thích.
- **Lỗi mã hóa**: Đảm bảo khóa mã hóa dài 16, 24 hoặc 32 ký tự.
- **Lỗi CORS**: Điều chỉnh `cors_allowed_origins` trong `server.py` nếu cần.

## Đóng góp
Chào mừng mọi đóng góp! Vui lòng gửi pull request hoặc mở issue cho lỗi, tính năng hoặc cải tiến.

## Giấy phép
Dự án này được cấp phép theo Giấy phép MIT.