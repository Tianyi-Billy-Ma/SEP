import torch
import sys
import torch.nn.functional as F
from data import dataset
from arguments import parse_args
from model import GCN_model

sys.dont_write_bytecode = True

def train(model, X, Y, edge_indices):
    model.train()
    optimizer = torch.optim.Adam(model.parameters(), lr = model.lr, weight_decay = model.wd)
    optimizer.zero_grad()
    activations = model(X, edge_indices)
    loss = F.nll_loss(activations, Y)
    loss.backward()
    optimizer.step()


def main():
    # get data
    data = dataset[0]

    # using the entire training and test set does not cause the indexing issue that appears in 'main.py'
    x = data.x
    y = data.y

    # get preferences
    args = parse_args()

    for run in range(args.runs):
        # initialize model
        model = GCN_model()
        print("\n------------ new model ------------\n")
        for epoch in range(args.epochs):

            # backprop & update
            train(model, x, y, data.edge_index)

            # log loss every 50 steps
            if epoch % 50 == 0:
                model.eval()
                train_activations = model(x, data.edge_index)
                train_loss = F.nll_loss(train_activations, y)
                print(f"Train loss: {train_loss}")
                # TODO: report accuracy


if __name__ == '__main__':
    main()













