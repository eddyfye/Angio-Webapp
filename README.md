# Angio Annotation Webapp

This webapp is designed for the annotation of angiograms under the ADDA project.

### Installation and initialization

- Clone the repo to your workstation

```
git clone https://github.com/eddyfye/Angio-Webapp.git
cd Angio-Webapp
```

The python code was designed using Jupyter_dash on Jupyter notebook. It has been verified to work using either Juypter notebook or pycharm.

- Setup a virtual environment with python (3.7 or 3.8) and install the necessary packages

```
pip install jupyter-dash
pip install -r requirement.txt
```

```
conda install -c conda-forge -c plotly jupyter-dash
```

- Connect to the CVPD secure storage and copy the following directory to your workstation

```
/mnt/heart/angio/data_26-8-2020/npz for annotation/
```
Under this directory, there are 3 sub-folders (npz, old-csv and new-csv)
1) ‘npz’ folder contains the preprocessed image files in npz format (frame, channel, width, height)
2) ‘old-csv’ folder contains the predicted annotations from the trained model in csv format
3) ‘new-csv’ folder contains the manually corrected annotations in csv format

- Change the working directory in the webapp's main.py to the view of interest found within the new copied directory

Example for someone working on RAO Caudal annotation
```
/home/tanwp/Documents/data_26-8-2020/npz for annotation/RAO Caudal/
```

### Step-by-step guide to using the webapp

1) Select npz file from the dropdown list
2) Use the sliders to view or adjust the lower and upper boundary images and annotations on the graph
3) When the desired good frames range have been selected using the sliders, click on the annotation button located at the top right-hand corner

Note: When the npz file has multiple good frames flanked by bad frames, just move on to the next file. (do not annotate the npz file)

![Webapp Illustration](Webapp Illustration.png)