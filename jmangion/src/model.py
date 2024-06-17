import torch
import torch.nn as nn
import torch_geometric
from torch_geometric.nn import GCNconv
import arguments



# checking imports
print(torch.__version__)
print(torch_geometric.__version__)





# defining a model

def make_layers():
    # get arguments
    args = arguments.parse_args()
    layers = []
    for i in range(args.num_layers):
        if i == 0:  # first layer 
            # dimensions in = input data size
            # dimensions out = hidden layer size
            layer = GCNConv(args.num_features, args.num_hidden)

        elif i < args.num_layers - 1: # hidden layer(s)
            # dimensions in = hidden layer size
            # dimensions out = hidden layer size 
            layer = GCNConv(args.num_hidden, args.num_hidden)

        else:  # output layer
            # dimensions in = hidden layer size
            # dimensions out = output size
            layer = GCNConv(args.num_hidden, args.num_classes)

        layers.append(layer)


    return nn.ModuleList(layers)



class GCN(nn.Module):
    def __init__(self):
        super().__init__()
        args = arguments.parse_args()
        self.num_layers = args.num_layers
        self.num_hidden = args.num_hidden




    def forward(self, x, edge_index):








