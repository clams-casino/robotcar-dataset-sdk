import os
import numpy as np
import argparse

from transform import build_se3_transform
from camera_model import CameraModel

parser = argparse.ArgumentParser(description='Project LIDAR data into camera image')
parser.add_argument('--image_dir', type=str, help='Directory containing images')
parser.add_argument('--models_dir', type=str, help='Directory containing camera models')
parser.add_argument('--extrinsics_dir', type=str, help='Directory containing sensor extrinsics')

args = parser.parse_args()

model = CameraModel(args.models_dir, args.image_dir)

extrinsics_path = os.path.join(args.extrinsics_dir, model.camera + '.txt')
with open(extrinsics_path) as extrinsics_file:
    extrinsics = [float(x) for x in next(extrinsics_file).split(' ')]

print('***** Intrinsics *****')

print('Focal length')
print(model.focal_length)

print('Principal Point')
print(model.principal_point)

G_camera_image = model.G_camera_image
print('From image frame to camera frame')
print(G_camera_image)


print('***** Extrinsics *****')

G_camera_vehicle = build_se3_transform(extrinsics)

print('From vehicle frame to camera frame')
print(G_camera_vehicle)

G_vehicle_camera = np.linalg.inv(G_camera_vehicle)

print('Frome camera frame to vehicle frame')
print(G_vehicle_camera)

G_vehicle_image = np.matmul(G_vehicle_camera, G_camera_image)

print('T_B_C')
print(G_vehicle_image)