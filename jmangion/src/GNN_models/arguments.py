import argparse
import os

def parse_args():
    parser = argparse.ArgumentParser()
    root_dir = os.getcwd()
    parser.add_argument("--root_dir", type=str, default=root_dir)
    parser.add_argument("--data_dir", type=str, default=os.path.join(root_dir, "data"))
    parser.add_argument('--epochs', default=300, type=int)
    parser.add_argument('--runs', default=5, type=int)
    parser.add_argument('--dropout', default=0.4, type=float)
    parser.add_argument('--lr', default=0.001, type=float)
    parser.add_argument('--wd', default=0.001, type=float)
    parser.add_argument('--num_layers', default=2, type=int)
    parser.add_argument("--num_hidden", default=256, type=int)
    parser.add_argument('--num_features', default= 1, type=int)  # Placeholder 1433 for Cora
    parser.add_argument('--num_classes', default=1, type=int)  # Placeholder 7 for Cora 

    args = parser.parse_args()
    return args


def add_data_features(args, data):
    args.num_features = data.x.shape[1]
    args.num_classes = data.y.shape[0]
    return args




