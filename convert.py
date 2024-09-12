import os
from PIL import Image
from pillow_avif import AvifImagePlugin  # Registers AVIF support automatically
from pillow_heif import register_heif_opener

register_heif_opener()  # Ensure HEIC is supported too

def convert(url, target):
    try:
        print(f"Converting file: {url} to {target}")

        im = Image.open(url)
        print(f"Opened image: {url} in mode: {im.mode}")

        # Create a copy of the image without any metadata
        im_no_metadata = Image.new(im.mode, im.size)
        im_no_metadata.putdata(list(im.getdata()))

        # Convert RGBA to RGB if saving as JPEG
        if target.lower() == "jpg" or target.lower() == "jpeg":
            if im_no_metadata.mode == "RGBA":
                print(f"Converting RGBA to RGB for JPEG format")
                im_no_metadata = im_no_metadata.convert("RGB")

        # Create the output folder inside the current directory
        output_folder = f"converted_{target.lower()}"
        if not os.path.exists(output_folder):
            print(f"Creating output folder: {output_folder}")
            os.makedirs(output_folder)

        # Build the file path in the new folder with unique naming
        filename = os.path.basename(url)
        name, ext = os.path.splitext(filename)
        combined = os.path.join(output_folder, f"{name}.{target.lower()}")

        # Ensure unique filename if file already exists
        counter = 1
        while os.path.exists(combined):
            combined = os.path.join(output_folder, f"{name}_{counter}.{target.lower()}")
            counter += 1

        # Save the image in the newly created folder
        print(f"Saving image to: {combined}")
        im_no_metadata.save(combined)
        print(f"Image saved successfully!")

    except Exception as e:
        print(f"Error during conversion for {url}: {e}")

def acceptable(urls, supported_inputs):
    for url in urls:
        extension = os.path.splitext(url)[1][1:]
        if extension.lower() not in supported_inputs:
            print(f"File {url} is not acceptable, extension: {extension}")
            return False
    return True
