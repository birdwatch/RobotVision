import cv2
import copy
import numpy as np

boot = True


class AirHockey():
    def __init__(self):
        # 画像データの読み込み
        self._field_img = cv2.imread("./img/field.png")
        self._ball_img = cv2.imread("./img/boll.png")
        self._left_img = cv2.imread("./img/left.png")
        self._right_img = cv2.imread("./img/right.png")

        # それぞれの要素の高さ、幅の取得
        self._ball_h, self._ball_w = self._ball_img.shape[0] // 2, self._ball_img.shape[1] // 2
        self._left_h, self._left_w = self._left_img.shape[0] // 2, self._left_img.shape[1] // 2
        self._right_h, self._right_w = self._right_img.shape[0] // 2, self._right_img.shape[1] // 2

        # それぞれの要素の中心位置
        self._idx_ball_h, self._idx_ball_w = self._field_img.shape[
            0] // 2, self._field_img.shape[1] // 2
        self._idx_left_h, self._idx_left_w = self._field_img.shape[
            0] // 2, self._field_img.shape[1] // 2 - 700
        self._idx_right_h, self._idx_right_w = self._field_img.shape[
            0] // 2, self._field_img.shape[1] // 2 + 700

        # 毎フレーム表示する画像
        self._frame = copy.deepcopy(self._field_img)

    # 入力
    def input(self):
        global boot
        key = cv2.waitKey(1)
        if key == ord("q"):
            boot = False
        elif key == ord("w"):
            self._idx_right_h -= 10
        elif key == ord("s"):
            self._idx_right_h += 10
        elif key == ord("a"):
            self._idx_right_w -= 10
        elif key == ord("d"):
            self._idx_right_w += 10

    # 各プレーヤーの位置調整
    def element_revise(self):
        # 左側のプレーヤー
        if self._idx_left_h - self._left_h < 0:
            self._idx_left_h = self._left_h
        if self._idx_left_h + self._left_h > self._field_img.shape[0]:
            self._idx_left_h = self._field_img.shape[0] - self._left_h
        if self._idx_left_w - self._left_w < 0:
            self._idx_left_w = self._left_w
        if self._idx_left_w + self._left_w > self._field_img.shape[1] // 2:
            self._idx_left_w = self._field_img.shape[1] // 2 - self._left_w
        # 右側のプレーヤー
        if self._idx_right_h - self._right_h < 0:
            self._idx_right_h = self._right_h
        if self._idx_right_h + self._right_h > self._field_img.shape[0]:
            self._idx_right_h = self._field_img.shape[0] - self._right_h
        if self._idx_right_w - self._right_w < self._field_img.shape[1] // 2:
            self._idx_right_w = self._right_w + self._field_img.shape[1] // 2
        if self._idx_right_w + self._right_w > self._field_img.shape[1]:
            self._idx_right_w = self._field_img.shape[1] - self._right_w

    # 毎フレームの画像の生成
    def img_generate(self):
        self._frame[
            (self._idx_ball_h - self._ball_h - 1): (self._idx_ball_h + self._ball_h), (self._idx_ball_w - self._ball_w): (self._idx_ball_w + self._ball_w)
        ] = self._ball_img
        self._frame[
            (self._idx_left_h - self._left_h): (self._idx_left_h + self._left_h), (self._idx_left_w - self._left_w - 1): (self._idx_left_w + self._left_w)
        ] = self._left_img
        self._frame[
            (self._idx_right_h - self._right_h): (self._idx_right_h + self._right_h), (self._idx_right_w - self._right_w - 1): (self._idx_right_w + self._right_w)
        ] = self._right_img

    # 表示
    def show(self):
        cv2.imshow("game", self._frame)
        self._frame = copy.deepcopy(self._field_img)


game = AirHockey()
while True:
    game.input()
    game.element_revise()
    game.img_generate()
    game.show()
    if not boot:
        break
