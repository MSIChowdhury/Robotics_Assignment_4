# CS7389K Advanced Robotics and Autonomous Systems

## Milestone 4: Teaching Your Robot to See and Pick Up a Bottle (YOLO)

**Author:** MD Sameer Iqbal Chowdhury

## What is this assignment?

You will give your TurtleBot **eyes**. A camera and a program called **YOLO** find objects in the picture. Then the robot turns toward a bottle, drives up to it, picks it up, and carries it back. You do not need to write any code. You will run programs, change a few numbers, and watch what happens.

| Tool | What it does |
| --- | --- |
| **YOLO** | Looks at a camera picture and draws a box around each object it knows, with a name tag |
| **Publisher / Subscriber** | One program shouts what YOLO sees. Another program listens |
| **`bottle_pick_place.py`** | The ready-made program that moves the robot toward the bottle |

**How to use this page:** do the steps in order, one at a time. Each step tells you what to do, what you should see, and what you learn. Compare your screen with the "You should see" box. Small differences (numbers, timestamps, which objects it sees) are normal.

Two places are used. **[Jetson]** is the small computer on the robot (type in its normal terminal, no Docker). **[Remote PC]** is your laptop (type inside the Docker container from Assignment 1).

**What you hand in:** 5 short video clips, uploaded to YouTube (Unlisted), with the 5 links pasted into Canvas. The full checklist is in the last step.

Questions? Send a direct message to the Doctoral Instructor Assistant on Slack. Please do not email the instructor about the milestones.

---

## Step 1 (Optional): Watch a video about Docker

**Watch (optional):** <https://www.youtube.com/watch?v=Gjnup-PuquQ>

You already did this in Assignment 1, so skip it if you remember what Docker is.

**What you learn:** A Docker container is like a small, separate computer running inside your laptop. You will use it later for the robot's driving program.

---

## Step 2: Read about YOLO

**Read:** <https://docs.ultralytics.com/>  (the first page is enough)

**What you learn:** YOLO ("You Only Look Once") finds and names many objects in a picture in one quick pass, fast enough to run on live video. It was trained on a set of photos called COCO, so it only knows the 80 kinds of things in that set, and it sometimes names things wrongly (for example a teddy bear as a donut).

---

## Step 3: Watch the Jetson's workload

**Do:** **[Jetson]** Open a terminal and start this. Leave it running for the whole assignment.

```bash
tegrastats
```

**You should see:** one line of numbers every second.

```text
RAM 2874/7773MB (lfb 4x4MB) SWAP 0/3886MB CPU [12%@1190,8%@1190,5%@1190,6%@1190,off,off] GR3D_FREQ 0% ...
```

**What you learn:** `CPU` shows how busy the processor is. `GR3D_FREQ` is how busy the graphics chip (GPU) is. When YOLO runs, `GR3D_FREQ` should jump up. That is your proof that the GPU is doing the work.

---

## Step 4: Download the assignment files

**Do:** **[Jetson]** Open a **second** terminal and download the repo.

```bash
cd ~/
git clone https://github.com/MSIChowdhury/Robotics_Assignment_4.git
```

**You should see:**

```text
Cloning into 'Robotics_Assignment_4'...
remote: Enumerating objects: 40, done.
Receiving objects: 100% (40/40), 18.2 MiB | 6.1 MiB/s, done.
```

**Do:** **[Remote PC]** On your laptop, open a normal terminal (not in Docker) and download the same repo into the folder that Docker shares.

```bash
cd ~/turtlebot_docker/my_code
git clone https://github.com/MSIChowdhury/Robotics_Assignment_4.git
```

**What you learn:** The Jetson runs the camera and YOLO. The laptop will run the driving program, so both need the files. Whatever is in `~/turtlebot_docker/my_code` on the laptop appears as `~/my_code` inside Docker.

---

## Step 5: See YOLO work on the camera

