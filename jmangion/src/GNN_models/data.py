from torch_geometric.datasets import Planetoid
from arguments import parse_args


args = parse_args()
dataset = Planetoid(root=args.root_dir, name='Cora')


# data notes
# nodes: 2708
# train nodes: 140
# test nodes: 1000
# validation nodes: 500
# x is a 2708 x 1433 matrix that holds a feature vector in each row
# y is 2708 elements long and contains a class label at each index
# 

