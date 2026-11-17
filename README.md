# CS7389K Advanced Robotics and Autonomous Systems

## Assignment 4: Visual Servoing and Bottle Pick-and-Place with YOLO

**Author:** MD Sameer Iqbal Chowdhury

## Introduction

In this assignment, you will give your TurtleBot the ability to see. A camera on the robot sends pictures to a program called YOLO, which finds objects in each picture and draws a labeled box around them. You will then run a ready-made program that uses those boxes to turn the robot toward a bottle, drive up to it, pick it up, and carry it back to where it started.

You are not required to write any code. You will run programs, change a small number of settings, and observe what happens.

**How to use this guide.** Please complete the steps in order, one at a time. Each step begins with a short statement of what you will learn. Each command is followed by an example of the output that you should see, so that you can compare it with your own screen. Small differences, such as numbers, timestamps, and the objects that YOLO detects, are normal.

**Reading the code.** You are encouraged to open the Python files and read the code to understand how each program works. You are not required to change any code, except for the specific changes that this guide asks you to make.

**Getting help.** The Doctoral Instructor Assistant can be contacted only by email at vsj23@txstate.edu. Please do not contact the instructor with questions about the assignments.

---

## Submission Requirements (Please Read Before You Begin)

You will submit **five video clips**. Every step that requires a recording is marked with "Recording required" at the very beginning of the step, so you will always know when to record.

**Rules for all clips**

1. Each clip must be **one continuous recording with no editing**. Please do not cut, trim, speed up, or join any parts. If something goes wrong during a clip, please record the whole clip again from the beginning.
2. Please film the clips with a phone or a camera. The film must show the computer screen and the robot at the same time, while one team member narrates what is happening.
3. At the beginning of Clip 1, please show the face of every team member and say each member's name.
4. Please name every clip with the convention `Assignment4_Group<number>_Clip<number>`. For example, the second clip of Group 2 is named `Assignment4_Group2_Clip2`.
5. Please upload each clip to YouTube and set its visibility to **Unlisted**. Please use the clip name as the video title. Please do not upload the raw video files to Canvas.
6. **Every team member** must paste all five links into Canvas under **Assignment 4**, even if the team recorded the clips together.
7. Source code is **not** required for this assignment.

**The five clips**

| Clip | File name (Group 2 as an example) | What the clip must show |
| --- | --- | --- |
| 1 | `Assignment4_Group2_Clip1` | The faces and names of all team members, YOLO detecting several objects on the Jetson camera, and the `tegrastats` window showing that the GPU is working. |
| 2 | `Assignment4_Group2_Clip2` | The YOLO publisher and the YOLO subscriber running at the same time, with the subscriber printing the objects that the camera sees. |
| 3 | `Assignment4_Group2_Clip3` | The robot keeping a slowly moving bottle in the center of its view by turning left and right. |
| 4 | `Assignment4_Group2_Clip4` | The robot facing the bottle, driving to it, grabbing it, and lifting it, while the narrator explains which settings were tuned and why. |
| 5 | `Assignment4_Group2_Clip5` | The robot picking up the bottle, returning near its starting position, and placing the bottle on the ground. |

---

## Step 1: Watch a Video About Docker

**What you will learn:** You will learn what a Docker container is. This step is optional, because you already studied Docker in Assignment 1. Please skip it if you remember the idea.

Please watch the following video if you would like a short reminder: <https://www.youtube.com/watch?v=Gjnup-PuquQ>

A Docker container is like a small, separate computer that runs inside your laptop. All of the robot software for the laptop is installed inside it.

---

## Step 2: Understand the Two Computers You Will Use

**What you will learn:** You will learn which computer you are typing on in each step. Knowing this prevents most of the mistakes that students make in this assignment.

This assignment uses two separate computers, and each step in this guide begins by telling you which one to use.

- The **Jetson** is the small computer that is mounted on the robot. It is connected to the camera and runs the YOLO program. You type on it in an ordinary terminal, without Docker.
- The **Remote PC** is your laptop. It sends driving commands to the robot from a distance. You type on it either in an ordinary terminal or inside the Docker container that you built in Assignment 1, and each step tells you which one to use.

