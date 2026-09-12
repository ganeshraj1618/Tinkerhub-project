from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image
import torch
import os

MODEL_NAME = "DunnBC22/vit-base-patch16-224-in21k_vegetables_clf"

print("Loading vegetable specialist model...")
processor = AutoImageProcessor.from_pretrained(MODEL_NAME)
model = AutoModelForImageClassification.from_pretrained(MODEL_NAME).eval()
print("Model ready.\n")

LABEL_MAP = {
    "broccoli": "broccoli",
    "bell pepper": "pepper",
    "pepper": "pepper",
    "mushroom": "mushroom",
    "corn": "corn",
    "cucumber": "cucumber",
    "cabbage": "cabbage",
    "cauliflower": "cauliflower",
    "lemon": "lemon",
    "tomato": "tomato",
    "carrot": "carrot",
    "potato": "potato",
    "onion": "onion",
    "eggplant": "eggplant",
    "zucchini": "zucchini",
    "spinach": "spinach",
    "lettuce": "lettuce",
    "radish": "radish",
    "beet": "beet",
    "pea": "pea",
    "bean": "bean",
}


def classify(image_input):
    if isinstance(image_input, str):
        img = Image.open(image_input).convert("RGB")
    else:
        img = image_input.convert("RGB")

    inputs = processor(img, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)

    probs = outputs.logits.softmax(1)[0]
    top_idx = probs.argmax().item()
    confidence = probs[top_idx].item()

    raw_label = model.config.id2label[top_idx].lower()
    veggie = LABEL_MAP.get(raw_label, raw_label)

    return veggie, confidence, raw_label


if __name__ == "__main__":
    test_folder = "test_images"

    if not os.path.isdir(test_folder):
        print(f"Folder '{test_folder}' not found.")
        exit()

    images = [f for f in os.listdir(test_folder)
              if f.lower().endswith((".jpg", ".jpeg", ".png"))]

    if not images:
        print(f"No images inside '{test_folder}'.")
        exit()

    print(f"Found {len(images)} image(s). Testing...\n")
    print("-" * 70)
    print(f"{'File':<20} {'Our Veggie':<15} {'Conf':<8} {'Raw Model Label'}")
    print("-" * 70)

    for filename in sorted(images):
        path = os.path.join(test_folder, filename)
        try:
            veggie, conf, raw = classify(path)
            print(f"{filename:<20} {veggie:<15} {conf:<8.2f} {raw}")
        except Exception as e:
            print(f"{filename:<20} ERROR: {e}")

    print("-" * 70)
    print("\nDone.")