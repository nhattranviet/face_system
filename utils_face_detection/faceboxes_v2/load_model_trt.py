
import torch
from torchvision.transforms import Normalize
import tensorrt as trt
import pycuda.driver as cuda
import pycuda.autoinit
import numpy as np
import cv2

img = cv2.resize(cv2.imread("./weights/1.png"), (720, 1280))
input_batch = np.array(np.repeat(np.expand_dims(np.array(img, dtype=np.float32), axis=0), 64, axis=0), dtype=np.float32)
print(input_batch.shape)

f = open("./weights/FaceBoxes_engine.trt", "rb")
runtime = trt.Runtime(trt.Logger(trt.Logger.WARNING)) 

engine = runtime.deserialize_cuda_engine(f.read())
context = engine.create_execution_context()

# need to set input and output precisions to FP16 to fully enable it
output = np.empty([64, 1000], dtype = np.float32) 

# allocate device memory
d_input = cuda.mem_alloc(1 * input_batch.nbytes)
d_output = cuda.mem_alloc(1 * output.nbytes)

bindings = [int(d_input), int(d_output)]

stream = cuda.Stream()

def predict(batch): # result gets copied into output
    # transfer input data to device
    cuda.memcpy_htod_async(d_input, batch, stream)
    # execute model
    context.execute_async_v2(bindings, stream.handle, None)
    # transfer predictions back
    cuda.memcpy_dtoh_async(output, d_output, stream)
    # syncronize threads
    stream.synchronize()
    
    return output

def preprocess_image(image):
    img = cv2.resize(image, dsize=(0, 0), fx=1, fy=1, interpolation=cv2.INTER_LINEAR)
    img = np.float32(img)
    img -= (104, 117, 123)
    img = img.transpose(2, 0, 1)
    img = torch.from_numpy(img).unsqueeze(0)
    img = img.to("cuda")
    return img

preprocessed_images = np.array([preprocess_image(image) for image in input_batch])

print("Warming up...")

pred = predict(preprocessed_images)

print("Done warming up!")

indices = (-pred[0]).argsort()[:5]
print("Class | Probability (out of 1)")
print(list(zip(indices, pred[0][indices])))
