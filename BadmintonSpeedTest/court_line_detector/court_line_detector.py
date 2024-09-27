import torch
import torchvision.transforms as transforms
import cv2
from torchvision import models
import numpy as np

class CourtLineDetector:
    def __init__(self, model_path):
        self.model = models.resnet50(pretrained=True)
        self.model.fc = torch.nn.Linear(self.model.fc.in_features, 14*2) 
        self.model.load_state_dict(torch.load(model_path, map_location='cpu'))
        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def predict(self, image):

    
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)#將輸入的圖像從 BGR 格式轉換為 RGB 格式，這是因為在 PyTorch 中，預訓練的模型通常期望圖像是 RGB 格式。
        image_tensor = self.transform(image_rgb).unsqueeze(0)#self.transform 是一個轉換函數，用於將圖像轉換為模型期望的格式，並且在轉換之後，使用 unsqueeze(0) 將張量的維度擴展，以匹配模型的輸入形狀。
        with torch.no_grad():#這個上下文管理器用於停用梯度計算，這是因為我們只是在推斷（預測）過程中使用模型，不需要計算梯度。
            outputs = self.model(image_tensor)#將圖像張量輸入模型，獲取模型的輸出。這裡的 self.model 是模型的實例。
        keypoints = outputs.squeeze().cpu().numpy()#將模型的輸出轉換為 NumPy 數組，並且將其轉移到 CPU 上。在這裡，.squeeze() 用於去除大小為 1 的維度，.cpu() 用於將數據移回 CPU。
        original_h, original_w = image.shape[:2]
        keypoints[::2] *= original_w / 224.0
        keypoints[1::2] *= original_h / 224.0

        return keypoints

    def draw_keypoints(self, image, keypoints):
        # Plot keypoints on the image
        for i in range(0, len(keypoints), 2):
            x = int(keypoints[i])
            y = int(keypoints[i+1])
            cv2.putText(image, str(i//2), (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,97,255), 2)
            cv2.circle(image, (x, y), 5, (0,97,255), -1)
            if((i+2) % 4 == 0):
                cv2.line(image, (int(keypoints[i-2]), int(keypoints[i-1])), (x,y), (255, 0, 0), 2)
            if(i==4 or i==6):
                cv2.line(image, (int(keypoints[i-4]), int(keypoints[i-3])), (x,y), (255, 0, 0), 2)
            
        return image
    
    def draw_keypoints_on_video(self, video_frames, keypoints):
        output_video_frames = []
        for i,frame in enumerate(video_frames):
            frame = self.draw_keypoints(frame, keypoints[i])
            output_video_frames.append(frame)
        return output_video_frames