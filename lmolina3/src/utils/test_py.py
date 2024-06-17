import torch
from torch_geometric.datasets import Planetoid

# Load Cora dataset
dataset = Planetoid(root='/tmp/cora', name='Cora')