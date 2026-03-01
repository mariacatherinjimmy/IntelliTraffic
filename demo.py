import time

FIXED_TIME = 40

class TrafficController:
    def __init__(self):
        self.current_road = 1
        self.time_left = FIXED_TIME
        self.density = {1: 5, 2: 3}  # example values
        self.saved_time = 0
        self.skips = 0

    def switch_road(self):
        self.current_road = 2 if self.current_road == 1 else 1
        self.time_left = FIXED_TIME
        print(f"\n🔄 Switched to Road {self.current_road}")

    def update_density(self):
        # Simulated density (replace with OpenCV logic)
        import random
        self.density[self.current_road] = random.randint(0, 5)

    def run(self):
        while True:
            self.update_density()
            current_density = self.density[self.current_road]

            print(f"Road {self.current_road} | Density: {current_density} | Time Left: {self.time_left}")

            if current_density == 0 and self.time_left > 0:
                print("⚡ Empty road detected → Skipping")
                self.saved_time += self.time_left
                self.skips += 1
                self.switch_road()
                continue

            time.sleep(1)
            self.time_left -= 1

            if self.time_left <= 0:
                self.switch_road()

controller = TrafficController()
controller.run()