The two computers send messages to each other over the network. Therefore, both of them must be connected to the same wifi network, `small_blue_wifi`, exactly as in Assignment 3.

---

## Step 3: Read About YOLO11

**What you will learn:** You will learn what YOLO11 is and what kinds of objects it can recognize.

Please read the following page about the YOLO11 model: <https://docs.ultralytics.com/models/yolo11>

YOLO stands for "You Only Look Once". It finds and names many objects in a picture in a single quick pass, which is fast enough for live video. YOLO11 was trained on a collection of photographs called COCO, so it only knows the 80 kinds of objects in that collection. It sometimes names an object incorrectly, for example by calling a teddy bear a donut.

---

## Step 4: Monitor the Jetson's Workload

**What you will learn:** You will learn how to check whether the Jetson's graphics chip (the GPU) is working. You will use this later as proof that YOLO runs on the GPU.

Please perform this step on the **Jetson**. Please open a terminal and keep it open for the whole assignment.

The following command shows the load on the Jetson's processor and GPU once per second. It is needed because it lets you see how hard the Jetson is working while YOLO runs. Please copy and paste the following command and run it:

```bash
tegrastats
```

Then you will see something like this, with one new line every second:

```text
RAM 2874/7773MB (lfb 4x4MB) SWAP 0/3886MB CPU [12%@1190,8%@1190,5%@1190,6%@1190,off,off] GR3D_FREQ 0% ...
```

In this output, `CPU` shows how busy the processor is, and `GR3D_FREQ` shows how busy the GPU is. When YOLO is running, the `GR3D_FREQ` value should rise.

---

## Step 5: Download the Assignment Files

**What you will learn:** You will learn where the assignment files are stored on each computer. The Jetson runs the camera and YOLO, and the Remote PC runs the robot's driving program, so both computers need the files.

Please perform the first part of this step on the **Jetson**. Please open a **second** terminal. The following two lines first move to your home folder and then download the assignment repository from GitHub. Please copy and paste them and run them:

```bash
cd ~/
git clone https://github.com/MSIChowdhury/Robotics_Assignment_4.git
```

Then you will see something like this:

```text
Cloning into 'Robotics_Assignment_4'...
remote: Enumerating objects: 40, done.
Receiving objects: 100% (40/40), 18.2 MiB | 6.1 MiB/s, done.
```

Please perform the second part of this step on the **Remote PC**. Please open an ordinary terminal on your laptop (not inside Docker). The following two lines move into the folder that Docker shares with your laptop and download the same repository there. Anything in `~/turtlebot_docker/my_code` on the laptop appears as `~/my_code` inside Docker. Please copy and paste them and run them:

```bash
cd ~/turtlebot_docker/my_code
git clone https://github.com/MSIChowdhury/Robotics_Assignment_4.git
```

Then you will see something like this:

```text
Cloning into 'Robotics_Assignment_4'...
remote: Enumerating objects: 40, done.
Receiving objects: 100% (40/40), 18.2 MiB | 6.1 MiB/s, done.
```

---

## Step 6: Run the YOLO Demonstration

**What you will learn:** You will learn how YOLO detects objects on the robot's own camera. You should also repeat this step every time before you use the camera in later steps, because it confirms that the camera and the GPU are working. If this demonstration fails, the problem is the camera hardware and not your later steps.

Please perform this step on the **Jetson**. The following two lines move into the folder that contains the demonstration and then start it. Please copy and paste them and run them:

```bash
cd ~/Robotics_Assignment_4/Assignment_4_demo/CUDA_Demo
python3 yolov11_demo.py
```

Please point the robot's camera at a few objects, such as a person, a bottle, and a laptop. When you are finished, please press the `Esc` key while the video window is selected to close it.

Then you will see a video window with a box and a label around each object, for example `bottle 0.87` or `person 0.92`. The number is how confident YOLO is, where 1.00 means completely confident. In the `tegrastats` window from Step 4, you will see the GPU value rise, for example:

```text
GR3D_FREQ 62% ...
```

You are encouraged to open `yolov11_demo.py` and read it. You are not required to change anything in it for this step.

---

## Step 7: Try a Different YOLO Model Size

