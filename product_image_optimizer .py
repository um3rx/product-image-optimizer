!pip install Pillow

from PIL import Image
from google.colab import files
import zipfile
import os
import shutil

print("Choose marketplace:")
print("1 = Daraz (800x800)")
print("2 = Amazon (1000x1000)")
print("3 = Shopify (1200x1200)")

marketplace = input("Enter choice: ").strip()

if marketplace == "1":
    size = 800
elif marketplace == "2":
    size = 1000
elif marketplace == "3":
    size = 1200
else:
    print("Invalid choice. Defaulting to Amazon (1000x1000)")
    size = 1000

print("\nCompression mode:")
print("1 = Maximum Quality")
print("2 = Balanced")
print("3 = Maximum Compression")

compression = input("Enter choice: ").strip()

if compression == "1":
    quality = 95
elif compression == "3":
    quality = 60
else:
    quality = 85

prefix = input("\nEnter filename prefix: ").strip()

if not prefix:
    prefix = "image"

square_canvas = input(
    "Make images square with white background? (y/n): "
).strip().lower()

if square_canvas not in ["y", "n"]:
    square_canvas = "n"

uploaded = files.upload()

# Clean old folder
if os.path.exists("processed"):
    shutil.rmtree("processed")

os.makedirs("processed")

processed_files = []

total_original = 0
total_new = 0

skipped_files = []

valid_extensions = (
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".bmp"
)

for count, filename in enumerate(uploaded.keys(), start=1):

    if not filename.lower().endswith(valid_extensions):
        skipped_files.append(filename)
        continue

    try:

        img = Image.open(filename)

        original_size = os.path.getsize(filename)

        has_alpha = (
            img.mode in ("RGBA", "LA")
            or "transparency" in img.info
        )

        if has_alpha:
            img = img.convert("RGBA")
        else:
            img = img.convert("RGB")

        # High-quality resize while keeping ratio
        img.thumbnail((size, size), Image.LANCZOS)

        if square_canvas == "y":

            canvas = Image.new(
                "RGB",
                (size, size),
                (255, 255, 255)
            )

            x = (size - img.width) // 2
            y = (size - img.height) // 2

            if has_alpha:
                canvas.paste(img, (x, y), img)
            else:
                canvas.paste(img, (x, y))

            img = canvas

        else:

            # Fix transparent PNG → JPG conversion
            if img.mode != "RGB":

                background = Image.new(
                    "RGB",
                    img.size,
                    (255, 255, 255)
                )

                if img.mode == "RGBA":
                    background.paste(
                        img,
                        mask=img.split()[3]
                    )
                else:
                    background.paste(img)

                img = background

        output_name = f"{prefix}-{count}.jpg"

        output_path = os.path.join(
            "processed",
            output_name
        )

        img.save(
            output_path,
            "JPEG",
            quality=quality,
            optimize=True
        )

        new_size = os.path.getsize(output_path)

        total_original += original_size
        total_new += new_size

        saved_kb = (
            original_size - new_size
        ) // 1024

        print(
            f"{output_name}: "
            f"{original_size // 1024}KB -> "
            f"{new_size // 1024}KB | "
            f"Saved: {saved_kb}KB"
        )

        processed_files.append(output_path)

    except Exception as e:

        print(
            f"Error processing {filename}: {e}"
        )

        skipped_files.append(filename)

saved = total_original - total_new

if total_original > 0:
    percent = (
        saved / total_original
    ) * 100
else:
    percent = 0

print("\n========== SUMMARY ==========")

print(
    f"Images processed: "
    f"{len(processed_files)}"
)

if skipped_files:
    print(
        f"Skipped files: "
        f"{', '.join(skipped_files)}"
    )

print(
    f"Original size: "
    f"{round(total_original / 1024 / 1024, 2)} MB"
)

print(
    f"New size: "
    f"{round(total_new / 1024 / 1024, 2)} MB"
)

print(
    f"Space saved: "
    f"{round(saved / 1024 / 1024, 2)} MB"
)

print(
    f"Reduction: "
    f"{round(percent, 1)}%"
)

zip_name = f"{prefix}_images.zip"

with zipfile.ZipFile(
    zip_name,
    "w",
    zipfile.ZIP_DEFLATED
) as zipf:

    for file_path in processed_files:

        zipf.write(
            file_path,
            arcname=os.path.basename(file_path)
        )

print(f"\nZIP created: {zip_name}")

files.download(zip_name)
