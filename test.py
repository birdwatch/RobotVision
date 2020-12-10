import cv2
import copy
import numpy as np

boot = True


class AirHockey():
    _ball_velocity_h = _ball_velocity_w = _left_velocity_h = _left_velocity_w = _right_velocity_h = _right_velocity_w = 0
    # 1 → left(blue)、2 → right(red)
    _ball_color = 0
    _previous_field = _mask = _blue = _red = 0
    _text = ""
    _boot = True

    def __init__(self):
        # 画像データの読み込み
        self._field_img = cv2.imread("./img/field.png")
        self._ball_img = cv2.imread("./img/ball3.png", -1)
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
        self._previous_field = copy.deepcopy(self._field_img)

        self._mask = self._ball_img[:, :, 3]  # アルファチャンネルだけ抜き出す。
        self._mask = cv2.cvtColor(self._mask, cv2.COLOR_GRAY2BGR)  # 3色分に増やす。
        # self._mask = self._mask / 255  # 0-255だと使い勝手が悪いので、0.0-1.0に変更。
        self._ball_img = self._ball_img[:, :, :3]

    # 入力
    def input(self):
        #global boot
        self._left_velocity_h = self._left_velocity_w = self._right_velocity_h = self._right_velocity_w = 0
        key = cv2.waitKey(1)
        if key == ord("q"):
            self._boot = False
        elif key == ord("w"):
            self._idx_right_h -= 10
            self._right_velocity_h = -5
        elif key == ord("s"):
            self._idx_right_h += 10
            self._right_velocity_h = 5
        elif key == ord("a"):
            self._idx_right_w -= 10
            self._right_velocity_w = -5
        elif key == ord("d"):
            self._idx_right_w += 10
            self._right_velocity_w = 5

    def set_left_velocity(self, x, y):
        self._left_velocity_h = x
        self._left_velocity_w = y

    def set_right_velocity(self, x, y):
        self._right_velocity_w = x
        self._right_velocity_h = y

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

    # 衝突判定
    def collision_detect(self):
        # 左プレイヤーとボールの衝突
        if abs(self._idx_left_h - self._idx_ball_h) < self._left_h + self._ball_h and abs(self._idx_left_w - self._idx_ball_w) < self._left_w + self._ball_w:
            self._ball_color = 1
            # ボールが上
            if self._ball_velocity_h >= 0 and self._idx_ball_h < self._idx_left_h and abs(self._idx_right_w - self._idx_ball_w) < self._left_w:
                self._idx_ball_h = self._idx_left_h - self._left_h - self._ball_h - 1
                self._ball_velocity_w = self._ball_velocity_w + self._left_velocity_w
                self._ball_velocity_h = -self._ball_velocity_h + self._left_velocity_h
                if self._idx_ball_h - self._ball_h < 1:
                    self._idx_left_h = self._ball_img.shape[0] + self._left_h
                    self._idx_ball_h = self._ball_h + 1
                    self._ball_velocity_h = 0
            # ボールが下
            elif self._ball_velocity_h <= 0 and self._idx_ball_h > self._idx_left_h and abs(self._idx_right_w - self._idx_ball_w) < self._left_w:
                self._idx_ball_h = self._idx_left_h + self._left_h + self._ball_h + 1
                self._ball_velocity_w = self._ball_velocity_w + self._left_velocity_w
                self._ball_velocity_h = -self._ball_velocity_h + self._left_velocity_h
                if self._idx_ball_h + self._ball_h > self._field_img.shape[0]:
                    self._idx_left_h = self._field_img.shape[0] - \
                        self._ball_img.shape[0] - self._left_h - 2
                    self._idx_ball_h = self._field_img.shape[0] - \
                        self._ball_h
                    self._ball_velocity_h = 0
            elif self._ball_velocity_w <= 0 and self._idx_ball_w > self._idx_left_w:  # ボールが右
                self._idx_ball_w = self._idx_left_w + self._left_w + self._ball_w + 1
                self._ball_velocity_w = -self._ball_velocity_w + self._left_velocity_w
                self._ball_velocity_h = self._ball_velocity_h + self._left_velocity_h
            elif self._ball_velocity_w >= 0 and self._idx_ball_w < self._idx_left_w:  # ボールが左
                self._idx_ball_w = self._idx_left_w - self._left_w - self._ball_w - 1
                self._ball_velocity_w = -self._ball_velocity_w + self._left_velocity_w
                self._ball_velocity_h = self._ball_velocity_h + self._left_velocity_h
                if self._idx_ball_w - self._ball_w < 1:
                    self._idx_left_w = self._ball_img.shape[1] + self._left_w
                    self._idx_ball_w = self._ball_h + 1
                    self._ball_velocity_w = 0

        # 右プレイヤーとボールの衝突
        if abs(self._idx_right_h - self._idx_ball_h) < self._right_h + self._ball_h and abs(self._idx_right_w - self._idx_ball_w) < self._right_w + self._ball_w:
            self._ball_color = 2
            # ボールが上
            if self._ball_velocity_h >= 0 and self._idx_ball_h < self._idx_right_h and abs(self._idx_right_w - self._idx_ball_w) < self._right_w + 5:
                print(self._ball_velocity_h)
                self._idx_ball_h = self._idx_right_h - self._right_h - self._ball_h - 1
                self._ball_velocity_w = self._ball_velocity_w + self._right_velocity_w
                self._ball_velocity_h = -self._ball_velocity_h + self._right_velocity_h
                if self._idx_ball_h - self._ball_h < 5 and not self._ball_velocity_h == 0:
                    self._idx_right_h = self._ball_img.shape[0] + \
                        self._right_h + 1
                    self._idx_ball_h = self._ball_h + 1
                    self._ball_velocity_h = 0
            # ボールが下
            elif self._ball_velocity_h <= 0 and self._idx_ball_h > self._idx_right_h and abs(self._idx_right_w - self._idx_ball_w) < self._right_w + 5:
                self._idx_ball_h = self._idx_right_h + self._right_h + self._ball_h + 1
                self._ball_velocity_w = self._ball_velocity_w + self._right_velocity_w
                self._ball_velocity_h = -self._ball_velocity_h + self._right_velocity_h
                if self._idx_ball_h + self._ball_h > self._field_img.shape[0]:
                    self._idx_right_h = self._field_img.shape[0] - \
                        self._ball_img.shape[0] - self._right_h - 2
                    self._idx_ball_h = self._field_img.shape[0] - self._ball_h
                    self._ball_velocity_h = 0
            elif self._ball_velocity_w >= 0 and self._idx_ball_w < self._idx_right_w:  # ボールが左
                self._idx_ball_w = self._idx_right_w - self._right_w - self._ball_w - 1
                self._ball_velocity_w = -self._ball_velocity_w + self._right_velocity_w
                self._ball_velocity_h = self._ball_velocity_h + self._right_velocity_h
            elif self._ball_velocity_w <= 0 and self._idx_ball_w > self._idx_right_w:  # ボールが右
                self._idx_ball_w = self._idx_right_w + self._right_w + self._ball_w + 1
                self._ball_velocity_w = -self._ball_velocity_w + self._right_velocity_w
                self._ball_velocity_h = self._ball_velocity_h + self._right_velocity_h
                if self._idx_ball_w + self._ball_w > self._field_img.shape[1]:
                    self._idx_right_w = self._field_img.shape[1] - \
                        self._ball_img.shape[1] - self._right_w - 2
                    self._idx_ball_w = self._field_img.shape[1] - \
                        self._ball_w - 2
                    self._ball_velocity_w = 0

        self._idx_ball_h += self._ball_velocity_h
        self._idx_ball_w += self._ball_velocity_w

        global boot

        # ボールと壁の衝突
        if self._idx_ball_h - self._ball_h < 1:
            self._idx_ball_h = self._ball_h + 1
            self._ball_velocity_h = -self._ball_velocity_h
        if self._idx_ball_h + self._ball_h > self._field_img.shape[0]:
            self._idx_ball_h = self._field_img.shape[0] - self._ball_h
            self._ball_velocity_h = -self._ball_velocity_h
        if self._idx_ball_w - self._ball_w < 1:
            if self._idx_ball_h < 600 and self._idx_ball_h > 400:
                print("game end")
                self._boot = False
            self._idx_ball_w = self._ball_w
            self._ball_velocity_w = -self._ball_velocity_w
        if self._idx_ball_w + self._ball_w > self._field_img.shape[1]:
            if self._idx_ball_h < 600 and self._idx_ball_h > 400:
                print("game end")
                self._boot = False
            self._idx_ball_w = self._field_img.shape[1] - self._ball_w
            self._ball_velocity_w = -self._ball_velocity_w

    # 毎フレームの画像の生成
    def img_generate(self):
        #self._ball_velocity_h = int(self._ball_velocity_w * 0.97)
        #self._ball_velocity_w = int(self._ball_velocity_w * 0.99)
        if self._ball_color != 0:
            if self._ball_color == 1:
                cv2.circle(self._previous_field, (self._idx_ball_w,
                                                  self._idx_ball_h), 70, (255, 0, 0), -1)
            elif self._ball_color == 2:
                cv2.circle(self._previous_field, (self._idx_ball_w,
                                                  self._idx_ball_h), 70, (0, 0, 255), -1)
        self._frame = copy.deepcopy(self._previous_field)
        # self._frame[(self._idx_ball_h - self._ball_h - 1): (self._idx_ball_h + self._ball_h), (self._idx_ball_w -
        # self._ball_w): (self._idx_ball_w + self._ball_w)] *= (1.0 - self._mask)  # 透過率に応じて元の画像を暗くする。
        self._frame[(self._idx_ball_h - self._ball_h - 1): (self._idx_ball_h + self._ball_h), (self._idx_ball_w - self._ball_w): (self._idx_ball_w + self._ball_w)] += self._ball_img * \
            self._mask  # 貼り付ける方の画像に透過率をかけて加算。
        self._frame[
            (self._idx_left_h - self._left_h): (self._idx_left_h + self._left_h), (self._idx_left_w - self._left_w - 1): (self._idx_left_w + self._left_w)
        ] = self._left_img
        self._frame[
            (self._idx_right_h - self._right_h): (self._idx_right_h + self._right_h), (self._idx_right_w - self._right_w - 1): (self._idx_right_w + self._right_w)
        ] = self._right_img

    # 表示
    def show(self):
        cv2.imshow("game", self._frame)

    def result_show(self):
        print(self._previous_field.shape)
        for i in range(self._previous_field.shape[0]-1):
            for j in range(self._previous_field.shape[1]-1):
                if self._previous_field[i, j, 2] == 255:
                    self._red += 1
                if self._previous_field[i, j, 0] == 255:
                    self._blue += 1
        if self._blue > self._red:
            self._text = "blue win"
        elif self._red > self._blue:
            self._text = "red win"
        else:
            self._text = "draw"
        cv2.putText(
            self._previous_field,
            self._text,
            (100, 450),
            cv2.FONT_HERSHEY_PLAIN,
            20,
            (0, 0, 0),
            10,
        )
        cv2.imshow("game", self._previous_field)


game = AirHockey()
while True:
    game.input()
    game.element_revise()
    game.collision_detect()
    game.img_generate()
    game.show()
    if not boot:
        break

game.result_show()
cv2.waitKey(0)
