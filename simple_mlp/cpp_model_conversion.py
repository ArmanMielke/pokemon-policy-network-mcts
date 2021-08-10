import torch

from switch_equivariant_agent import SwitchEquivariantAgent


def convert_model_for_cpp(
    source_checkpoint_path: str,
    out_path: str,
    p1_pokemon_size: int,
    p2_pokemon_size: int,
    num_pokemon: int,
    label_type: int = 1
):
    # load model
    p2_size = num_pokemon * p2_pokemon_size
    model = SwitchEquivariantAgent(p1_pokemon_size, p2_size, label_type)
    model_parameters = torch.load(source_checkpoint_path, map_location=torch.device('cpu'))
    model.load_state_dict(model_parameters)

    # convert the model to torch script
    # https://pytorch.org/tutorials/advanced/cpp_export.html#converting-to-torch-script-via-tracing
    example_batch_size = 128
    example_input_p1 = torch.rand(example_batch_size, num_pokemon, p1_pokemon_size)
    example_input_p2 = torch.rand(example_batch_size, num_pokemon, p2_pokemon_size)
    # Use torch.jit.trace to generate a torch.jit.ScriptModule via tracing
    traced_script_model = torch.jit.trace(model, (example_input_p1, example_input_p2))

    # save converted model
    traced_script_model.save(out_path)
