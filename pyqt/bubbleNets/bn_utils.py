# Utils for BubbleNets.
def read_annotation_list(text_file):
    read_list = read_list_file(text_file)
    n_ant = int(read_list[0].split(' ')[0])
    ant_idx = []; ant_file = []
    for i in range(n_ant):
        ant_idx.append(int(read_list[i*2+1]))
        ant_file.append(read_list[i*2+2])
    return ant_idx, ant_file

def num_unique(video_list):
    unique_list = []
    for _, video in enumerate(video_list):
        if not video[:-1] in unique_list:
            unique_list.append(video[:-1])
    return len(unique_list), unique_list

def read_list_file(file_name):
    read_list = open(file_name,'r').readlines()
    for i in range(len(read_list)):
        read_list[i] = read_list[i].strip('\n')
    return read_list

def print_out_text(file_name, text, arg='a'):
    output_file = open(file_name, arg)
    output_file.write(str(text))
    output_file.close()

def print_statements(file_name, statements):
    for _, statement in enumerate(statements):
        print(statement)
        print_out_text(file_name, statement)
