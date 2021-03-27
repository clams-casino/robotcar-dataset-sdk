import argparse
import os
import re
import matplotlib.pyplot as plt
import cv2
from image import load_image
from camera_model import CameraModel


def rectifiy_images(img_dir, models_dir, grayscale=True):
    """rectifies all images and saves to a new directory 

        Args:
            images_dir (str): directory containing images for which to read camera model.
            models_dir (str): directory containing camera model files.
        
    """
    camera = re.search('(stereo|mono_(left|right|rear))', img_dir).group(0)

    model = CameraModel(models_dir, img_dir)

    rectified_dir = img_dir +'_rectified'
    if not os.path.isdir(rectified_dir):
        print('Creating new directory for rectified images: {}'.format(rectified_dir))
        os.mkdir(rectified_dir)

    timestamps_path = os.path.join(os.path.join(img_dir, os.pardir, camera + '.timestamps'))
    if not os.path.isfile(timestamps_path):
        timestamps_path = os.path.join(img_dir, os.pardir, os.pardir, camera + '.timestamps')
        if not os.path.isfile(timestamps_path):
            raise IOError("Could not find timestamps file")

    timestamps_file = open(timestamps_path)
    for line in timestamps_file:
        tokens = line.split()
        filename = tokens[0] + '.png'

        img = load_image(os.path.join(img_dir, filename), model)
        if grayscale:
            plt.imsave(os.path.join(rectified_dir, filename), cv2.cvtColor(img, cv2.COLOR_RGB2GRAY), cmap='gray')
        else:
            plt.imsave(os.path.join(rectified_dir, filename), img)
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='rectifiy images from a given directory, save in a new directory')

    parser.add_argument('dir', type=str, help='Directory containing images.')
    parser.add_argument('models_dir', type=str, default=None, help='Directory containing camera model.')

    args = parser.parse_args()

    rectifiy_images(args.dir, args.models_dir, grayscale=True)