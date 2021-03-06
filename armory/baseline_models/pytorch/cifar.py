"""
CNN model for 32x32x3 image classification
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from art.classifiers import PyTorchClassifier


DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(3, 4, 5, 1)
        self.conv2 = nn.Conv2d(4, 10, 5, 1)
        self.fc1 = nn.Linear(250, 100)
        self.fc2 = nn.Linear(100, 10)

    def forward(self, x):
        x = x.permute(0, 3, 1, 2)  # from NHWC to NCHW
        x = self.conv1(x)
        x = F.relu(x)
        x = F.max_pool2d(x, 2)
        x = self.conv2(x)
        x = F.relu(x)
        x = F.max_pool2d(x, 2)
        x = torch.flatten(x, 1)
        x = self.fc1(x)
        x = F.relu(x)
        x = self.fc2(x)
        output = F.log_softmax(x, dim=1)
        return output


def make_cifar_model(**kwargs):
    return Net()


def get_art_model(model_kwargs, wrapper_kwargs, weights_path=None):
    model = make_cifar_model(**model_kwargs)
    model.to(DEVICE)

    if weights_path:
        checkpoint = torch.load(weights_path, map_location=DEVICE)
        model.load_state_dict(checkpoint)

    wrapped_model = PyTorchClassifier(
        model,
        loss=nn.CrossEntropyLoss(),
        optimizer=torch.optim.Adam(model.parameters(), lr=0.003),
        input_shape=(3, 32, 32),
        nb_classes=10,
        clip_values=(0.0, 1.0),
        **wrapper_kwargs,
    )
    return wrapped_model