**Do:** **[Jetson]** Go to the demo folder and run the demo. Point the camera at a few objects (a person, a bottle, a laptop). Press `Esc` on the video window to quit.

```bash
cd ~/Robotics_Assignment_4/Assignment_4_demo/CUDA_Demo
python3 yolov11_demo.py
```

**You should see:** a video window with boxes and labels around the objects, like `bottle 0.87` or `person 0.92`. The number is how sure YOLO is (1.00 means very sure). In the `tegrastats` window, `GR3D_FREQ` rises.

```text
GR3D_FREQ 62% ...
```

**What you learn:** YOLO is working on the robot's own camera and GPU. **Run this demo every time before using the camera in later steps.** If it fails, the camera or cable is the problem, not your later steps.

---

## Step 6: Try a different YOLO model size (optional)

**Do:** **[Jetson]** YOLO comes in five sizes. Pick one from the list, open `yolov11_demo.py` and find these two lines:

```python
ENGINE = "yolo11n.engine"
PT     = "yolo11n.pt"
```

Change **both** names to the same size, save, and run the demo again.

| Size | `PT` name | `ENGINE` name | Parameters (about) | What to expect |
| --- | --- | --- | --- | --- |
| Nano (default) | `yolo11n.pt` | `yolo11n.engine` | 2.6 M | Fastest, least accurate |
| Small | `yolo11s.pt` | `yolo11s.engine` | 9.4 M | A bit slower, more accurate |
| Medium | `yolo11m.pt` | `yolo11m.engine` | 20 M | Slower again |
| Large | `yolo11l.pt` | `yolo11l.engine` | 25 M | Slow on the Jetson |
| Extra large | `yolo11x.pt` | `yolo11x.engine` | 57 M | Slowest, most accurate |

**Example:** to try the Small model, the lines become:

```python
ENGINE = "yolo11s.engine"
PT     = "yolo11s.pt"
```

```bash
python3 yolov11_demo.py
```

**You should see:** the first run of a new size takes a few minutes. The program downloads the `.pt` file and converts it into an `.engine` file (this is the "export"). Later runs start quickly because the `.engine` file now exists.

```text
[INFO] yolo11s.engine not found, exporting from yolo11s.pt …
Downloading https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11s.pt to 'yolo11s.pt'...
...
```

Then the same video window as Step 5 appears. Compare it with the Nano model: how smooth is the video, and how high does `GR3D_FREQ` go in `tegrastats`? Put the names back to `yolo11n` when you are done.

**What you learn:** Bigger models are usually more accurate but slower and use more GPU. The robot needs quick reactions, so a small model is often the better choice.

---

## Step 7: 🎥 Record Clip 1: YOLO on the Jetson (Part A)

**Do:** Film this with a phone or camera. The film must show the **computer screen** and the **robot** while one team member narrates. **At the very start, show the face of every team member and say everyone's name.** Then run `python3 yolov11_demo.py` again. Point the robot's camera at several objects (for example a person, a bottle, a laptop). Keep the `tegrastats` window visible next to the video window. Say out loud what you see.

**You should see (and show in the video):** boxes and labels on the objects, and `GR3D_FREQ` going up while the model runs.

**What you learn:** Showing `tegrastats` is your proof that the model ran on the GPU. Keep the clip short, about one minute.

---

## Step 8: Start the YOLO publisher

**Do:** **[Jetson]** In a terminal, start the publisher. It reads the camera, runs YOLO, and sends out the results. The first run downloads the model weights, so it needs the internet and takes a while. After that you can go back to `small_blue_wifi`.

```bash
cd ~/Robotics_Assignment_4
python3 yolo_publisher_sample_code.py
```

**You should see:** (long camera lines will scroll past, which is normal)

```text
[INFO] [1774133694.824883296] [yolo_json_publisher]: Loading YOLOv11 model on CUDA...
Downloading https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11n.pt to 'yolo11n.pt'...
100%|██████████████████████████████████████| 5.35M/5.35M [00:00<00:00, 9.65MB/s]
[INFO] [1774133708.662359424] [yolo_json_publisher]: Initializing CSI Camera...
GST_ARGUS: Creating output stream
CONSUMER: Producer has connected; continuing.
```

