#coding: utf-8
# python3
import cv2
import base64
from PIL import Image
from io import BytesIO


def frame2base64(frame):
    Img = Image.fromarray(frame)  # convert each frame to an image
    output_buffer = BytesIO()  # Create a BytesIO
    Img.save(output_buffer, format='JPEG')  # write output_buffer
    byte_data = output_buffer.getvalue()  # Read in memory
    base64_data = base64.b64encode(byte_data)  # BASE64
    return base64_data  # transcode success return base64 encoding
