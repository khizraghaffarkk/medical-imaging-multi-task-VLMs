import os
import pydicom
import matplotlib.pyplot as plt

folder_path = "./input_images/ct_scan/dicoms"  # your folder

dicom_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(".dcm")]
dicom_files.sort()  # optional: sort alphabetically

for f in dicom_files[:5]:  # preview first 5 slices
    ds = pydicom.dcmread(f)
    print(f"Filename: {f}")
    print(f"Patient: {ds.get('PatientName', 'Unknown')}")
    print(f"Modality: {ds.get('Modality', 'Unknown')}")
    print(f"Slice Location: {ds.get('SliceLocation', 'Unknown')}")
    print(f"Image shape: {ds.pixel_array.shape}")

    plt.imshow(ds.pixel_array, cmap='gray')
    plt.title(f"Slice: {ds.get('InstanceNumber', 'Unknown')}")
    plt.axis('off')
    plt.show()
