from pathlib import Path

import torch
from PIL import Image, ImageDraw, ImageFont
from transformers import YolosForObjectDetection, YolosImageProcessor

root_dir = Path(__file__).parent.parent
picture_path = root_dir / "assets" / "coffee-shop.jpg"
image = Image.open(picture_path)

image_processor = YolosImageProcessor()
model = YolosForObjectDetection.from_pretrained("hustvl/yolos-tiny")

inputs = image_processor(image, return_tensors="pt")
outputs = model(**inputs)

target_sizes = torch.tensor([image.size[::-1]])
results = image_processor.post_process_object_detection(
    outputs, target_sizes=target_sizes
)[0]

draw = ImageDraw.Draw(image)
for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
    if score > 0.7:
        box_values = box.tolist()
        label = model.config.id2label[label.item()]
        draw.rectangle(box_values, outline="red", width=5)
        draw.text(box_values[0:2], label, fill="red")
image.show()