**What you will learn:** You will learn that bigger YOLO models are usually more accurate but slower, and that the robot needs fast reactions. This step is optional, and you may skip it if you are short on time.

Please perform this step on the **Jetson**. YOLO11 comes in five sizes. Please choose one from the following list:

| Size | Name for `PT` | Name for `ENGINE` | Parameters (approximate) |
| --- | --- | --- | --- |
| Nano (the default) | `yolo11n.pt` | `yolo11n.engine` | 2.6 million |
| Small | `yolo11s.pt` | `yolo11s.engine` | 9.4 million |
| Medium | `yolo11m.pt` | `yolo11m.engine` | 20 million |
| Large | `yolo11l.pt` | `yolo11l.engine` | 25 million |
| Extra large | `yolo11x.pt` | `yolo11x.engine` | 57 million |

The Nano model is the fastest and the least accurate. Each larger model is more accurate but slower, and the Extra large model is the slowest on the Jetson.

Please open `yolov11_demo.py` in a text editor, for example by running the following command. The command opens the file in the `nano` editor, which lets you change the file directly in the terminal. After you make your change, please press `Ctrl+O` and then `Enter` to save, and then `Ctrl+X` to leave the editor.

```bash
nano ~/Robotics_Assignment_4/Assignment_4_demo/CUDA_Demo/yolov11_demo.py
```

Please find the following two lines:

```python
ENGINE = "yolo11n.engine"
PT     = "yolo11n.pt"
```

Please change **both** names to the same size. For example, to try the Small model, the lines become:

```python
ENGINE = "yolo11s.engine"
PT     = "yolo11s.pt"
```

The following command runs the demonstration again with your chosen size. Please copy and paste it and run it:

```bash
cd ~/Robotics_Assignment_4/Assignment_4_demo/CUDA_Demo && python3 yolov11_demo.py
```

Then you will see something like this. The first run of a new size takes a few minutes, because the program downloads the `.pt` file and converts it into an `.engine` file. Later runs start quickly, because the `.engine` file then already exists.

```text
[INFO] yolo11s.engine not found, exporting from yolo11s.pt …
Downloading https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11s.pt to 'yolo11s.pt'...
...
```

After the video window opens, please compare it with the Nano model. How smooth is the video, and how high does the `GR3D_FREQ` value go in `tegrastats`? When you are finished, please change both names back to `yolo11n`.

---

## Step 8: Record Clip 1 (YOLO on the Jetson)

**Recording required:** Please record this step as one continuous video without editing. Please name the clip `Assignment4_Group<number>_Clip1`, for example `Assignment4_Group2_Clip1`.

**What you will learn:** You will practice explaining what YOLO does, and you will show that the detection runs on the GPU.

Please film the computer screen and the robot with a phone or a camera, while one team member narrates. **At the very beginning of the clip, please show the face of every team member and say each member's name.**

The following two lines run the YOLO demonstration again. Please copy and paste them and run them while you are filming:

```bash
cd ~/Robotics_Assignment_4/Assignment_4_demo/CUDA_Demo
python3 yolov11_demo.py
```

Please point the robot's camera at several objects, for example a person, a bottle, and a laptop. Please keep the `tegrastats` window visible next to the video window, and please describe aloud what you see.

Then you will see boxes and labels on the objects, and the `GR3D_FREQ` value in `tegrastats` will rise while the model runs. This is your proof that the GPU is doing the work. The clip should be about one minute long.

---

## Step 9: Start the YOLO Publisher

**What you will learn:** You will learn what a publisher is. A publisher is a program that continuously sends information to other programs. This one sends a short text message describing every object that YOLO sees, about 20 times per second, on a channel named `/yolo/detections_json`.

Please perform this step on the **Jetson**. The following two lines move into the repository folder and start the publisher. The publisher reads the camera, runs YOLO, and sends out the results. Please copy and paste them and run them:

```bash
cd ~/Robotics_Assignment_4
python3 yolo_publisher_sample_code.py
```

The first time that you run it, the program must download the model weights, so the Jetson needs an internet connection and the step takes longer. Afterward, you can reconnect the Jetson to `small_blue_wifi`.

