### Automatic Generation of Live Blog Posts during <i>Formula One</i> races
In this repository, you will find the scripts that I used for creating a live blog generation system for my Master thesis. Below, an overview of the contents of each of the folders is provided.

<h3>Data extraction</h3>
This folder is split up in <i>race data</i> and <i>blog data</i>.

<h4>Blog data</h4>
The Jupyter notebook contains the code used to scrape all blogs after 2018 from <i>Autosport.com</i>. The scraped items can be found in the data set folder.

<h4>Race data</h4>
In the race data folder, the <i>Node.js</i> file used to scrape data from <i>TFeed</i> can be found. Furthermore, the Jupyter notebooks to extract data from the other sources are present here, as well as the folders containing the extracted data itself.

<h3>Event identification</h3>
Using the Jupyter notebook and Python file present in this folder, the events were filtered from the initial input data. The resulting filtered data is stored in the events folder.

<h3>Experimentation</h3>
Of most experiments, the code used is integrated in the implementation. In this folder, only a notebook that was used to test the use of LLMs for data extraction can be found.

<h3>FineTuning</h3>
The <i>PEFT</i> script contains the code used for fine-tuning the model. The various fine-tuned models (with different settings) can be found in the fine-tuned models folder.

<h3>Implementation</h3>
In the implementation folder, the functions for generating the posts, as well as the generated posts themselves, are present.

<h3>Linguistic Feature Extraction</h3>
Here, the code used for establishing the fine-tuning data set can be found. It contains various Python files and has separate folders for the NER scripts and the LFE output.
