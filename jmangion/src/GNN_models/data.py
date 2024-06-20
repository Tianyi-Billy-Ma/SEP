from torch_geometric.datasets import Planetoid
from arguments import parse_args

"""
torch version 2.3.1
torch_geometric version 2.5.3
"""

args = parse_args()
dataset = Planetoid(root=args.root_dir, name='Cora')

data = dataset[0]

"""
debugging stuff
print("x shape:")
print(data.x.shape)

print("Y shape:")
print(data.y.shape)
"""

"""
PubMed data notes
x shape:
torch.Size([19717, 500])
Y shape:
torch.Size([19717])
"""


# Cora data notes
# nodes: 2708
# train nodes: 140
# test nodes: 1000
# validation nodes: 500
# x is a 2708 x 1433 matrix that holds a feature vector in each row
# y is 2708 elements long and contains a class label at each index
# 