Then you will see something like this. Many lines about the camera will scroll past, which is normal.

```text
[INFO] [1774133694.824883296] [yolo_json_publisher]: Loading YOLOv11 model on CUDA...
Downloading https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11n.pt to 'yolo11n.pt'...
100%|██████████████████████████████████████| 5.35M/5.35M [00:00<00:00, 9.65MB/s]
[INFO] [1774133708.662359424] [yolo_json_publisher]: Initializing CSI Camera...
GST_ARGUS: Creating output stream
CONSUMER: Producer has connected; continuing.
```

You are encouraged to open `yolo_publisher_sample_code.py` and read it to see how a publisher is written. You are not required to change it, except in Step 11.

---

## Step 10: Start the YOLO Subscriber

**What you will learn:** You will learn what a subscriber is and how to read its output. A subscriber is a program that listens to a channel and receives whatever a publisher sends.

Please perform this step on the **Jetson**. Please leave the publisher running and open a **new** terminal. The following two lines move into the repository folder and start the subscriber, which listens to the `/yolo/detections_json` channel and prints what it receives. Please copy and paste them and run them, and then point the camera at a few objects:

```bash
cd ~/Robotics_Assignment_4
python3 yolo_subscriber_sample_code.py
```

Then you will see something like this, with one block of lines for every camera picture:

```text
[INFO] [1774133827.058645760] [yolo_json_subscriber]: Listening for YOLO JSON detections...
[INFO] [1774133827.062601856] [yolo_json_subscriber]: Received 1 detections at t=1774133826.99 [camera_link]:
[INFO] [1774133827.064806720] [yolo_json_subscriber]:   [0] bottle (0.87) | Center: (689.2, 239.0), Size: 180.4x412.7
```

The last line can be read as follows:

- `bottle (0.87)` is the name of the object that YOLO sees and how confident YOLO is.
- `Center: (689.2, 239.0)` is the position of the middle of the box in pixels. The picture is 1280 pixels wide, so the middle of the picture is at 640.
- `Size: 180.4x412.7` means that the box is about 180 pixels wide and 412 pixels tall. **The taller the box is, the closer the object is.** The robot will use exactly this information to find the bottle and to decide when it is close enough.

You are encouraged to open `yolo_subscriber_sample_code.py` and read it. You are not required to change it.

---

## Step 11: Change the Publisher's Settings

**What you will learn:** You will learn that the same program can be made faster or more accurate by changing a single value.

Please perform this step on the **Jetson**. First, please stop the publisher by pressing `Ctrl+C` in its terminal. Then please open the publisher file in a text editor. The following command opens it in `nano`, using the same saving method as in Step 7:

```bash
nano ~/Robotics_Assignment_4/yolo_publisher_sample_code.py
```

Please find the settings block near the top of the file:

```python
MODEL_PATH = 'yolo11n.pt'
PUBLISH_PERIOD = 0.05
```

Please change **one** value at a time, start the publisher again with the command in Step 9, and watch the subscriber and `tegrastats`. The following suggestions explain what each value does:

- `MODEL_PATH = 'yolo11n.engine'` selects an optimized version of the model, which starts faster and uses less of the GPU. Before you use it for the first time, please run the following command. It copies the optimized file from the demonstration folder into the folder that contains the publisher.

```bash
cp ~/Robotics_Assignment_4/Assignment_4_demo/CUDA_Demo/yolo11n.engine ~/Robotics_Assignment_4/
```

- `MODEL_PATH = 'yolo11s.pt'` selects the larger Small model, which is usually more accurate but slower.
- `PUBLISH_PERIOD = 0.2` makes the publisher send 5 messages per second instead of 20, so the subscriber prints less often.

Then you will see the same kind of output as in Step 10, but faster, slower, or different depending on your change. When you use an `.engine` file, you will also see some lines that begin with `[TRT]` and a note that the program assumes `task=detect`. This is normal.

---

## Step 12: Record Clip 2 (Publisher and Subscriber)

**Recording required:** Please record this step as one continuous video without editing. Please name the clip `Assignment4_Group<number>_Clip2`, for example `Assignment4_Group2_Clip2`.

