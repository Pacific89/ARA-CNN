import pandas as pd
from matplotlib import pyplot as plt
import PIL
from PIL import ImageDraw
import numpy as np
from sklearn import preprocessing


csv = pd.read_csv("output/results/results.csv")
# print(result_csv)

# result_csv.hist(column="06_MUCOSA", bins=50)
# result_csv.hist(column="07_ADIPOSE", bins=50)
# result_csv.hist(column="04_LYMPHO", bins=50)
# result_csv.hist(column="03_COMPLEX", bins=50)
# result_csv.hist(column="02_STROMA", bins=50)
# result_csv.hist(column="01_TUMOR", bins=50)
# result_csv.hist(column="uncertainty", bins=50)
# plt.show()

result_csv = csv.iloc[2145:]

width = np.max(result_csv["patch_x"]) - np.min(result_csv["patch_x"])
width_ = width+width*0.3

height = np.max(result_csv["patch_y"]) - np.min(result_csv["patch_y"])
height_ = height+height*0.3

img = PIL.Image.new("RGB",(int(width_) , int(height_)), (255, 255, 255))
Drawer = ImageDraw.Draw(img)

colors = ["green", "red", "blue", "purple", "yellow", "white", "black", "pink"]

# min_max_scaler = preprocessing.MinMaxScaler()
# scaled = (result_csv["uncertainty"]-result_csv["uncertainty"].min())/(result_csv["uncertainty"].max()-result_csv["uncertainty"].min())
for patch in range(len(result_csv)):
    # print(result_csv.iloc[patch])
    x = result_csv.iloc[patch]["patch_x"] - np.min(result_csv["patch_x"])
    y = result_csv.iloc[patch]["patch_y"] - np.min(result_csv["patch_y"])

    Drawer.rectangle([x,y,x+150,y+150], fill=colors[np.argmax(result_csv.iloc[patch].values[2:10])])
    print(patch)

plt.imshow(img)
plt.plot(0,0, colors[6], label="01_TUMOR")
plt.plot(0,0, colors[1], label="02_STROMA")
plt.plot(0,0, colors[2], label="03_COMPLEX")
plt.plot(0,0, colors[3], label="04_LYMPHO")
plt.plot(0,0, colors[4], label="05_DEBRIS")
plt.plot(0,0, colors[0], label="06_MUCOSA")
plt.plot(0,0, colors[7], label="07_ADIPOSE")
plt.plot(0,0, colors[5], label="08_EMPTY")
plt.legend()

plt.show()

