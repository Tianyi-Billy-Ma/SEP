import torch
import torch.optim as optim 
import torch.nn.functional as F
from torch_geometric.loader import DataLoader
from load_data import data, dataset
from GCN import GCN


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
# Separate data into train, validation, and test sets
train_mask = data.train_mask
val_mask = data.val_mask
test_mask = data.test_mask

# node features 
train_data_x = data.x[train_mask]
test_data_x = data.x[test_mask]
val_data_x  = data.x[val_mask]

# node labels
train_data_y = data.y[train_mask]
test_data_y = data.y[test_mask]
val_data_y = data.y[val_mask]

# print(train_data)
# print(train_data.shape)
node_features_for_train_data = train_data_x.shape[1]
num_classes_for_model = dataset.num_classes


model = GCN(num_features=node_features_for_train_data, hidden=256, num_classes= num_classes_for_model).to(device)
optimizer = optim.Adam(model.parameters(), lr= 0.01)

def train(model, optimizer, data):
    global train_mask, train_data_y
    model.train()
    optimizer.zero_grad()
    out = model(data) 
    loss = F.nll_loss(out[train_mask], train_data_y)
    loss.backward()
    optimizer.step()

    return loss.item()


# Example usage:
# train(model, optimizer, criterion, train_loader)s
def evaluate(model, data, val_mask):

    model.eval()
    with torch.no_grad():
        logits = model(data)
        prediction = logits[val_mask].max(1)[1]
        correct = prediction.eq(data.y[val_mask]).sum().item()
        acc = correct / val_mask.sum().item()
        loss = F.nll_loss(logits[val_mask], data.y[val_mask])
        print(acc)
        return acc, loss.item()


def test(model, data):
    model.eval()
    acc, loss, = evaluate(model, data, data.test_mask)
    return acc, loss


def main():
    global val_mask 
    # train_load = DataLoader(list(zip(train_data_x, train_data_y)), batch_size = 64, shuffle = True)
    val_accs, val_losses = [], []
    best_val_accs = 0.0
    best_model_state = None

    for epoch in range(1,301):
        loss_on_train = train(model, optimizer, data)
        val_acc, val_loss = evaluate(model, data, val_mask)

        val_accs.append(val_acc)
        val_losses.append(val_loss)
        
        if val_acc > best_val_accs:
            best_val_accs = val_acc
            best_model_state = model.state_dict()

        print(f'Epoch {epoch}, Train loss: {loss_on_train:.4f}, val loss: {val_loss:.4f}, Val acc: {val_acc:.4f}')
    if best_model_state:
        model.load_state_dict(best_model_state)
    test_acc, test_loss = test(model, data)
    print(f"Test accuracy: {test_acc: .4f}, Text loss {test_loss: .4f}")


if __name__ == '__main__':
    main()