**What you learn:** A *publisher* is a program that keeps sending out information. This one sends out a short text message about every object YOLO sees, 20 times a second, on a "channel" called `/yolo/detections_json`. Other programs can tune in to that channel.

---

## Step 9: Start the YOLO subscriber

**Do:** **[Jetson]** Open a **new** terminal and start the subscriber. Point the camera at a few objects.

```bash
cd ~/Robotics_Assignment_4
python3 yolo_subscriber_sample_code.py
```

**You should see:** one block of lines for each camera picture, naming each object, how sure YOLO is, and where the box is.

```text
[INFO] [1774133827.058645760] [yolo_json_subscriber]: Listening for YOLO JSON detections...
[INFO] [1774133827.062601856] [yolo_json_subscriber]: Received 1 detections at t=1774133826.99 [camera_link]:
[INFO] [1774133827.064806720] [yolo_json_subscriber]:   [0] bottle (0.87) | Center: (689.2, 239.0), Size: 180.4x412.7
```

**What you learn:** A *subscriber* is a program that listens to a channel. Here is how to read the last line:
- `bottle (0.87)`: what YOLO sees, and how sure it is.
- `Center: (689.2, 239.0)`: where the middle of the box is, in pixels. The picture is 1280 wide, so the middle of the picture is `640`.
- `Size: 180.4x412.7`: the box is 180 pixels wide and 412 tall. **The bigger the box, the closer the object.** The robot will use exactly this to find the bottle and to know when it is close enough.

---

## Step 10: Change the publisher's settings

**Do:** **[Jetson]** Stop the publisher (`Ctrl+C`). Open `yolo_publisher_sample_code.py` and find the settings block near the top. Change **one** value, start the publisher again, and watch the subscriber and `tegrastats`.

```python
MODEL_PATH = 'yolo11n.pt'
PUBLISH_PERIOD = 0.05
```

| Setting | Try this | What to notice |
| --- | --- | --- |
| `MODEL_PATH` | `'yolo11n.engine'` (a faster, optimized version) | Starts faster and uses less GPU. First run this once: `cp ~/Robotics_Assignment_4/Assignment_4_demo/CUDA_Demo/yolo11n.engine ~/Robotics_Assignment_4/` |
| `MODEL_PATH` | `'yolo11s.pt'` | Slower, usually more accurate |
| `PUBLISH_PERIOD` | `0.2` (5 times a second instead of 20) | The subscriber prints less often |

**You should see:** the same kind of output as Step 9, only faster, slower or different, depending on your change. For `.engine` files you will also see lines starting with `[TRT]` and a note that it assumes `task=detect`. That is fine.

**What you learn:** The same program can be made faster or more accurate by changing one number. Faster models save power and keep the robot's reactions quick.

---

## Step 11: 🎥 Record Clip 2: publisher and subscriber (Part B)

**Do:** Start filming (phone or camera aimed at the screen and the robot). Run the publisher and the subscriber in two terminals side by side. Point the robot's camera at several objects (a person, a bottle, a laptop). Say out loud what each program does.

**You should see (and show in the video):** the subscriber printing the objects that the publisher's camera sees.

**What you learn:** You are showing that two separate programs can share information over ROS 2. The robot's driving program works the same way.

---

## Step 12: Read how the robot finds the bottle

**Read:** This is how `bottle_pick_place.py` works. You do not need to understand the code.

1. It listens to the YOLO channel (Step 9) and looks for a `bottle`.
2. If the bottle's box is left or right of the middle of the picture, it turns the wheels to bring it back to the middle. This is called **visual servoing**.
3. When the bottle is centered, it drives forward until the box is tall enough (the bottle is close).
4. Then it moves the arm to home pose, opens the gripper, reaches forward, closes the gripper, and pulls back to home.
5. To place the bottle, it drives back to where it started (using the wheel sensors) and sets the bottle down.

