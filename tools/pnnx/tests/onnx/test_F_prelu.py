# Tencent is pleased to support the open source community by making ncnn available.
#
# Copyright (C) 2024 THL A29 Limited, a Tencent company. All rights reserved.
#
# Licensed under the BSD 3-Clause License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
# https://opensource.org/licenses/BSD-3-Clause
#
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import torch
import torch.nn as nn
import torch.nn.functional as F

class Model(nn.Module):
    def __init__(self):
        super(Model, self).__init__()

        self.w4 = nn.Parameter(torch.rand(16))
        self.w5 = nn.Parameter(torch.rand(2))
        self.w6 = nn.Parameter(torch.rand(3))
        self.w7 = nn.Parameter(torch.rand(1))

    def forward(self, x, y, z, w, w0, w1, w2, w3):
        x = x * 2 - 1
        y = y * 2 - 1
        z = z * 2 - 1
        w = w * 2 - 1
        x = F.prelu(x, w0)
        x = F.prelu(x, self.w4)
        y = F.prelu(y, w1)
        y = F.prelu(y, self.w5)
        z = F.prelu(z, w2)
        z = F.prelu(z, self.w6)
        w = F.prelu(w, w3)
        w = F.prelu(w, self.w7)
        return x, y, z, w

def test():
    net = Model()
    net.eval()

    torch.manual_seed(0)
    x = torch.rand(1, 16)
    y = torch.rand(12, 2, 16)
    z = torch.rand(1, 3, 12, 16)
    w = torch.rand(1, 5, 7, 9, 11)
    w0 = torch.rand(16)
    w1 = torch.rand(2)
    w2 = torch.rand(3)
    w3 = torch.rand(1)

    a = net(x, y, z, w, w0, w1, w2, w3)

    # export onnx
    torch.onnx.export(net, (x, y, z, w, w0, w1, w2, w3), "test_F_prelu.onnx")

    # onnx to pnnx
    import os
    os.system("../../src/pnnx test_F_prelu.onnx inputshape=[1,16],[12,2,16],[1,3,12,16],[1,5,7,9,11],[16],[2],[3],[1]")

    # pnnx inference
    import test_F_prelu_pnnx
    b = test_F_prelu_pnnx.test_inference()

    for a0, b0 in zip(a, b):
        if not torch.equal(a0, b0):
            return False
    return True

if __name__ == "__main__":
    if test():
        exit(0)
    else:
        exit(1)
