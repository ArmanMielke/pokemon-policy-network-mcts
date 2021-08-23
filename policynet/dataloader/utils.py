from .dataconverter import DataConverter

def print_input(input):
    msg = f"HP: {input[0]}, Enemy HP: {input[-1]}"
    print(msg)

def print_batch(batch):
    dataconverter = DataConverter()
    data = batch[0]
    print_input(data)