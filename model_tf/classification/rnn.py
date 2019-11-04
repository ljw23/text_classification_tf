#!/usr/bin/env python
# coding:utf-8
"""
Tencent is pleased to support the open source community by making NeuralClassifier available.
Copyright (C) 2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance
with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License
is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied. See the License for thespecific language governing permissions and limitations under
the License.
"""

import tensorflow as tf
from tensorflow import keras
from util import Type


class RNNType(Type):
    RNN = 'RNN'
    LSTM = 'LSTM'
    GRU = 'GRU'

    @classmethod
    def str(cls):
        return ",".join([cls.RNN, cls.LSTM, cls.GRU])


class RNN(tf.keras.Model):
    """
    One layer rnn.
    """
    def __init__(self, config):
        super(RNN, self).__init__()
        self.config = config
        if  self.config.TextRNN.rnn_type == RNNType.LSTM:
            layer_cell = keras.layers.LSTM
        elif self.config.TextRNN.rnn_type == RNNType.GRU:
            layer_cell = keras.layers.GRU
        else:
            layer_cell = keras.layers.SimpleRNN

        self.rnn_type = config.TextRNN.rnn_type
        self.num_layers = config.TextRNN.num_layers
        self.bidirectional = config.TextRNN.bidirectional
        self.embedding = keras.layers.Embedding(config.TextRNN.input_dim, config.TextRNN.embedding_dimension,
                                                input_length=config.TextRNN.input_length)

        self.layer_cells = []
        for i in range(config.TextRNN.num_layers):
            self.layer_cells.append(keras.layers.Bidirectional(
                layer_cell(config.TextRNN.hidden_dimension,
                            use_bias=config.TextRNN.use_bias,
                            activation=config.TextRNN.activation,
                            kernel_regularizer=keras.regularizers.l2(self.config.TextRNN.l2 * 0.1),
                            recurrent_regularizer=keras.regularizers.l2(self.config.TextRNN.l2))))

        self.fc = keras.layers.Dense(config.TextRNN.num_classes)

    def call(self, inputs, training=None, mask=None):

        print('inputs', inputs)
        # [b, sentence len] => [b, sentence len, word embedding]
        x = self.embedding(inputs)
        print('embedding', x)
        for layer_cell in self.layer_cells:
            x = layer_cell(x)
        print('rnn', x)

        x = self.fc(x)
        print(x.shape)

        if self.config.logits_type == "softmax":
            x = tf.nn.softmax(x)
        elif self.config.logits_type == "sigmoid":
            x = tf.nn.sigmoid(x)

        return x


