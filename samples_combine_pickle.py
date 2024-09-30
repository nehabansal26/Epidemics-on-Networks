import pickle
import glob
import argparse
import os

parser = argparse.ArgumentParser(description="Process some integers.")
parser.add_argument('file_start', type=str, help='file start')
parser.add_argument('file_end', type=str, help='file end')
args = parser.parse_args()

file_paths = glob.glob(f"/home/neha/{args.file_start}_*_{args.file_end}.pkl")

file_paths = [(filepath.split("/")[-1].split("_")[2],filepath) for filepath in file_paths]

# Sort the list based on the extracted numerical ranges
sorted_file_paths = [ls[1] for ls in sorted(file_paths)]

# # Print the sorted list
# for path in sorted_file_paths:
#     print(path)

combined_dict = {'RW':[],'MHRW':[]}
for filepath in sorted_file_paths:
    print(filepath)
    # Load the first pickle file
    with open(filepath, 'rb') as f:
        data1 = pickle.load(f)
        for key in data1.keys():
            combined_dict[key].extend(data1[key])
        os.remove(filepath)
        

# Save the combined data into a new pickle file
with open(f'/home/neha/{args.file_start}_{args.file_end}.pkl', 'wb') as f:
    pickle.dump(combined_dict, f)

