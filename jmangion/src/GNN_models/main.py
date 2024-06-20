import torch
import torch.nn.functional as F
from data import dataset
from arguments import parse_args, add_data_features
from model import GCN_model


def train(model, X, Y,data):
    model.train()
    optimizer = torch.optim.Adam(model.parameters(), lr = model.lr, weight_decay = model.wd)
    optimizer.zero_grad()
    activations = model(X, data.edge_index)

    # only calculate loss on train labels!!
    loss = F.nll_loss(activations[data.train_mask], Y[data.train_mask])
    loss.backward()
    optimizer.step()

def get_masked_acc(activations, y_true, mask):
    length = activations[mask].shape[0]
    correct = 0
    for yhat, y in zip(activations[mask], y_true[mask]):
        if torch.argmax(yhat) == y:
            correct += 1

    return correct / length

def get_accuracy(activations, y_true, data):
    train_acc = get_masked_acc(activations, y_true, data.train_mask)
    test_acc = get_masked_acc(activations, y_true, data.test_mask)
    val_acc = get_masked_acc(activations, y_true, data.val_mask)
    return train_acc, test_acc, val_acc


def main():
    # get data
    data = dataset[0]
    x = data.x
    y = data.y

    # get preferences
    args = parse_args()
    args = add_data_features(args, data)

    for run in range(args.runs):
        # initialize model
        model = GCN_model(args)

        print("\n------------ new model ------------\n")
        for epoch in range(args.epochs):

            # backprop & update
            train(model, x, y, data.edge_index, data)

            # log loss every 50 steps
            if epoch % 50 == 0 or epoch == args.epochs - 1:
                model.eval()
                activations = model(x, data.edge_index)
                loss = F.nll_loss(activations, y)
                train_acc, test_acc, val_acc = get_accuracy(activations, y, data)
                print(f" Epoch: {epoch} | Total Loss: {loss} | Train Accuracy: {train_acc} | Test Accuracy: {test_acc} | Val Accuracy: {val_acc}")


if __name__ == '__main__':
    main()













