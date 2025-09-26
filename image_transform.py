from torch.utils.data import random_split
from torchvision import transforms
from torchvision.datasets import ImageFolder


def transform_image(image_path: str):
    # Manual Transform the dataset
    manual_transform = transforms.Compose([
        transforms.Resize((150, 150)),
        transforms.ToTensor(),
    ])

    # create dataset using ImageFolder
    dataset = ImageFolder(root=image_path,
                        transform=manual_transform)

    # create train dataset from dataset
    train_size = int(0.8 * len(dataset))
    test_val_size = len(dataset) - train_size
    train_data, test_val_data = random_split(dataset, [train_size, test_val_size])

    # create test and validation set frm test_val_dataset
    test_size = int(0.5 * len(test_val_data))
    val_size = len(test_val_data) - test_size
    test_data, val_data = random_split(test_val_data, [test_size, val_size])

    # create class names
    class_names = dataset.classes

    return train_data, test_data, val_data, class_names
