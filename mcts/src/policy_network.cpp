#include "policy_network.h"

#include <torch/script.h>


// see https://pytorch.org/tutorials/advanced/cpp_export.html#step-3-loading-your-script-module-in-c
PolicyNetwork::PolicyNetwork(std::string const model_path) {
    this->model = torch::jit::load(model_path);
}

// see https://pytorch.org/tutorials/advanced/cpp_export.html#step-4-executing-the-script-module-in-c
torch::Tensor PolicyNetwork::forward(const torch::Tensor p1, const torch::Tensor p2) {
    // create a vector of inputs
    std::vector<torch::jit::IValue> inputs = {p1, p2};
    // execute the model and turn its output into a tensor
    return model.forward(inputs).toTensor();
}
