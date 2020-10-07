from PIL import Image
import os


if __name__ == '__main__':
    for filename in os.listdir('./umg_shared/mech_images/'):
        if filename[-3:] == 'png':
            image=Image.open(f'./umg_shared/mech_images/{filename}')
            imageBox = image.getbbox()
            cropped=image.crop(imageBox)
            cropped.save(f'./umg_shared/mech_images/cropped/{filename[:-4]}.png')
            resized=Image.new(cropped.mode, (60, 60), (0, 0, 0, 0))
            width, height = cropped.size
            resized.paste(cropped, (int((60-width)/2), 60-height))
            resized.save(f'./umg_shared/mech_images/resized/{filename[:-4]}.png')