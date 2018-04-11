# Import the modules
from PIL import Image, ImageFilter

try:
    # Load an image from the hard drive
    original = Image.open("220px-Lenna.png")

    # Blur the image
    blurred = original.filter(ImageFilter.BLUR)

    # Display both images
    original.show()
    blurred.show()

    # save the new image
    blurred.save("blurred.png")

except:
    print("Unable to load image")
