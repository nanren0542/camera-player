import cv2
import time

# ======================
# 配置参数
# ======================
WIDTH = 1280       # 视频宽度
HEIGHT = 720      # 视频高度
FPS = 25          # 帧率
#OUTPUT_FILE = "output_h264.avi"  # 输出文件名

# 注意：H.264 推荐用 .mp4 后缀，.avi 容器对 H.264 的支持有限
OUTPUT_FILE = "output_h264.mp4"

# ======================
# 打开摄像头
# ======================
cap = cv2.VideoCapture(0)  # 0 = 默认摄像头
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
cap.set(cv2.CAP_PROP_FPS, FPS)

"""
# ======================
# H.264 编码器 + 写入 AVI
# ======================
# 关键：cv2.VideoWriter_fourcc(*'XVID') 会自动使用 H.264 编码
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(
    OUTPUT_FILE,
    fourcc,
    FPS,
    (WIDTH, HEIGHT)
)
"""

# avc1 就是 H.264 的标准 fourcc, 但需要系统安装了对应的编码器（如 x264）
# https://github.com/cisco/openh264/releases?page=2 , 下载 v1.8.0，
# 把 openh264-1.8.0-win64.dll ， 放到 H:\py-env\py-evn314\Scripts 目录下
fourcc = cv2.VideoWriter_fourcc(*'avc1')
out = cv2.VideoWriter(OUTPUT_FILE, fourcc, FPS, (WIDTH, HEIGHT))


print("📷 摄像头已开启，正在录制...")
print("按 q 退出并保存视频")

# ======================
# 主循环：预览 + 写入文件
# ======================
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 显示预览画面
    cv2.imshow("Camera Preview (H.264 + AVI)", frame)

    # 写入视频文件（自动 H.264 压缩）
    out.write(frame)

    # 按 q 退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ======================
# 释放资源
# ======================
cap.release()
out.release()
cv2.destroyAllWindows()

print(f"\n✅ 视频已保存：{OUTPUT_FILE}")