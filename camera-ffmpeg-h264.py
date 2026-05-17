import cv2
import ffmpeg
import numpy as np

WIDTH, HEIGHT, FPS = 640, 480, 20
OUTPUT_FILE = "ffmpeg_h264.mp4"

# 打开摄像头
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
cap.set(cv2.CAP_PROP_FPS, FPS)

# 配置 FFmpeg H.264 编码
process = (
    ffmpeg
    .input('pipe:', format='rawvideo', pix_fmt='bgr24', s=f'{WIDTH}x{HEIGHT}', r=FPS)
    .output(OUTPUT_FILE, vcodec='libx264', pix_fmt='yuv420p', r=FPS)
    .overwrite_output()
    .run_async(pipe_stdin=True)
)

print("📷 摄像头已开启，正在录制 H.264 视频...")
print("按 q 退出并保存视频")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    cv2.imshow("Camera Preview", frame)
    process.stdin.write(frame.tobytes())

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

process.stdin.close()
process.wait()
cap.release()
cv2.destroyAllWindows()

print(f"\n✅ 视频已保存：{OUTPUT_FILE}")