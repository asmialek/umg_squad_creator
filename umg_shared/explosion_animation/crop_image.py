from PIL import Image
import os


if __name__ == '__main__':
    for filename in os.listdir('./'):
        if filename[-3:] == 'png':
            image = Image.open(f'./{filename}')
            resized = Image.new(image.mode, (60, 60), (0, 0, 0, 0))
            # width, height = cropped.size
            im1 = image.resize((60, 60)) 
            resized.paste(im1, (0, 0))
            resized.save(f'./resized/{filename[:-4]}.png')