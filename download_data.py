import urllib.request
import os

os.makedirs('data', exist_ok=True)

print("Downloading training file...")
urllib.request.urlretrieve(
    "https://raw.githubusercontent.com/defcom17/NSL_KDD/master/KDDTrain+.txt",
    "data/kddtrain.csv"
)
print("Done! File saved as data/kddtrain.csv")