**What you will learn:** You will show that two separate programs can share information with each other through ROS 2, which is the same way that the robot's driving program will receive the position of the bottle.

Please film the computer screen and the robot with a phone or a camera, while one team member narrates. Please start the publisher in one terminal, and then start the subscriber in a second terminal, with the two terminals side by side on the screen. Please copy and paste the following command for the publisher and run it:

```bash
cd ~/Robotics_Assignment_4 && python3 yolo_publisher_sample_code.py
```

Then please copy and paste the following command in the second terminal for the subscriber and run it:

```bash
cd ~/Robotics_Assignment_4 && python3 yolo_subscriber_sample_code.py
```

Please point the robot's camera at several objects, for example a person, a bottle, and a laptop, and please explain aloud what each of the two programs does.

Then you will see the subscriber printing the objects that the publisher's camera sees.

---

## Step 13: Understand How the Robot Finds the Bottle

**What you will learn:** You will learn that a robot can complete a real task using only two pieces of information: where the object is (the center of its box) and how close the object is (the height of its box). You will tune a few numbers that control each of these.

Please read the following description of how the ready-made program `bottle_pick_place.py` works. You do not need to understand every line of its code, but you are encouraged to open it and read it.

1. The program listens to the YOLO channel from Step 10 and looks for a bottle.
2. If the center of the bottle's box is to the left or to the right of the middle of the picture, the program turns the wheels to bring the bottle back to the middle. This technique is called **visual servoing**.
3. When the bottle is in the middle, the program drives forward until the box is tall enough, which means that the bottle is close.
4. The program then moves the arm to the home pose, opens the gripper, reaches forward, closes the gripper, and pulls the arm back to the home pose with the bottle lifted.
5. To place the bottle, the program drives back to the point where it started, using the wheel sensors, extends the arm, opens the gripper, and pulls the arm back.

---

## Step 14: Start the Robot

**What you will learn:** You will learn which programs must be running before the driving program can work. The robot's drivers allow programs to move the wheels and the arm, and the publisher keeps sending what the camera sees.

Please perform this step on the **Jetson**. Please make sure that there is free space around the robot, and please close any programs from the earlier steps. The following command starts the robot's drivers. It is the same command that you used in Assignment 3. Please copy and paste it and run it in a terminal:

```bash
ros2 launch turtlebot3_manipulation_bringup hardware.launch.py
```

Then you will see many lines of text, and none of them should be a red `ERROR`. The output will look something like this:

```text
[INFO] [launch]: All log files can be found below /home/nvidia/.ros/log/...
[ros2_control_node-1] [INFO] ...: Successfully loaded controller arm_controller
[ros2_control_node-1] [INFO] ...: Successfully loaded controller gripper_controller
```

Next, please open a **second** terminal on the Jetson. The following command starts the YOLO publisher again, which the driving program needs. Please copy and paste it and run it:

```bash
cd ~/Robotics_Assignment_4 && python3 yolo_publisher_sample_code.py
```

Please leave both terminals running for the remaining steps.

---

## Step 15: Reuse Your Assignment 3 Values

**What you will learn:** You will learn how to reuse the work that you already did. In Assignment 3, you found the arm poses and the gripper values that work for your robot. The driving program needs the same four values, so you do not have to find them again.

Please perform this step on the **Remote PC**. First, please open a terminal inside the Docker container. The following two commands start the container if it is not already running and then open a terminal inside it. If the container is already running, running the first command again does no harm. Please copy and paste them one after the other:

```bash
cd ~/turtlebot_docker && HOST_UID=$(id -u) USER_HOME=$HOME docker compose up -d
```

```bash
docker exec -it remote_pc_humble bash
```

Next, the following command reads the four values from your own Assignment 3 file, `sample_code.py`, and prints them in exactly the form that the driving program needs. Please copy and paste it and run it inside the Docker terminal:

```bash
cd ~/my_code && python3 -c "import sample_code as a; print('HOME_POSE =', a.POSES['9']); print('EXTEND_POSE =', a.POSES['0']); print('GRIPPER_OPEN =', a.GRIPPER_KEY_BINDINGS['g']); print('GRIPPER_CLOSE =', a.GRIPPER_KEY_BINDINGS['h'])"
```

