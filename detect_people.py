from flask import Flask, Response
import cv2
import threading

# Đường dẫn RTSP từ camera
RTSP_URL = "rtsp://admin:UHEGHG@server.iof.vn:5546/ch1/main"

# Kết nối tới camera RTSP
cap = cv2.VideoCapture(RTSP_URL)

# Kiểm tra kết nối
if not cap.isOpened():
    print("Không thể kết nối tới camera. Kiểm tra lại URL RTSP.")
    exit()

# Biến toàn cục để lưu khung hình
frame_lock = threading.Lock()
current_frame = None

# Hàm đọc luồng RTSP liên tục trong luồng riêng
def rtsp_stream():
    global current_frame
    while True:
        success, frame = cap.read()
        if not success:
            print("Không nhận được khung hình. Đang thử lại...")
            continue

        # Đảm bảo độ phân giải là 1920x1080 (Full HD)
        frame = cv2.resize(frame, (1920, 1080))

        # Cập nhật khung hình toàn cục
        with frame_lock:
            current_frame = frame

# Tạo một luồng riêng để xử lý RTSP
stream_thread = threading.Thread(target=rtsp_stream, daemon=True)
stream_thread.start()

# Khởi tạo Flask
app = Flask(__name__)

def generate_frames(quadrant):
    global current_frame
    while True:
        with frame_lock:
            if current_frame is None:
                continue

            # Cắt khung hình thành 4 phần
            height, width, _ = current_frame.shape
            mid_x, mid_y = width // 2, height // 2

            if quadrant == 1:  # Phần trên bên trái
                sub_frame = current_frame[0:mid_y, 0:mid_x]
            elif quadrant == 2:  # Phần trên bên phải
                sub_frame = current_frame[0:mid_y, mid_x:width]
            elif quadrant == 3:  # Phần dưới bên trái
                sub_frame = current_frame[mid_y:height, 0:mid_x]
            elif quadrant == 4:  # Phần dưới bên phải
                sub_frame = current_frame[mid_y:height, mid_x:width]

            # Mã hóa khung hình thành JPEG
            _, buffer = cv2.imencode('.jpg', sub_frame)
            frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Đường dẫn web phát từng khung hình
@app.route('/video_feed/<int:quadrant>')
def video_feed(quadrant):
    return Response(generate_frames(quadrant), mimetype='multipart/x-mixed-replace; boundary=frame')

# Trang chính hiển thị 4 khung hình
@app.route('/')
def index():
    return '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <title>Camera Stream</title>
            <style>
                body { display: flex; flex-wrap: wrap; margin: 0; }
                img { width: 50%; height: auto; }
            </style>
        </head>
        <body>
            <h1 style="width: 100%; text-align: center;">Camera Stream (4 khung hình)</h1>
            <img src="/video_feed/1" alt="Quadrant 1">
            <img src="/video_feed/2" alt="Quadrant 2">
            <img src="/video_feed/3" alt="Quadrant 3">
            <img src="/video_feed/4" alt="Quadrant 4">
        </body>
        </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
