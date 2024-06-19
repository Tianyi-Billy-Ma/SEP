import torch
from torch_geometric.nn import GCNConv
from torch_geometric.datasets import Planetoid
import torch.nn.functional as F

# data.x node features
# data.edge is graph connectivity 
# data.y node labels

SAVE_PATH = r'C:\Users\16822\Research Project SER\SEP-NHANES\lmolina3\src\utils\Data'

def get_data_sets(data):
    train_data = data.train_mask
    val_data = data.val_mask
    test_data = data.test_mask
    return train_data, val_data, test_data
    
def train(data,train_data, model, optimizer):
    model.train()
    optimizer.zero_grad()
    out = model(data)
    loss = F.nll_loss(out[train_data], data.y[train_data])
    loss.backward()
    optimizer.step()

# def validate(model, data, val_data):
#     model.eval()
#     with torch.no_grad():
#         out = model(data)
#         val_loss = F.nll_loss(out[val_data], data.y[val_data].item())
#         pred = out[val_data].argmax(dim = 1)


def run(data, train_data, model, optimizer, epochs=200):
    for epoch in epochs:
        train(data, train_data, model, optimizer)
        validate()



def main_func():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    dataset = Planetoid(root=SAVE_PATH, name = 'Cora')
    data = dataset[0].to(device)
    train_data, val_data, test_data, = get_data_sets(data)

    model = GCN(dataset).to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

    train(data, train_data, model, optimizer)
    # datasets = {}
    # data_cleaned = {}
    # for name in ['Cora', 'CiteSeer', 'PubMed']:
    #     datasets[name] = Planetoid(root=SAVE_PATH, name=name)
    #     data = datasets[name][0].to(device)
    #     train_data, val_data, test_data = get_data_sets(data)
    #     data_cleaned[name] = [train_data, val_data, test_data]
    #     print(train_data, val_data, test_data)


class GCN(torch.nn.Module):
    def __init__(self, data):
        super().__init__()
        self.conv1 = GCNConv(data.num_node_features, 256)
        self.conv2 = GCNConv(256, data.num_classes)

    def forward(self, data):
        x, edge_index = data.x, data.edge_index

        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = F.dropout(x, p=0.5)
        x = self.conv2(x, edge_index)

        return F.log_softmax(x, dim=1)

if __name__ == '__main__': 
    main_func()


    