Then you will see something like this. Your numbers will be different, and you should use your own numbers.

```text
HOME_POSE = [0.0, 0.0, 0.0, 0.0]
EXTEND_POSE = [0.0, 0.9, 0.0, 0.5]
GRIPPER_OPEN = 0.01
GRIPPER_CLOSE = -0.01
```

If you see `KeyError: '0'`, your Assignment 3 file does not yet contain the "extend arm forward" pose, so please add it to your Assignment 3 file first. If you see `No module named 'sample_code'`, your Assignment 3 file is stored in a different folder, so please change the folder name after `cd` to the folder that contains it.

Now please open the driving program in a text editor. The following command opens it in `nano`, using the same saving method as in Step 7. Please copy and paste it and run it in an ordinary terminal on the laptop, not in Docker:

```bash
nano ~/turtlebot_docker/my_code/Robotics_Assignment_4/bottle_pick_place.py
```

Please find the following four placeholder lines in the settings block:

```python
HOME_POSE = [0.0, 0.0, 0.0, 0.0]
EXTEND_POSE = [0.0, 0.9, 0.0, 0.5]
GRIPPER_OPEN = 0.01
GRIPPER_CLOSE = -0.01
```

Please replace these four lines with the four lines that were printed on your screen. These are the only changes that you must make to the file at this point. The values that are in the file now are only placeholders.

---

## Step 16: Find the "Close Enough" Box Height

**What you will learn:** You will learn how the robot decides when to stop driving. A taller box means a closer bottle, so the robot stops when the box reaches a height that you choose.

Please perform the first part of this step on the **Jetson**. Please make sure that the YOLO publisher from Step 14 is still running. Please open a **third** terminal on the Jetson and start the subscriber. The following command starts it. Please copy and paste it and run it:

```bash
cd ~/Robotics_Assignment_4 && python3 yolo_subscriber_sample_code.py
```

Please hold the bottle at the distance from which the robot's gripper could grab it, and please read the second number after `Size`. Then you will see something like this:

```text
[INFO] [...] [yolo_json_subscriber]:   [0] bottle (0.89) | Center: (640.0, 360.0), Size: 210.5x430.2
```

In this example, the height is about 430. Please press `Ctrl+C` to close the subscriber.

Please perform the second part of this step on the **Remote PC**. Please open `bottle_pick_place.py` again with the `nano` command from Step 15, find the following line, and set it to a number that is slightly smaller than the height that you measured. For example, if you measured about 430, you can use 400:

```python
STOP_BBOX_HEIGHT = 400
```

---

## Step 17: Run Stage 1 (Turning Toward the Bottle)

**What you will learn:** You will learn how the robot compares the center of the bottle with the middle of the picture and turns its wheels to reduce the difference. In this first stage, the robot only turns. It does not drive forward.

Please perform this step on the **Remote PC**, inside the Docker terminal from Step 15. Please make sure that the setting `STAGE = "servo"` appears in `bottle_pick_place.py`, which is the default. The following two lines move into the folder that contains the driving program and start it. Please copy and paste them and run them, then place the bottle in front of the robot and move it slowly to the left and to the right. You can press `Ctrl+C` at any time to stop the robot.

```bash
cd ~/my_code/Robotics_Assignment_4
python3 bottle_pick_place.py
```

Then you will see something like this, and the robot will turn in place to face the bottle:

```text
[INFO] [1780000000.123456789] [bottle_pick_place]: STAGE = servo, looking for ['bottle']
[INFO] [1780000000.223456789] [bottle_pick_place]: Tracking the bottle. Press Ctrl+C to stop.
```

If the robot wobbles or reacts slowly, please see the tuning table in Step 20. You are encouraged to read `bottle_pick_place.py` to see how the turning command is calculated. You are not required to change anything in it other than the settings that this guide mentions.

---

## Step 18: Record Clip 3 (Visual Servoing)

**Recording required:** Please record this step as one continuous video without editing. Please name the clip `Assignment4_Group<number>_Clip3`, for example `Assignment4_Group2_Clip3`.

**What you will learn:** You will show that the robot can use its camera to steer, which is the central idea of visual servoing.

