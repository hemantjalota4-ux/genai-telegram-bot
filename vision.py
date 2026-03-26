from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image

# Load model once (important for performance)
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")


# -------------------------------
# Generate caption + tags
# -------------------------------
def caption_image(image_path):
    try:
        image = Image.open(image_path).convert("RGB")

        inputs = processor(images=image, return_tensors="pt")

        output = model.generate(**inputs, max_new_tokens=50)

        caption = processor.decode(output[0], skip_special_tokens=True)

        # -------------------------------
        # Extract 3 meaningful tags
        # -------------------------------
        words = caption.lower().split()

        # remove common words
        stopwords = {"a", "the", "is", "on", "in", "with", "and", "of"}
        tags = [w.strip(".,") for w in words if w not in stopwords]

        # unique + top 3
        tags = list(dict.fromkeys(tags))[:3]

        return caption, tags

    except Exception as e:
        return f"Error: {str(e)}", []