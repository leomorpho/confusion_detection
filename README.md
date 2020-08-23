# README

Our code can all be accessed through our Jupyter Notebook [here](https://colab.research.google.com/drive/1GB-D6D5eOkK_TgdmVJ8mqMvPmIvMl7aG).

Our annotation, json_aggregator, and preprocessing scripts are present in the repository, and are pulled into our Notebook in the top cell. With regards to our proposal, which set out to construct a model that could reliably predict a customer’s confusion level with high confidence, we would classify our achievement as a “qualified success”. Based on the difficulties we had with the data, and the resulting time limitations we had in building and improving our model, the fact that we were able to produce results above random chance is certainly a success. However, we were unable to produce a model capable of achieving the requirements of the use case we set out to address. Due to the issues mentioned, we were unable to try building models other than the LSTM, improve or increase the complexity of the LSTMs we did build, and were unable to complete a working autoencoder. All required dependencies are included in the Jupyter Notebook.

## Annotation Tool

The annotation tool can be found in the `annotator` directory. Documentation can be found [here](annotator/README.md).

## Preprocessing Tools

The annotation tool can be found in the `jupyter_tools` directory. Documentation can be found [here](jupyter_tools/README.md).

## Aggregator Script

The aggregator script can be found in the root of the repository in the file `json_aggregator.py`.

To run it, simply run the command `python3 json_aggregator.py`.