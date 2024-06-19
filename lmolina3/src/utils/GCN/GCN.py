import torch
import torch.nn.functional as F
from torch_geometric.nn import GCNConv


class GCN(torch.nn.Module):

    def __init__(self, num_features, hidden, num_classes):
        super().__init__()
        self.conv_1 = GCNConv(num_features, hidden)
        self.conv_2 = GCNConv(hidden, num_classes)

    def forward(self, data):
        x, edge_index = data.x, data.edge_index
        # pass thorugh first layer 
        x = self.conv_1(x, edge_index)
        # do activation function 
        x = F.relu(x)
        # drop out for regularization, reduces overfitting 
        x = F.dropout(x, training=self.training)
        # pass through second layer
        x = self.conv_2(x, edge_index)
        # computes the softmax algo 
        x = F.log_softmax(x, dim=1)
        return x