Please film the computer screen, the robot, and the bottle with a phone or a camera, while one team member narrates. The setting `STAGE = "servo"` must be selected. Please copy and paste the following two lines and run them while you are filming:

```bash
cd ~/my_code/Robotics_Assignment_4
python3 bottle_pick_place.py
```

Please move the bottle slowly in front of the robot, and please explain aloud what the robot is doing.

Then you will see the robot lock onto the bottle and keep it in the center of the camera's view by turning left and right.

---

## Step 19: Run Stage 2 (Picking Up the Bottle)

**What you will learn:** You will learn how the same program drives forward and uses the arm and the gripper that you set up in Assignment 3.

Please perform this step on the **Remote PC**. Please open `bottle_pick_place.py` with the `nano` command from Step 15, and please change the stage setting to the following:

```python
STAGE = "pick"
```

Please place the bottle on the ground in front of the robot, slightly to one side of the center. The following two lines start the program. Please copy and paste them and run them. You can press `Ctrl+C` at any time to stop the robot.

```bash
cd ~/my_code/Robotics_Assignment_4
python3 bottle_pick_place.py
```

Then you will see something like this, and the robot will turn to face the bottle, drive up to it, reach forward, close the gripper, and lift the bottle:

```text
[INFO] [1780000000.123456789] [bottle_pick_place]: STAGE = pick, looking for ['bottle']
[INFO] [1780000000.223456789] [bottle_pick_place]: Waiting for arm and gripper controllers and odometry...
[INFO] [1780000001.323456789] [bottle_pick_place]: Start point recorded at x=0.00 y=0.00
[INFO] [1780000001.423456789] [bottle_pick_place]: Arm to home pose, gripper open.
[INFO] [1780000009.423456789] [bottle_pick_place]: Tracking the bottle. Press Ctrl+C to stop.
[INFO] [1780000024.523456789] [bottle_pick_place]: Picking up the bottle.
[INFO] [1780000036.623456789] [bottle_pick_place]: Pick complete.
```

If the robot does not behave well, please continue to Step 20.

---

## Step 20: Tune the Settings if Needed

**What you will learn:** You will learn that real robots need tuning. Changing one number at a time and observing the result is how engineers find good values. This step is only needed if the robot does not behave well, so you may skip it if the robot already works.

Please perform this step on the **Remote PC**. Please open `bottle_pick_place.py` with the `nano` command from Step 15. Please change **one** value at a time in the settings block, save the file, and run the program again with the command from Step 19. The following table lists common problems and the setting that usually fixes each of them.

| What the robot does | What to change |
| --- | --- |
| The robot wobbles left and right around the bottle. | Please lower `TURN_GAIN`, or raise `CENTER_TOLERANCE_PX`. |
| The robot reacts slowly or lags behind the bottle. | Please raise `TURN_GAIN`. |
| The robot stops too far from the bottle or too close to it. | Please change `STOP_BBOX_HEIGHT`, using the measurement method in Step 16. |
| The robot drives too fast to follow the bottle. | Please lower `FORWARD_VEL`. |
| The gripper misses the bottle or crushes it. | Please adjust `EXTEND_POSE` and `GRIPPER_CLOSE`, starting from your Assignment 3 values. |
| YOLO names the bottle as another object. | Please add the other name to `TARGET_CLASSES`, for example `["bottle", "vase"]`. |
| The detections flicker on and off. | Please raise `MIN_CONFIDENCE`. |
| The robot does not return to its starting point in Step 22. | Please change `RETURN_VEL` or `HOME_TOLERANCE`. |

Then you will see the robot's behavior improve. Please write down which values you changed and why, because you will be asked to explain them in the next clip.

---

## Step 21: Record Clip 4 (Picking Up the Bottle)

**Recording required:** Please record this step as one continuous video without editing. Please name the clip `Assignment4_Group<number>_Clip4`, for example `Assignment4_Group2_Clip4`.

**What you will learn:** You will practice explaining your choices, which is as important as having a robot that works.

Please film the computer screen, the robot, and the bottle with a phone or a camera, while one team member narrates. The setting `STAGE = "pick"` must be selected. Please place the bottle on the ground in the camera's view, slightly to one side of the center. Please copy and paste the following two lines and run them while you are filming:

