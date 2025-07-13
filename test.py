import cv2
import math
import json
from ultralytics import YOLO

def estimate_explosive_type(radius):
    if radius < 8:
        return "Hand Grenade (100–200g TNT)"
    elif radius < 18:
        return "Small IED (0.5–1kg TNT)"
    elif radius < 35:
        return "Medium IED or Backpack Bomb (2–5kg TNT)"
    elif radius < 80:
        return "VBIED or Car Bomb (10–50kg TNT)"
    else:
        return "Air-dropped Bomb or Heavy Explosive (100kg+ TNT)"

def estimate_scale(person_boxes):
    if not person_boxes:
        return 0.02
    heights = [abs(y2-y1) for x1, y1, x2, y2 in person_boxes]
    avg_height_pixels = sum(heights)/len(heights)
    scale = 1.7/ avg_height_pixels # meters per pixels
    return scale

# n is nono smallest & fastest
model = YOLO("yolov8n.pt")

results = model("data/blast_images/blast1.jpg")

# finding centers of all detected boxes
centers = []
for box in results[0].boxes.xyxy:
    x1,y1,x2,y2 = box[:4]
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2
    centers.append((cx.item(),cy.item()))

# avg all centers
blast_center_x = sum(x for x, y in centers) / len(centers)
blast_center_y = sum(y for x, y in centers) / len(centers)
blast_center = (blast_center_x, blast_center_y)

# saving output in jpg file with dot in center of damage
image = cv2.imread("data/blast_images/blast1.jpg")
cv2.circle(image, (int(blast_center_x), int(blast_center_y)), 10, (0,0,255), -1)
cv2.imwrite("outputs/detection_with_center.jpg", image)

# finding distance from the center of damage using euclidean formula
distances = []
for cx,cy in centers:
    dx = cx - blast_center[0]
    dy = cy - blast_center[1]
    distance = math.sqrt(dx**2 + dy**2)
    distances.append(distance)


# finding blast radius in pixels
blast_radius = max(distances)

# draw a blast circle
image = cv2.imread("outputs/detection_with_center.jpg")
center_point = (int(blast_center[0]), int(blast_center[1]))
cv2.circle(image, center_point, int(blast_radius), (0,0,255), 2)
cv2.imwrite("outputs/blast_circle.jpg",image)

# saving output in json
object_data = []
for (cx,cy), cls in zip(centers, results[0].boxes.cls):
    label = results[0].names[int(cls)]
    object_data.append({
        "label": label,
        "x": float(cx),
        "y": float(cy)
    })

# actual blast radius in meters
person_boxes = []
for box, cls in zip(results[0].boxes.xyxy, results[0].boxes.cls):
    if int(cls) == 0:
        x1, y1, x2, y2 = box.tolist()
        person_boxes.append((x1,y1,x2,y2))
scale = estimate_scale(person_boxes)
blast_radius *= scale

#converting distances from pixels to meters
human_damage = []

for box, cls in zip(results[0].boxes.xyxy, results[0].boxes.cls):
    class_name = model.names[int(cls)]

    if class_name != "person": continue

    x1, y1, x2, y2 = box
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2

    # Use blast center from before
    dx = cx - blast_center[0]
    dy = cy - blast_center[1]
    dist_px = math.sqrt(dx**2 + dy**2)
    dist_m = dist_px * scale

    # Classify based on distance
    if dist_m < 8:
        status = "Fatal"
    elif dist_m < 20:
        status = "Critical Injury"
    elif dist_m < 35:
        status = "Minor Injury"
    else:
        status = "Safe"

    human_damage.append({
        "center": (float(cx), float(cy)),
        "distance_m": round(dist_m, 2),
        "status": status
    })

blast_data = {
    "blast_center": [blast_center_x, blast_center_y],
    "blast_radius": blast_radius,
    "estimate_explosive_type": estimate_explosive_type(blast_radius),
    "human_damage_report": human_damage,
    "objects_detected": object_data,
}

with open("outputs/blast_analysis.json", "w") as f:
    json.dump(blast_data, f, indent=2)

results[0].show()