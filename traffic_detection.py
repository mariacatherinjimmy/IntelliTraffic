import cv2
import time
from ultralytics import YOLO

# -----------------------------
# Load YOLO Model
# -----------------------------
model = YOLO("yolov8n.pt")

# -----------------------------
# Load Videos (Two Roads)
# -----------------------------
roadA = cv2.VideoCapture("roadA.mp4")
roadB = cv2.VideoCapture("roadB.mp4")

# -----------------------------
# Signal Parameters
# -----------------------------
MIN_GREEN_TIME = 10
YELLOW_TIME = 3

current_green = "A"
green_start_time = time.time()

# -----------------------------
# Detection Classes (COCO)
# -----------------------------
VEHICLE_CLASSES = [2, 3, 5, 7]  # car, motorcycle, bus, truck
PEDESTRIAN_CLASS = 0
# Ambulance & firetruck detected as truck/car but we'll check label name

# -----------------------------
# Detection Function
# -----------------------------
def analyze_frame(frame):
    results = model(frame, verbose=False)

    vehicle_count = 0
    pedestrian_count = 0
    emergency_detected = False

    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            label = model.names[cls]

            if cls in VEHICLE_CLASSES:
                vehicle_count += 1

                # Emergency detection by label (basic demo logic)
                if "ambulance" in label.lower() or "fire" in label.lower():
                    emergency_detected = True

            elif cls == PEDESTRIAN_CLASS:
                pedestrian_count += 1

    return vehicle_count, pedestrian_count, emergency_detected


# -----------------------------
# Main Loop
# -----------------------------
while True:

    retA, frameA = roadA.read()
    retB, frameB = roadB.read()

    if not retA or not retB:
        break

    frameA = cv2.resize(frameA, (640, 480))
    frameB = cv2.resize(frameB, (640, 480))

    vehA, pedA, emerA = analyze_frame(frameA)
    vehB, pedB, emerB = analyze_frame(frameB)

    elapsed_time = time.time() - green_start_time

    # -----------------------------
    # PRIORITY LOGIC
    # -----------------------------

    # Emergency override
    if emerA:
        current_green = "A"
        green_start_time = time.time()

    elif emerB:
        current_green = "B"
        green_start_time = time.time()

    else:
        if current_green == "A":
            if vehA == 0 and elapsed_time > MIN_GREEN_TIME:
                current_green = "B"
                green_start_time = time.time()

        elif current_green == "B":
            if vehB == 0 and elapsed_time > MIN_GREEN_TIME:
                current_green = "A"
                green_start_time = time.time()

    # -----------------------------
    # Display Signal Status
    # -----------------------------
    def draw_signal(frame, road_name, is_green):
        color = (0,255,0) if is_green else (0,0,255)
        cv2.circle(frame, (50,50), 20, color, -1)
        cv2.putText(frame, f"Road {road_name}", (20,100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)

    draw_signal(frameA, "A", current_green == "A")
    draw_signal(frameB, "B", current_green == "B")

    # Display Counts
    cv2.putText(frameA, f"Vehicles: {vehA}", (20,150),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
    cv2.putText(frameB, f"Vehicles: {vehB}", (20,150),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

    cv2.putText(frameA, f"Pedestrians: {pedA}", (20,180),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
    cv2.putText(frameB, f"Pedestrians: {pedB}", (20,180),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

    # Combine display
    combined = cv2.hconcat([frameA, frameB])

    cv2.imshow("IntelliTraffic Prototype", combined)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

roadA.release()
roadB.release()
cv2.destroyAllWindows()