**What you learn:** A robot can do a real task using just two things: *where* the object is (the box center) and *how close* it is (the box height). You will tune a few numbers that control each of those.

---

## Step 13: Start the robot

**Do:** **[Jetson]** Close the old programs. Make sure the robot has free space around it. Then start the robot's drivers in a terminal.

```bash
ros2 launch turtlebot3_manipulation_bringup hardware.launch.py
```

**You should see:** a lot of lines, ending with no red `ERROR` lines. (This is the same step as in Assignment 3.)

```text
[INFO] [launch]: All log files can be found below /home/nvidia/.ros/log/...
[ros2_control_node-1] [INFO] ...: Successfully loaded controller arm_controller
[ros2_control_node-1] [INFO] ...: Successfully loaded controller gripper_controller
```

Then, in a **second Jetson terminal**, start the YOLO publisher again:

```bash
cd ~/Robotics_Assignment_4
python3 yolo_publisher_sample_code.py
```

**What you learn:** The robot's drivers let programs move the wheels and the arm. The publisher keeps sending what the camera sees. Both must be running for the next steps.

---

## Step 14: Copy your Assignment 3 values

**Do:** **[Remote PC]** Open your own Assignment 3 code (`~/turtlebot_docker/my_code/sample_code.py`, the one you submitted). Find these values. This command prints them for you (run it in a normal terminal on the laptop):

```bash
grep -nE "LIN_VEL_STEP_SIZE|ANG_VEL_STEP_SIZE|GRIPPER_KEY_BINDINGS|'g'|'h'|'9'|'0'" ~/turtlebot_docker/my_code/sample_code.py
```

```text
32:LIN_VEL_STEP_SIZE = 0.01
41:GRIPPER_KEY_BINDINGS = {
42:    'g': 0.01,  # Open
43:    'h': -0.01  # Close
47:    '9': [0.0, 0.0, 0.0, 0.0],  # Home pose
52:    '0': [0.0, 0.9, 0.0, 0.5],  # Extend arm forward
```

(Your numbers will be different. Use **yours**.)

Now open `~/turtlebot_docker/my_code/Robotics_Assignment_4/bottle_pick_place.py` and copy your values into the settings block:

| In `bottle_pick_place.py` | Copy from your Assignment 3 code |
| --- | --- |
| `HOME_POSE` | The `'9'` (Home) entry in `POSES` |
| `EXTEND_POSE` | The `'0'` (Extend Forward) entry in `POSES` |
| `GRIPPER_OPEN` | The `'g'` value in `GRIPPER_KEY_BINDINGS` |
| `GRIPPER_CLOSE` | The `'h'` value in `GRIPPER_KEY_BINDINGS` |

Optional: if your robot moved well in Assignment 3, `LIN_VEL_STEP_SIZE` is a good hint for a safe, slow `FORWARD_VEL`.

**You should see:** the settings block looks like this, with **your** numbers:

```python
HOME_POSE = [0.0, 0.0, 0.0, 0.0]
EXTEND_POSE = [0.0, 0.9, 0.0, 0.5]
GRIPPER_OPEN = 0.01
GRIPPER_CLOSE = -0.01
```

**What you learn:** You already found the arm poses and gripper values for this exact robot in Assignment 3. Reusing them means you don't have to find them again. The numbers in the file are only placeholders until you replace them.

---

## Step 15: Find the "close enough" box height

**Do:** **[Jetson]** Open a terminal and start the subscriber (Step 9). Hold the bottle at the distance where the robot's gripper could grab it. Read the second number of `Size`.

```bash
cd ~/Robotics_Assignment_4
python3 yolo_subscriber_sample_code.py
```

**You should see:**

```text
[INFO] [...] [yolo_json_subscriber]:   [0] bottle (0.89) | Center: (640.0, 360.0), Size: 210.5x430.2
```

