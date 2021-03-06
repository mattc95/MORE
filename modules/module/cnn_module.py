import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

'''
The original file come from :
https://github.com/thunlp/RSN
'''


# embedding layers
class Embedding_word(nn.Module):

    def __init__(self, vocab_size, embedding_dim, weights, requires_grad=True):
        """
        the weights will be add one random vector for unk word
                add one zeros vector for blank word
                all weights should be trainable.
        :param vocab_size:
        :param embedding_dim:
        :param weights: the numpy version.
        :param trainable:
        """
        super(Embedding_word, self).__init__()
        self.word_embedding = nn.Embedding(vocab_size + 2, embedding_dim)
        unk_embedding = torch.nn.init.xavier_uniform_(torch.empty(1, embedding_dim)).cpu().numpy()
        blk_embedding = np.zeros((1, embedding_dim))

        weights = np.concatenate((weights, unk_embedding, blk_embedding), axis=0)

        self.word_embedding.weight.data.copy_(torch.from_numpy(weights))
        self.word_embedding.weight.requires_grad = requires_grad

    def forward(self, idx_input):
        return self.word_embedding(idx_input)


def model_init(m):
    if isinstance(m, nn.Conv1d):
        nn.init.normal_(m.weight, mean=0, std=1e-2)
        nn.init.normal_(m.bias, mean=0.5, std=1e-2)
    elif isinstance(m, nn.Linear):
        nn.init.normal_(m.weight, mean=0, std=1e-2)
        nn.init.normal_(m.bias, mean=0, std=2e-1)


class CNN(nn.Module):
    def __init__(self, cnn_input_shape, out_dim=64):
        """
        :param cnn_input_shape: [max_len, word_embedding+2 * pos_emb]
        """
        super().__init__()
        self.conv1 = nn.Conv1d(in_channels=cnn_input_shape[-1], out_channels=230, kernel_size=3)
        self.max_pool1 = nn.MaxPool1d(kernel_size=cnn_input_shape[0] - 2)

        self.linear = nn.Linear(230, out_dim)

    def forward(self, x):
        x = self.conv1(x)
        x = self.max_pool1(x)
        x = F.relu(x)
        x = x.reshape(-1, 230)

        return self.linear(x)


if __name__ == '__main__':
    # test for embedding
    cnn = CNN((120, 60))

    for name, weight in cnn.named_parameters():
        print("name:", name)
        print("weight:", weight)

    try:
        all_paprameters = sum([p.numel() for p in cnn.parameters() if p.requires_grad])
    except:
        print("error")

    print("There are {} parameters needed to be trained".format(all_paprameters))
    # summary(cnn, input_size=(60, 120))
    # print(cnn)

    # a = Embedding_word(10, embedding_dim=100, weights=np.random.random((10, 100)))
    # b = a(Variable(torch.from_numpy(np.array([[0, 1, 2, 11, 11, 11]], dtype=np.int64))))
    # fake_label = torch.rand(size=(6, 100))
    # optimizer = torch.optim.Adam(a.parameters())
    # loss = torch.nn.MSELoss()
    # l = loss(b, fake_label)
    #
    # optimizer.zero_grad()
    # l.backward()
    # # test done!
    # a.word_embedding.weight.grad[-1] = 0
    # optimizer.step()
    #
    # print(a.word_embedding.weight)