```bash
cd ~/my_code/Robotics_Assignment_4
python3 bottle_pick_place.py
```

While the robot works, please say aloud which settings you tuned and why you tuned them.

Then you will see the robot face the bottle, drive to it, reach out, grab it, and lift it off the ground.

---

## Step 22: Run Stage 3 (Picking Up and Placing the Bottle)

**What you will learn:** You will learn that the robot remembers its starting point using its wheel sensors, which is called odometry, and that it can drive back to that point. The wheel sensors drift slightly, so the robot may not return to exactly the same place.

Please perform this step on the **Remote PC**. Please open `bottle_pick_place.py` with the `nano` command from Step 15, and please change the stage setting to the following:

```python
STAGE = "full"
```

Please keep the path in front of the robot clear and be ready to press `Ctrl+C`. The following two lines start the program. Please copy and paste them and run them:

```bash
cd ~/my_code/Robotics_Assignment_4
python3 bottle_pick_place.py
```

Then you will see everything from Step 19, followed by the following lines, as the robot drives back and puts the bottle down:

```text
[INFO] [1780000036.623456789] [bottle_pick_place]: Returning to the start point.
[INFO] [1780000052.723456789] [bottle_pick_place]: Placing the bottle.
[INFO] [1780000064.823456789] [bottle_pick_place]: Pick and place complete.
```

If the return takes too long, you will see the following warning instead, and the robot will place the bottle where it is:

```text
[WARN] [...] [bottle_pick_place]: Return timed out, placing the bottle here.
```

---

## Step 23: Record Clip 5 (Picking Up and Placing the Bottle)

**Recording required:** Please record this step as one continuous video without editing. Please name the clip `Assignment4_Group<number>_Clip5`, for example `Assignment4_Group2_Clip5`.

**What you will learn:** You will show the complete task in one recording: seeing the bottle, aiming at it, approaching it, grabbing it, carrying it, and placing it.

Please film the computer screen, the robot, and the bottle with a phone or a camera, while one team member narrates. The setting `STAGE = "full"` must be selected. Please place the bottle on the ground in the camera's view, slightly to one side of the center, in the same way as in Clip 4. Please copy and paste the following two lines and run them while you are filming:

```bash
cd ~/my_code/Robotics_Assignment_4
python3 bottle_pick_place.py
```

Then you will see the robot pick up the bottle, return near its starting position, and put the bottle on the ground.

---

## Step 24: Final Check and Submission

**What you will learn:** You will confirm that you have everything that the assignment requires before you submit.

Please check that each of the following five clips exists, and please tick every box before you submit.

- [ ] **Clip 1** (`Assignment4_Group<number>_Clip1`) shows the faces and names of all team members, YOLO detecting several objects, and the `tegrastats` window with the GPU value rising.
- [ ] **Clip 2** (`Assignment4_Group<number>_Clip2`) shows the publisher and the subscriber running together, with the subscriber printing the objects that the camera sees.
- [ ] **Clip 3** (`Assignment4_Group<number>_Clip3`) shows the setting `STAGE = "servo"`, with the robot keeping a slowly moving bottle in the center by turning left and right.
- [ ] **Clip 4** (`Assignment4_Group<number>_Clip4`) shows the setting `STAGE = "pick"`, with the robot grabbing and lifting the bottle, while the narrator explains the tuned settings and the reasons for them.
- [ ] **Clip 5** (`Assignment4_Group<number>_Clip5`) shows the setting `STAGE = "full"`, with the robot picking up the bottle, returning near its starting position, and placing the bottle on the ground.

Please also confirm the following rules before you upload:

- [ ] Every clip is one continuous recording with no editing.
- [ ] Every clip shows both the computer screen and the robot, with a team member narrating.
- [ ] Every clip is named with the convention `Assignment4_Group<number>_Clip<number>`.

To submit, please upload each clip to YouTube and set its visibility to **Unlisted**, using the clip name as the title. Then every team member must paste all five links into Canvas under **Assignment 4**, even if the team recorded the clips together. Please do not upload the raw video files to Canvas. Source code is **not** required for this assignment.
