import cv2
import time
from ultralytics import YOLO

# ---------------- SETTINGS ----------------
FIXED_TIME = 40
FRAME_SKIP = 8
IMG_SIZE = 416
# ------------------------------------------

model = YOLO("yolov8n.pt")

class TrafficController:
    def __init__(self, road1_video, road2_video):
        self.cap1 = cv2.VideoCapture(road1_video)
        self.cap2 = cv2.VideoCapture(road2_video)

        self.current_road = 1
        self.time_left = FIXED_TIME
        self.frame_counter = 0

    def detect_vehicles(self, frame):
        results = model(frame, imgsz=IMG_SIZE, verbose=False)

        vehicle_count = 0

        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                label = model.names[cls_id]

                if label in ["car", "bus", "truck", "motorcycle"]:
                    vehicle_count += 1
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, label, (x1, y1 - 5),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.5, (0, 255, 0), 2)

        return vehicle_count, frame

    def get_density(self):
        cap = self.cap1 if self.current_road == 1 else self.cap2

        ret, frame = cap.read()
        if not ret:
            return None, None

        self.frame_counter += 1

        # Skip frames for speed
        if self.frame_counter % FRAME_SKIP != 0:
            return None, None

        frame = cv2.resize(frame, (IMG_SIZE, IMG_SIZE))
        count, frame = self.detect_vehicles(frame)

        return count, frame

    def switch_road(self):
        self.current_road = 2 if self.current_road == 1 else 1
        self.time_left = FIXED_TIME
        print(f"\nSwitched to Road {self.current_road}")

    def run(self):
        while True:
            density, frame = self.get_density()

            if density is None:
                continue

            print(f"Road {self.current_road} | Vehicles: {density} | Time Left: {self.time_left}")

            cv2.imshow(f"Road {self.current_road}", frame)

            if density == 0:
                print("Empty road → Switching")
                self.switch_road()
                continue

            time.sleep(1)
            self.time_left -= 1

            if self.time_left <= 0:
                self.switch_road()

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap1.release()
        self.cap2.release()
        cv2.destroyAllWindows()


controller = TrafficController("road2.mp4", "road1.mp4")
controller.run()