#utils/check_gpu.py

import torch

# Check if a CUDA-enabled GPU is available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using device:", device)

# Example: Move a tensor to the GPU
tensor = torch.randn(3, 3).to(device)
print("Tensor on device:", tensor.device)
