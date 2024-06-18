import torch.nn as nn
import torch_geometric
from torch_geometric.nn import GCNConv
import torch.nn.functional as F
import arguments

def make_layers(self):
    layers = []
    # initialize layers in a loop that uses conditionals to determine the input and output dimensions of the feature vectors
    for i in range(self.num_layers):
        if i == 0:  # first layer 
            # dimensions in = input data size
            # dimensions out = hidden layer size
            layer = GCNConv(self.num_features, self.num_hidden)

        elif i < self.num_layers - 1: # hidden layer(s)
            # dimensions in = hidden layer size
            # dimensions out = hidden layer size 
            layer = GCNConv(self.num_hidden, self.num_hidden)

        else:  # output layer
            # dimensions in = hidden layer size
            # dimensions out = output size
            layer = GCNConv(self.num_hidden, self.num_classes)

        layers.append(layer)

    return nn.ModuleList(layers)

class GCN_model(nn.Module):
    def __init__(self):
        super().__init__()
        args = arguments.parse_args()
        self.num_features = args.num_features
        self.num_layers = args.num_layers
        self.num_hidden = args.num_hidden
        self.num_classes = args.num_classes
        self.wd = args.wd
        self.lr = args.lr
        self.layers = make_layers(self)

    def forward(self, x, edge_idx):
        for i, layer in enumerate(self.layers):
            # apply the convolutional layer
            x = layer(x, edge_idx)

            # Since I did not apply the activation function in the Layers array, I apply it using conditionals (to decide relu or softmax) here
            if i != len(self.layers) - 1:
                x = F.relu(x)
            else:
                x = F.log_softmax(x, dim = 1)

        return x

