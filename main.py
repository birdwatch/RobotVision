import cv2
import copy
import numpy as np
import test


cap_L = cv2.VideoCapture(0)
cap_R = cv2.VideoCapture(1)
boot = True

# ノイズ除去のためのカーネルの定義

kernel = np.ones((5, 5), np.uint8)


# HSVによる上限、下限の設定（肌色の検出）　 ([Hue, Saturation, Value])

hsvLower = np.array([0, 30, 60])  # 下限
hsvUpper = np.array([20, 150, 255])  # 上限


def cap_center(frame):

    # HSVに変換
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # HSVから肌色を検出したマスクを作成
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

        return(int(x0), int(y0))

    else:
        return(100, 100)


game = test.AirHockey()

while True:

    ret, frame_L = cap_L.read()
    x0_L, y0_L = cap_center(frame_L)

    ret, frame_R = cap_R.read()
    x0_R, y0_R = cap_center(frame_R)

    #print("カメラ１の物体中心座標（ｘ：" + str(x0_L) + "　ｙ：" + str(y0_L) + "）")
    #print("カメラ２の物体中心座標（ｘ：" + str(x0_R) + "　ｙ：" + str(y0_R) + "）")

    game.input()
    game.set_left(x0_L, y0_L)
    game.set_right(x0_R, y0_R)
    game.element_revise()
    game.collision_detect()
    game.img_generate()
    game.show()
    if not game._boot:
        break

    ##cv2.imshow("camera_L", frame_L)
    #cv2.imshow("camera_R", frame_R)


game.result_show()
cv2.waitKey(0)

cap_L.release()
cap_R.release()
cv2.destroyAllWindows()
