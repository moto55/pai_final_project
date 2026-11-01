# PAI Final Project

## 概要

Physical AI応用1講座の最終課題として、ROS 2とGazeboを用いた移動ロボットのシミュレーションを作成しました。

車載カメラの画像をROS 2経由で取得し、学習済み物体検出モデルYOLOを用いて人物を検出します。

人物が十分近いと判断した場合はロボットを停止し、人物が通過した後に一定時間安全を確認してから再発進します。

## システム構成

```text
Gazebo
  ↓ 車載カメラ
/front_camera
  ↓
ros_gz_image
  ↓
ROS 2
  ↓
YOLO
  ↓
人物検出・接近判定
  ↓
/cmd_vel
  ↓
Gazebo上の移動ロボット
```

## 主な機能

- Gazebo上の差動二輪ロボット
- 前方カメラによる画像取得
- YOLOによる人物検出
- 人物の検出枠サイズを利用した接近判定
- 人物接近時の自動停止
- 人物通過後の安全確認
- 安全確認後の自動再発進

## AIの利用

Ultralytics YOLOの学習済みモデルを利用し、車載カメラ画像から人物を推論しています。

人物の検出信頼度に加えて、人物のBounding Boxが画像全体に占める割合を計算し、一定以上の場合に「人物が近い」と判断します。

単純な画像処理ではなく、学習済みAIモデルによる物体認識結果をロボット制御へ利用しています。

## 工夫した点

人物を一瞬見失っただけでロボットが即座に再発進すると危険なため、停止後は一定時間安全な状態が続いたことを確認してから再発進するようにしました。

また、Gazebo上の人物をロボット前方で横断させることで、人物の接近・通過・再発進までを連続して確認できるデモ環境を作成しました。

## 使用環境

- Windows 11
- WSL2
- Ubuntu 24.04
- ROS 2 Jazzy
- Gazebo Harmonic
- Python 3
- Ultralytics YOLO
- OpenCV / cv_bridge

## 主なファイル

```text
pai_final/
├── obstacle_world.sdf
├── vehicle_camera.sdf
├── yolo_stop_robot.py
├── yolo_camera.py
└── robot_control.py
```

### obstacle_world.sdf

Gazeboのシミュレーション環境です。移動ロボットと人物Actorを配置しています。

### vehicle_camera.sdf

差動二輪ロボットに前方カメラを追加したモデルです。

### yolo_stop_robot.py

車載カメラ画像をYOLOで推論し、人物の接近状況に応じて前進・停止・再発進を制御します。

### yolo_camera.py

YOLOによる人物検出結果を確認するためのテストプログラムです。

### robot_control.py

ROS 2から移動ロボットへ手動で前進・旋回・停止指令を送るための確認用プログラムです。

## 実行方法

Gazeboを起動します。

```bash
cd ~/pai_final
gz sim obstacle_world.sdf
```

Gazebo上でシミュレーションを再生します。

別のターミナルで、カメラ画像をROS 2へBridgeします。

```bash
ros2 run ros_gz_image image_bridge /front_camera
```

別のターミナルで、ROS 2の速度指令をGazeboへBridgeします。

```bash
ros2 run ros_gz_bridge parameter_bridge /model/vehicle_blue/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist
```

YOLO環境を有効にします。

```bash
cd ~/pai_final
source .venv/bin/activate
```

AI制御プログラムを実行します。

```bash
python3 yolo_stop_robot.py
```

## 動作

人物がいない場合：

```text
No person -> FORWARD
```

人物を検出したが遠い場合：

```text
Person far -> FORWARD
```

人物が近い場合：

```text
PERSON CLOSE -> STOP
```

人物が通過した後：

```text
Path clearing...
```

一定時間安全状態が続くと再び前進します。

## 今後の改善点

現在は人物のBounding Boxサイズから接近状況を推定しています。

今後はDepth CameraやLiDARを組み合わせ、実距離を利用した停止判定を行うことで、より安全で精度の高い制御に発展させることができます。