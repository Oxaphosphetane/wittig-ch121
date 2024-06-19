import pandas as pd
from rdkit import Chem
import deepchem as dc
from deepchem.feat import MolGraphConvFeaturizer

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import dgl
import dgl.nn.pytorch as dglnn
import numpy as np

import os
import sys

# Get the current working directory
current_dir = os.getcwd()

# Get the parent directory
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))

# Add the parent directory to the system path
sys.path.insert(0, parent_dir)

import os_navigation as os_nav
from dft.molecule import MoleculeInfo

print('Loaded all modules.')

# Load the CSV file
file_path = os.path.join(os_nav.find_project_root(), 'data', 'cis_op_for_galaxy')
df = pd.read_csv(file_path)

# Assume the SMILES column is named 'smiles'
smiles_list = df['reactant_smiles'].tolist()

# Featurize the molecules
featurizer = MolGraphConvFeaturizer(use_edges=True)
molecular_graphs = featurizer.featurize(smiles_list)

print('Featurized molecular graphs.')


class GraphEncoder(nn.Module):
    def __init__(self, in_feats, hidden_feats):
        super(GraphEncoder, self).__init__()
        self.conv1 = dglnn.GraphConv(in_feats, hidden_feats, activation=F.relu)
        self.conv2 = dglnn.GraphConv(hidden_feats, hidden_feats, activation=F.relu)

    def forward(self, g, inputs):
        h = self.conv1(g, inputs)
        h = self.conv2(g, h)
        return h


class GraphDecoder(nn.Module):
    def __init__(self, hidden_feats, out_feats):
        super(GraphDecoder, self).__init__()
        self.conv1 = dglnn.GraphConv(hidden_feats, hidden_feats, activation=F.relu)
        self.conv2 = dglnn.GraphConv(hidden_feats, out_feats)

    def forward(self, g, inputs):
        h = self.conv1(g, inputs)
        h = self.conv2(g, h)
        return h


class GraphAutoencoder(nn.Module):
    def __init__(self, in_feats, hidden_feats, out_feats):
        super(GraphAutoencoder, self).__init__()
        self.encoder = GraphEncoder(in_feats, hidden_feats)
        self.decoder = GraphDecoder(hidden_feats, out_feats)

    def forward(self, g, inputs):
        encoded = self.encoder(g, inputs)
        decoded = self.decoder(g, encoded)
        return encoded, decoded


print('Created model classes.')


# Create the dataset
dataset = dc.data.NumpyDataset(molecular_graphs)

print('Created dataset.')

# Initialize the model
in_feats = molecular_graphs[0].node_features.shape[1]
hidden_feats = 64  # Hidden layer size
out_feats = in_feats
model = GraphAutoencoder(in_feats, hidden_feats, out_feats).cuda()

print('Initialized model.')

# Training settings
learning_rate = 0.001
epochs = 100

# Define loss function and optimizer
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=learning_rate)

# Training loop
for epoch in range(epochs):
    total_loss = 0
    for data in dataset.itersamples():
        g = data[0].to_dgl_graph().to('cuda')
        inputs = torch.tensor(g.ndata['h'], dtype=torch.float32).to('cuda')

        # Forward pass
        encoded, decoded = model(g, inputs)

        # Compute loss
        loss = criterion(decoded, inputs)

        # Backward pass and optimization
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    print(f'Epoch {epoch + 1}/{epochs}, Loss: {total_loss / len(dataset)}')

print("Training completed.")

embeddings = []

with torch.no_grad():
    for data in dataset.itersamples():
        g = data[0].to_dgl_graph().to('cuda')
        inputs = torch.tensor(g.ndata['h'], dtype=torch.float32).to('cuda')

        # Get embeddings
        encoded, _ = model(g, inputs)
        embeddings.append(encoded.cpu().numpy())

embeddings = np.array(embeddings)
np.save('molecule_embeddings.npy', embeddings)
print("Embeddings saved to 'molecule_embeddings.npy'.")


