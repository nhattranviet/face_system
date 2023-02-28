import torch
from collections import OrderedDict
from nets import FaceBoxesNet

img_dim = (720, 1280)
rgb_mean = (104, 117, 123) # bgr order
num_classes = 2
model_path = "weights/FaceBoxes.pth"
onnx_path = "weights/FaceBoxes_onnx.onnx"

# Create the model and load the weights
model = FaceBoxesNet()

state_dict = torch.load(model_path)
# create new OrderedDict that does not contain `module.`
new_state_dict = OrderedDict()
for k, v in state_dict.items():
    head = k[:7]
    if head == 'module.':
        name = k[7:]  # remove `module.`
    else:
        name = k
    new_state_dict[name] = v
model.load_state_dict(new_state_dict)

# Create dummy input
dummy_input = torch.rand(64, 3, img_dim[0], img_dim[1])

# Define input / output names
input_names = ["actual_input_1"]
output_names = ["output1", '345']

# Convert the PyTorch model to ONNX
torch.onnx.export(model,
                  dummy_input,
                  onnx_path,
                  verbose=True,
                  input_names=input_names,
                  output_names=output_names)