from django.core.management.base import BaseCommand
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np


class Command(BaseCommand):
    help = "Train the embedding model using session data"

    def handle(self, *args, **options):
        def load_session_data(file_path):
            with open(file_path, "r") as infile:
                session_data = [
                    list(map(int, line.strip().split())) for line in infile.readlines()
                ]
            return session_data

        file_path = "nadooit_website/TrainingData/session_data.txt"
        session_data = load_session_data(file_path)

        embedding_dim = 128
        num_signal_types = 1000

        class EmbeddingModel(nn.Module):
            def __init__(self, num_signal_types, embedding_dim):
                super(EmbeddingModel, self).__init__()
                self.embedding = nn.Embedding(num_signal_types, embedding_dim)

            def forward(self, x):
                return self.embedding(x)

        model = EmbeddingModel(num_signal_types, embedding_dim)
        criterion = nn.MSELoss()
        optimizer = optim.SGD(model.parameters(), lr=0.01)

        session_data_tensors = [
            torch.tensor(session, dtype=torch.long) for session in session_data
        ]

        num_epochs = 100

        for epoch in range(num_epochs):
            for session in session_data_tensors:
                optimizer.zero_grad()
                embeddings = model(session)
                target = torch.zeros_like(embeddings)
                loss = criterion(embeddings, target)
                loss.backward()
                optimizer.step()

            print(f"Epoch {epoch + 1}/{num_epochs}, Loss: {loss.item()}")

        embedding_matrix = model.embedding.weight.detach().numpy()
        np.save("nadooit_website/TrainingData/embeddings.npy", embedding_matrix)
