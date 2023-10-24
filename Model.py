import torch.nn as nn

class myNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.cnnPart = nn.Sequential(
            nn.Conv2d(in_channels=3,out_channels=16,kernel_size=3,stride=2,dilation=1), #31*31
            nn.MaxPool2d(kernel_size=3,stride=2), #15*15
            nn.ReLU(),

            nn.Conv2d(in_channels=16,out_channels=32,kernel_size=15),
        )
        self.fcPart = nn.Sequential(
            nn.Linear(32,1), #由于是二分类任务，所以输出维度为1
            nn.Sigmoid()  #输出值在0-1之间
        )
    def forward(self,x):
        batchsize = x.shape[0]
        out = self.cnnPart(x)
        out = out.view(batchsize,-1)
        out = self.fcPart(out)
        return out