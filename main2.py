import cv2
import copy
import numpy as np
import test
import time

cap_L = cv2.VideoCapture(0)
cap_R = cv2.VideoCapture(1)

boot = True
# ノイズ除去のためのカーネルの定義
kernel = np.ones((5, 5), np.uint8)
# HSVによる上限、下限の設定（特定色の検出）　 ([Hue, Saturation, Value])
hsvLower = np.array([90, 122, 100])  # 下限
hsvUpper = np.array([115, 255, 255])  # 上限
x_pre1 = 0
y_pre1 = 0
x_pre2 = 0
y_pre2 = 0
frame_L = frame_R = 0


def cap_center(num):
    global x_pre1, y_pre1
    global x_pre2, y_pre2
    global frame_L, frame_R
    if num == 0:
        frame = frame_L
    else:
        frame = frame_R
    # HSVに変換
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # HSVから特定色を検出したマスクを作成
    hsv_mask = cv2.inRange(hsv, hsvLower, hsvUpper)
    # 膨張，収縮を用いたノイズ除去
    blur_mask = cv2.dilate(hsv_mask, kernel)
    blur_mask = cv2.erode(hsv_mask, kernel)
    # ラベリング処理
    nlabels, labels, stats, centroids = cv2.connectedComponentsWithStats(
        blur_mask)
    # 領域が２つ以上ある場合に処理
    if nlabels >= 2:
        # 面積でソートして最大のもののみを取得
        top = stats[:, 4].argsort()[-2]
        # 領域の重心座標を浮動小数点表示で取得
        x0 = centroids[top, 0]
        y0 = centroids[top, 1]
        if num == 0:
            vx = int(x0 - x_pre1)
            vy = int(y0 - y_pre1)
            x_pre1 = x0
            y_pre1 = y0
        else:
            vx = int(x0 - x_pre2)
            vy = int(y0 - y_pre2)
            x_pre2 = x0
            y_pre2 = y0
        # 重心座標の保存
        if abs(vx) > 100 or abs(vy) > 100:
            return (0, 0)
        else:
            return(vx, vy)
    else:
        return(0, 0)


game = test.AirHockey()
print("aa")
while True:
    ret, frame_L = cap_L.read()
    x0_L, y0_L = cap_center(0)
    ret, frame_R = cap_R.read()
    x0_R, y0_R = cap_center(1)
    #print("カメラ１の物体中心座標（ｘ：" + str(x0_L) + "　ｙ：" + str(y0_L) + "）")
    #print("カメラ２の物体中心座標（ｘ：" + str(x0_R) + "　ｙ：" + str(y0_R) + "）")
    game.input()
    game.set_left_velocity(x0_L, y0_L)
    game.set_right_velocity(x0_R, y0_R)
    game.element_revise()
    game.collision_detect()
    game.element_revise()
    game.img_generate()
    game.show()
    if not game._boot:
        break
    ##cv2.imshow("camera_L", frame_L)
    #cv2.imshow("camera_R", frame_R)
time.sleep(5)
game.draw_winner_circle()
game.result_show()
cv2.waitKey(0)
cap_L.release()
cap_R.release()
cv2.destroyAllWindows()
