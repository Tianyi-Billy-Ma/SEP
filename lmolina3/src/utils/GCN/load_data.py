import os 
import torch
from torch_geometric.datasets import Planetoid

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

cwd = r'C:\Users\16822\Research Project SER\SEP-NHANES\lmolina3\src\utils\GCN\Data'


dataset = Planetoid(root=cwd, name='Cora')
data = dataset[0].to(device)
# print(dataset.num_classes)
# print(dataset.num_edge_features)
# print(dataset.num_features)
# print(dataset.num_node_features)
# print(data.x)
# print(data.y)
# print(data.edge_attrs)
# print(data.edge_index)
