python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

# Install ipyevents for interactive labeling widgets
jupyter labextension install @jupyter-widgets/jupyterlab-manager ipyevents

# Enable extensions
jupyter nbextension enable --py widgetsnbextension      # ipywidgets
jupyter nbextension enable --py --sys-prefix ipyevents  # ipyevents

jupyter lab
