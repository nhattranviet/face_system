import cv2
from utils_face_feature_extraction.arcface.model import Backbone, Arcface, MobileFaceNet, Am_softmax, l2_norm
import torch
from PIL import Image
from torch2trt import TRTModule
from config.config import DEVICE_IDX

class face_learner(object):
    def __init__(self, conf):
        self.conf = conf
        if self.conf.use_mobilfacenet:
            self.model = MobileFaceNet(self.conf.embedding_size).to(self.conf.device)
            print('MobileFaceNet model generated')
        else:
            self.model = TRTModule()
            # self.model = Backbone(self.conf.net_depth, self.conf.drop_ratio, self.conf.net_mode).to(self.conf.device)
            # print('{}_{} model generated'.format(self.conf.net_mode, self.conf.net_depth))
        self.threshold = self.conf.threshold
        
    def load_state(self):
        save_path = self.conf.model_path_trt            
        self.model.load_state_dict(torch.load(save_path))
        self.model.eval()
        if torch.cuda.is_available() and DEVICE_IDX != -1:
            self.model.to('cuda:{0}'.format(str(DEVICE_IDX)))
        
    def extract_feature(self, faces):
        '''
        faces : list of PIL Image
        target_embs : [n, 512] computed embeddings of faces in facebank
        names : recorded names of faces in facebank
        tta : test time augmentation (hfilp, that's all)
        '''
        embs = []
        for img in faces:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            embs.append(l2_norm(self.model(self.conf.test_transform(img).to(self.conf.device).unsqueeze(0))))
        source_embs = torch.cat(embs)
        return source_embs