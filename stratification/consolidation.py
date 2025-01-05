import os
import shutil
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from sklearn.model_selection import train_test_split

def consolidate_files(source_dirs, target_dir):
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff')
    label_extensions = ('.txt',)

    image_dir = os.path.join(target_dir, 'images')
    label_dir = os.path.join(target_dir, 'labels')

    os.makedirs(image_dir, exist_ok=True)
    os.makedirs(label_dir, exist_ok=True)

    for source_dir in source_dirs:
        for root, _, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                file_extension = os.path.splitext(file)[1].lower()

                if file_extension in image_extensions:
                    destination = os.path.join(image_dir, file)
                elif file_extension in label_extensions:
                    destination = os.path.join(label_dir, file)
                else:
                    continue

                shutil.copy2(file_path, destination)

    print(f"Files consolidated successfully in {target_dir}")
    return image_dir, label_dir

def get_class_labels(label_dir):
    class_labels = set()
    for file in os.listdir(label_dir):
        if file.endswith('.txt'):
            with open(os.path.join(label_dir, file), 'r') as f:
                for line in f:
                    class_label = line.strip().split()[0]
                    class_labels.add(class_label)
    return sorted(list(class_labels))

def replace_class_labels(label_dir, class_mapping):
    for file in os.listdir(label_dir):
        if file.endswith('.txt'):
            file_path = os.path.join(label_dir, file)
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            modified = False
            new_lines = []
            for line in lines:
                parts = line.strip().split()
                if parts:
                    old_class = parts[0]
                    if old_class in class_mapping:
                        parts[0] = class_mapping[old_class]
                        modified = True
                new_lines.append(' '.join(parts) + '\n')
            
            if modified:
                with open(file_path, 'w') as f:
                    f.writelines(new_lines)
    
    print(f"Class labels replaced successfully in {label_dir}")


def stratify_and_split_dataset(image_dir, label_dir, output_dir, train_ratio=0.6, val_ratio=0.2, test_ratio=0.2):
    # Get all image and label files
    image_files = [f for f in os.listdir(image_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    label_files = [f for f in os.listdir(label_dir) if f.lower().endswith('.txt')]

    # Ensure image and label files match
    image_files = [f for f in image_files if os.path.splitext(f)[0] + '.txt' in label_files]
    label_files = [os.path.splitext(f)[0] + '.txt' for f in image_files]

    # Get class labels for stratification
    class_labels = []
    for label_file in label_files:
        with open(os.path.join(label_dir, label_file), 'r') as f:
            classes = set([line.strip().split()[0] for line in f])
            class_labels.append(','.join(sorted(classes)))
    
    # Split the dataset
    train_images, test_val_images, train_labels, test_val_labels = train_test_split(
        image_files, label_files, test_size=(1 - train_ratio), stratify= None, random_state=42
    )

    val_ratio_adjusted = val_ratio / (val_ratio + test_ratio)
    val_images, test_images, val_labels, test_labels = train_test_split(
        test_val_images, test_val_labels, test_size=(1 - val_ratio_adjusted), stratify=None, random_state=42
    )

    # Create output directories
    for split in ['train', 'val', 'test']:
        os.makedirs(os.path.join(output_dir, split, 'images'), exist_ok=True)
        os.makedirs(os.path.join(output_dir, split, 'labels'), exist_ok=True)

    # Copy files to respective directories
    for images, labels, split in [(train_images, train_labels, 'train'),
                                  (val_images, val_labels, 'val'),
                                  (test_images, test_labels, 'test')]:
        for img, lbl in zip(images, labels):
            shutil.copy2(os.path.join(image_dir, img), os.path.join(output_dir, split, 'images', img))
            shutil.copy2(os.path.join(label_dir, lbl), os.path.join(output_dir, split, 'labels', lbl))

    print(f"Dataset stratified and split successfully in {output_dir}")
    print(f"Train: {len(train_images)}, Validation: {len(val_images)}, Test: {len(test_images)}")
   
    # Plot class distribution
    plot_combined_class_distribution(output_dir)

# выводим результат стратификации на экран
def plot_combined_class_distribution(output_dir):
    splits = ['train', 'val', 'test']
    class_counts = {split: Counter() for split in splits}

    for split in splits:
        label_dir = os.path.join(output_dir, split, 'labels')
        label_files = [f for f in os.listdir(label_dir) if f.lower().endswith('.txt')]

        for label_file in label_files:
            with open(os.path.join(label_dir, label_file), 'r') as f:
                classes = [line.strip().split()[0] for line in f]
                class_counts[split].update(classes)

    all_classes = sorted(set.union(*[set(counts.keys()) for counts in class_counts.values()]))

    fig, ax = plt.subplots(figsize=(15, 8))
    bar_width = 0.25
    index = np.arange(len(all_classes))

    for i, split in enumerate(splits):
        counts = [class_counts[split][cls] for cls in all_classes]
        ax.bar(index + i * bar_width, counts, bar_width, label=split.capitalize())

    ax.set_xlabel('Class Labels')
    ax.set_ylabel('Number of Instances')
    ax.set_title('Combined Class Distribution for Train, Validation, and Test Sets')
    ax.set_xticks(index + bar_width)
    ax.set_xticklabels(all_classes, rotation=45, ha='right')
    ax.legend()

    plt.tight_layout()
    plot_path = os.path.join(output_dir, 'combined_class_distribution.png')
    plt.savefig(plot_path)
    plt.close()

    print(f"Combined class distribution plot saved to {plot_path}")



# Usage example:
source_directories = [rf'Для отчета\dataset_symbols_correct']
target_directory = rf'Для отчета\dataset_symbols_correct_new\data_prepared'
image_dir, label_dir = consolidate_files(source_directories, target_directory)
print(get_class_labels(label_dir))
class_mapping = {
     '0': '0',
     '1': '1',
     '2': '2',
     '3': '3',
     '4': '4',
     '5': '5',
     '6': '6',
     '7': '7',
     '8': '8',
     '9': '9',
     '10': '10',
     '11': '11',
     '12': '12',
     '13': '13',
     '14': '14',
     '15': '15',
     '16': '16',
     '17': '17',
     '18': '18',
     '19': '19',
     '20': '20',
     '21': '21',
    #  '22': '0',
     '23': '22',
    #  '24': '1',
    #  '25': '2',
    #  '26': '1'
     # Add more mappings as needed
 }
replace_class_labels(label_dir, class_mapping)
print(get_class_labels(label_dir))

# Usage example:
output_directory = rf'Для отчета\dataset_symbols_correct_new\datasets'
stratify_and_split_dataset(image_dir, label_dir, output_directory)