Here the height is about `430`. In `bottle_pick_place.py`, set `STOP_BBOX_HEIGHT` a little below that number (for example `400`). Then close the subscriber with `Ctrl+C`.

```python
STOP_BBOX_HEIGHT = 400
```

**What you learn:** A taller box means a closer bottle. The robot stops when the box reaches this height. This is how it knows how far to drive.

---

## Step 16: Run Stage 1: only turn toward the bottle

**Do:** **[Remote PC]** Make sure the laptop and the Jetson are on the same `small_blue_wifi` network, as in Assignment 3. Open a Docker shell (`docker exec -it remote_pc_humble bash`). Make sure `STAGE = "servo"` is set in the file (it is the default). Run the script. Place the bottle slowly in front of the robot and move it left and right. Press `Ctrl+C` any time to stop the robot.

```bash
cd ~/my_code/Robotics_Assignment_4
python3 bottle_pick_place.py
```

**You should see:** the robot turns in place to face the bottle. It does not drive forward.

```text
[INFO] [1780000000.123456789] [bottle_pick_place]: STAGE = servo, looking for ['bottle']
[INFO] [1780000000.223456789] [bottle_pick_place]: Tracking the bottle. Press Ctrl+C to stop.
```

**What you learn:** The robot compares the bottle's center to the middle of the picture, and turns the wheels to shrink that gap. If it wobbles or lags, see the tuning table in Step 19.

---

## Step 17: 🎥 Record Clip 3: visual servoing (Part C a)

**Do:** Start filming. Make sure the robot, the bottle and the terminal screen are all in view. Run `bottle_pick_place.py` with `STAGE = "servo"`. Move the bottle slowly in front of the robot. Say out loud what you see.

**You should see (and show in the video):** the robot "locks onto" the bottle and keeps it in the center of the camera's view by turning left and right.

**What you learn:** This is visual servoing: using the camera to steer. Keep the clip short.

---

## Step 18: Run Stage 2: pick up the bottle

**Do:** **[Remote PC]** Open `bottle_pick_place.py` and change the stage. Put the bottle on the ground in front of the robot, slightly off-center, and run it again. Press `Ctrl+C` to stop the robot.

```python
STAGE = "pick"
```

```bash
python3 bottle_pick_place.py
```

**You should see:** the robot turns to face the bottle, drives up to it, reaches forward, closes the gripper, and lifts the bottle.

```text
[INFO] [1780000000.123456789] [bottle_pick_place]: STAGE = pick, looking for ['bottle']
[INFO] [1780000000.223456789] [bottle_pick_place]: Waiting for arm and gripper controllers and odometry...
[INFO] [1780000001.323456789] [bottle_pick_place]: Start point recorded at x=0.00 y=0.00
[INFO] [1780000001.423456789] [bottle_pick_place]: Arm to home pose, gripper open.
[INFO] [1780000009.423456789] [bottle_pick_place]: Tracking the bottle. Press Ctrl+C to stop.
[INFO] [1780000024.523456789] [bottle_pick_place]: Picking up the bottle.
[INFO] [1780000036.623456789] [bottle_pick_place]: Pick complete.
```

**What you learn:** The same program now also drives forward and uses the arm and gripper you set up in Assignment 3. If the robot does not do well, use the tuning table in Step 19.

---

## Step 19: Tune it (only if needed)

**Do:** If the robot does not behave well, change **one** value at a time in the settings block of `bottle_pick_place.py` and run it again.

| Symptom | Setting to change |
| --- | --- |
| Robot wobbles left and right around the bottle | Lower `TURN_GAIN`, or raise `CENTER_TOLERANCE_PX` |
| Robot reacts slowly or lags behind the bottle | Raise `TURN_GAIN` |
| Robot stops too far from or too close to the bottle | Change `STOP_BBOX_HEIGHT` (see Step 15) |
| Robot drives too fast to track | Lower `FORWARD_VEL` |
| Gripper misses or crushes the bottle | Adjust `EXTEND_POSE`, `GRIPPER_CLOSE` (start from your Assignment 3 values) |
| Bottle is named as another object | Add the extra names to `TARGET_CLASSES`, for example `["bottle", "vase"]` |
| Detections flicker on and off | Raise `MIN_CONFIDENCE` |
| Robot does not get back to its start point (Step 21) | Change `RETURN_VEL`, `HOME_TOLERANCE` |

