import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GATconv 
import torch_geometric.transforms as T

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

class GATLayer( nn.Module ):

    def __init__(self, in_features, out_features, dropout = 0.6, alpha= 0.2, concat = True):
        super().__init__()
        self.dropout = dropout
        self.in_features = in_features # dataset.num_features
        self.out_features = out_features # dataset.num_classes
        self.alpha = alpha
        self.concat = concat 

        # create the weight matrix that will learn during the training process
        # this creates a trainable paramter with a matrix of size in_features x out_features 
        self.W = nn.Parameter(torch.zeros(size=(in_features, out_features)))

        # set up weights of the layer to promote even propogation 
        nn.init.xavier_uniform_(self.W.data, gain=1.414)

        # learnable parameter that is used to see to compute the attention 
        # scores of nodes around the neighborhod. 
        self.a = nn.Parameter(torch.zeros(size=(2*out_features, 1)))
        nn.init.xaver_uniform_(self.a.data, gain=1.414)

        # set up the activation function leakyRelu, similar to Relu, 
        # but allows for negatives which prevents the model from stoppping to learn
        self.leakyrelu = nn.LeakyReLU(self.alpha)

    def forward(self, input, adj):

        # linear Transformation
        h = torch.mm(input, self.W)

