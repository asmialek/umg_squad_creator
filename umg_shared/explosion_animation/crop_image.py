from PIL import Image
import os


if __name__ == '__main__':
    for filename in os.listdir('./'):
        if filename[-3:] == 'png':
            image=Image.open(f'./{filename}')
            imageBox = image.getbbox()
            # cropped=image.crop(imageBox)
            # cropped.save(f'./cropped/{filename[:-4]}.png')
            resized=Image.new(image.mode, (60, 60), (0, 0, 0, 0))
            width, height = image.size
            resized.paste(image, (int((60-width)/2), 60-height))
            resized.save(f'./resized/{filename[:-4]}.png')