**You should see:** the behaviour improves. Write down which numbers you changed and why. You will mention them in the next clip.

**What you learn:** Real robots need tuning. Changing one number at a time, and watching what changes, is how engineers find good values.

---

## Step 20: 🎥 Record Clip 4: pick up the bottle (Part C b)

**Do:** Start filming (robot, bottle and screen in view). Set `STAGE = "pick"`. Put the bottle on the ground in the camera's view, slightly off-center. Run the script. **Say out loud which settings you tuned and why.**

**You should see (and show in the video):** the robot faces the bottle, drives to it, reaches out, grabs it and lifts it off the ground.

**What you learn:** You can explain your choices, which is as important as the robot working.

---

## Step 21: Run Stage 3: pick up and place the bottle

**Do:** **[Remote PC]** Set the stage to `"full"` and run it. The robot will drive back to where it started and put the bottle down. Keep the way clear and be ready to press `Ctrl+C`.

```python
STAGE = "full"
```

```bash
python3 bottle_pick_place.py
```

**You should see:** everything in Step 18, then the robot drives back and places the bottle.

```text
[INFO] [1780000036.623456789] [bottle_pick_place]: Returning to the start point.
[INFO] [1780000052.723456789] [bottle_pick_place]: Placing the bottle.
[INFO] [1780000064.823456789] [bottle_pick_place]: Pick and place complete.
```

If the return takes too long, you will see this instead and the robot places the bottle where it is:

```text
[WARN] [...] [bottle_pick_place]: Return timed out, placing the bottle here.
```

**What you learn:** The robot remembers its start point from its wheel sensors (called odometry) and drives back to it. The wheel sensors drift a little, so it may not return exactly.

---

## Step 22: 🎥 Record Clip 5: pick and place (Part C c)

**Do:** Start filming (robot, bottle and screen in view). Set `STAGE = "full"`. Test it the same way as Clip 4. Show that the robot returns near its starting spot and puts the bottle on the ground.

**You should see (and show in the video):** pick, return, place, with the robot ending near where it started.

**What you learn:** You have now shown the full job: see, aim, approach, grab, carry, and place.

---

## Step 23: Submit

You must submit **5 video clips**. Tick every box before you submit.

- [ ] **Clip 1 (Part A): YOLO on the Jetson.** Shows every team member's face and name at the start. Shows boxes and labels on several objects, and `tegrastats` with `GR3D_FREQ` going up.
- [ ] **Clip 2 (Part B): Publisher and subscriber.** Shows both programs running, and the subscriber printing the objects the camera sees.
- [ ] **Clip 3 (Part C a): Visual servoing.** Shows `STAGE = "servo"`. The robot keeps the bottle in the center by turning left and right as you move the bottle slowly.
- [ ] **Clip 4 (Part C b): Pick up the bottle.** Shows `STAGE = "pick"`. The robot faces the bottle, drives to it, grabs it and lifts it. The narrator says which settings were tuned and why.
- [ ] **Clip 5 (Part C c): Pick and place.** Shows `STAGE = "full"`. The robot returns near its start spot and puts the bottle on the ground.

For every clip: film the screen **and** the robot with a phone or camera while one team member narrates. You do not need to edit, and a few minutes in total is enough.

**How to hand in**

1. Upload each clip to YouTube and set it to **Unlisted**. Do not upload the raw video files to Canvas.
2. **Every team member** pastes all 5 links into Canvas under **Assignment 4**, even if the team recorded the clips together.

Source code is **not** required for this assignment.
