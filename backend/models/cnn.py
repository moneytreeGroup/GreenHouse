import torch
import torch.nn as nn
import torch.nn.functional as F


class SmallCNN(nn.Module):
    """
    5-layer CNN for plant species classification
    - 5 convolutional blocks with batch normalization
    - Gradual channel progression
    - Balanced capacity
    """

    def __init__(self, num_classes):
        super(SmallCNN, self).__init__()

        # 5 Convolutional blocks with gradual progression
        self.conv1 = nn.Conv2d(3, 64, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(64)

        self.conv2 = nn.Conv2d(64, 96, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(96)

        self.conv3 = nn.Conv2d(96, 128, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(128)

        self.conv4 = nn.Conv2d(128, 192, kernel_size=3, padding=1)
        self.bn4 = nn.BatchNorm2d(192)

        self.conv5 = nn.Conv2d(192, 256, kernel_size=3, padding=1)
        self.bn5 = nn.BatchNorm2d(256)

        # Pooling layers
        self.pool = nn.MaxPool2d(2, 2)
        self.adaptive_pool = nn.AdaptiveAvgPool2d((6, 6))

        # Single FC layer to prevent overfitting
        self.fc1 = nn.Linear(256 * 6 * 6, 512)
        self.dropout = nn.Dropout(0.7)
        self.fc2 = nn.Linear(512, num_classes)

    def forward(self, x):
        # Convolutional blocks with BatchNorm and ReLU
        x = self.pool(F.relu(self.bn1(self.conv1(x))))
        x = self.pool(F.relu(self.bn2(self.conv2(x))))
        x = self.pool(F.relu(self.bn3(self.conv3(x))))
        x = self.pool(F.relu(self.bn4(self.conv4(x))))
        x = self.pool(F.relu(self.bn5(self.conv5(x))))

        # Adaptive pooling
        x = self.adaptive_pool(x)

        # Flatten and fully connected layers
        x = x.view(x.size(0), -1)
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)

        return x

    def get_feature_maps(self, x):
        """Return intermediate feature maps for visualization"""
        features = []
        x = self.pool(F.relu(self.bn1(self.conv1(x))))
        features.append(x)
        x = self.pool(F.relu(self.bn2(self.conv2(x))))
        features.append(x)
        x = self.pool(F.relu(self.bn3(self.conv3(x))))
        features.append(x)
        x = self.pool(F.relu(self.bn4(self.conv4(x))))
        features.append(x)
        x = self.pool(F.relu(self.bn5(self.conv5(x))))
        features.append(x)
        return features
