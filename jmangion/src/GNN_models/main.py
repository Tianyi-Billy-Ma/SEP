import torch
import sys
import torch.nn.functional as F
from data import dataset
from arguments import parse_args
from model import GCN_model

sys.dont_write_bytecode = True

def train(model, X, Y, edge_indices):
    model.train()
    optimizer = torch.optim.Adam(model.parameters(), lr = 0.001, weight_decay = model.wd)
    optimizer.zero_grad()
    activations = model(X, edge_indices)
    loss = F.nll_loss(activations, Y)
    loss.backward()
    optimizer.step()

def main():
    # get data
    data = dataset[0]
    # training data
    x_train = data.x[data.train_mask]
    y_train = data.y[data.train_mask]
    # testing data
    x_test = data.x[data.test_mask]
    y_test = data.y[data.test_mask]
    # validation data
    x_val = data.x[data.val_mask]
    y_val = data.y[data.val_mask]

    # get preferences
    args = parse_args()

    for run in range(args.runs):
        # initialize model
        model = GCN_model()
        print("\n------------ new model ----------\n")

        for epoch in range(args.epochs):
            # backprop & update
            train(model, x_train, y_train, data.edge_index)

            # print accuracy every 50 steps
            if epoch % 50 == 0:
                model.eval()
                train_activations = model(x_train, edge_indices)
                train_loss = F.nll_loss(train_activations, y_train)
                test_activations = model(x_test, edge_indices)
                test_loss = F.nll_loss(test_activations, y_test)
                val_activations = model(x_val, edge_index)
                val_loss = F.nll_loss(val_activations, y_val)
                print(f"Train loss: {train_loss} | Test loss: {test_loss} | Validation Loss: {val_loss}")
                # TODO: report accuracy 


if __name__ == '__main__':
    main()













