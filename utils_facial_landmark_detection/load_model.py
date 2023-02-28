from config.config import *
import torch
from utils_facial_landmark_detection.models.basenet import MobileNet_GDConv
from utils_facial_landmark_detection.models.pfld_compressed import PFLDInference
from utils_facial_landmark_detection.models.mobilefacenet import MobileFaceNet

def load_model():
    out_size = 112
    # if torch.cuda.is_available():
    #     map_location=lambda storage, loc: storage.cuda()
    # else:
    #     map_location='cpu'
    if LandmarkBackbone=='MobileNet':
        out_size = 224
        model = MobileNet_GDConv(136)
        model = torch.nn.DataParallel(model)
        # download model from https://drive.google.com/file/d/1Le5UdpMkKOTRr1sTp4lwkw8263sbgdSe/view?usp=sharing
        checkpoint = torch.load(CR_WEIGHTS)
        print('Use MobileNet as backbone')
    elif LandmarkBackbone=='PFLD':
        model = PFLDInference() 
        # download from https://drive.google.com/file/d/1gjgtm6qaBQJ_EY7lQfQj3EuMJCVg9lVu/view?usp=sharing
        checkpoint = torch.load(CR_WEIGHTS)
        print('Use PFLD as backbone') 
        # download from https://drive.google.com/file/d/1T8J73UTcB25BEJ_ObAJczCkyGKW5VaeY/view?usp=sharing
    elif LandmarkBackbone=='MobileFaceNet':
        model = MobileFaceNet([112, 112],136)   
        checkpoint = torch.load(CR_WEIGHTS)      
        print('Use MobileFaceNet as backbone')         
    else:
        print('Error: not suppored backbone')    
    model.load_state_dict(checkpoint['state_dict'])
    model.eval()
    if torch.cuda.is_available() and DEVICE_IDX != -1:
        model.to(device='cuda:{}'.format(str(DEVICE_IDX)))
    return model, out_size