import os

from examples import draw_flow_field

if __name__ == '__main__':
    output_folder = 'Images'
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    # Creation starts here
    draw_flow_field(1000, 1000)
