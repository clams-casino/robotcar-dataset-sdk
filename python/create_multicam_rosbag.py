import argparse
import os
import re
import matplotlib.pyplot as plt
import cv2
from image import load_image
from camera_model import CameraModel

import rosbag
import rospy
from cv_bridge import CvBridge
bridge = CvBridge()

def write_rosbag(bag, topic_name, img_dir, models_dir, grayscale=True, rectify=False, compressed=False):
    """rectifies all images in img_dir and writes them to the bag with timestamps

        Args:
            bag (rosbag) : rosbag to write to
            topic_name (str) : name of ROS topic to write images to
            images_dir (str): directory containing images for which to read camera model.
            models_dir (str): directory containing camera model files.
            grayscale (bool): save the demosaiced images in grayscale if True
            rectify (bool): rectify the images using a camera model if True
        
    """
    camera = re.search('(stereo|mono_(left|right|rear))', img_dir).group(0)

    model = CameraModel(models_dir, img_dir) if rectify else None

    timestamps_path = os.path.join(os.path.join(img_dir, os.pardir, camera + '.timestamps'))
    if not os.path.isfile(timestamps_path):
        timestamps_path = os.path.join(img_dir, os.pardir, os.pardir, camera + '.timestamps')
        if not os.path.isfile(timestamps_path):
            raise IOError("Could not find timestamps file")

    timestamps_file = open(timestamps_path)
    for line in timestamps_file:
        tokens = line.split()
        timestamp = float(tokens[0]) / 1e6
        filename = tokens[0] + '.png'

        img = load_image(os.path.join(img_dir, filename), model)
        if grayscale:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

        if compressed:
            img_msg = bridge.cv2_to_compressed_imgmsg(img, dst_format='jpeg')
        else:
            img_msg = bridge.cv2_to_imgmsg(img, encoding='passthrough')

        msg_timestamp = rospy.Time.from_sec(timestamp)
        img_msg.header.stamp = msg_timestamp
        bag.write(topic_name, img_msg, msg_timestamp)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='rectifiy monocular multi camera images and write them to a rosbag')

    parser.add_argument('dir', type=str, help='Directory of the dataset.')
    parser.add_argument('models_dir', type=str, default=None, help='Directory containing camera model.')
    parser.add_argument('--compressed', action='store_true', help='write compressed images')

    args = parser.parse_args()

    bag = rosbag.Bag('test.bag', 'w')

    cameras = ['mono_left', 'mono_rear', 'mono_right'] 
    # cameras = ['mono_left', 'mono_right'] 

    for camera in cameras:
        img_dir = os.path.join(args.dir, camera)
        topic = '/' + camera + ('/compressed' if args.compressed else '/image_raw')
        write_rosbag(bag, topic, img_dir, args.models_dir, grayscale=True, rectify=True, compressed=args.compressed)

    bag.close()


    # # test
    # bag = rosbag.Bag('test.bag', 'r')

    # for camera in cameras:
    #     for topic, msg, t in bag.read_messages(topics=[camera]):
    #         img = bridge.compressed_imgmsg_to_cv2(msg, desired_encoding='passthrough')
    #         print(msg.header.stamp)
    #         cv2.imshow('', img)
    #         cv2.waitKey(10)