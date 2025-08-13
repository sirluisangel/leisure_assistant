# app/emotion_net.py
# Red neuronal PyTorch para clasificación emocional (densa)
import torch, os, json, numpy as np
import torch.nn as nn

# Lista de emociones, agregadas nuevas emociones
EMOTIONS = ['Feliz', 'Triste', 'Enojado', 'Estresado', 'Desesperado', 'Miedo', 'Sorpresa', 'Avergonzado', 'Calma']

class EmotionNet(nn.Module):
    def __init__(self, input_dim=384, hidden_dim=256, output_dim=len(EMOTIONS)):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.dropout = nn.Dropout(0.3)
        self.fc2 = nn.Linear(hidden_dim, 128)
        self.fc3 = nn.Linear(128, output_dim)  # El output_dim ahora está basado en la longitud de EMOTIONS
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        return self.fc3(x)

def load_model_state(model, path):
    state = torch.load(path, map_location='cpu')
    model.load_state_dict(state)

def model_infer(model, vec):
    model.eval()
    with torch.no_grad():
        x = torch.tensor(vec, dtype=torch.float32).unsqueeze(0)
        logits = model(x)
        probs = torch.softmax(logits, dim=1).cpu().numpy()[0]
        idx = int(probs.argmax())
        return EMOTIONS[idx], float(round(probs[idx], 2))

# utilities to train quickly with small dataset (example)
def train_small(model, X, y, epochs=30):
    # X: numpy array shape (n, dim), y: int labels
    import torch.optim as optim
    model.train()
    X_t = torch.tensor(X, dtype=torch.float32)
    y_t = torch.tensor(y, dtype=torch.long)
    opt = optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = nn.CrossEntropyLoss()
    for e in range(epochs):
        opt.zero_grad()
        logits = model(X_t)
        loss = loss_fn(logits, y_t)
        loss.backward()
        opt.step()
    return model