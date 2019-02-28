# Opinion Mining for Product Reviews

## Description

An opinion mining pipeline to perform automatic classification of product reviews at aspect level for Brazilian Portuguese.

This is part of a research project developed at ICMC-USP.

## Content
- `/src` contains the source code for the classes and functions used.
- `/references` contains the [system pipeline](https://github.com/guimaraescca/opinion-mining-for-product-reviews/blob/master/references/diagrams/system-flowchart.png) and [class diagrams](https://github.com/guimaraescca/opinion-mining-for-product-reviews/blob/master/references/diagrams/class-diagram.png) for the project
- `/data` stores the data from different sources and stages of the processing pipeline.
  - `/raw` stores the raw corpus dataset.
  - `/processed` stores the corpus data processed after the normalization by the [UGCNormal](https://github.com/avanco/UGCNormal/).
  - `/interim` stores temporary files (models, etc).
  - `/external` stores data acquired from external sources.
    - `/liwc` contains the [LIWC dictionary](http://www.nilc.icmc.usp.br/nilc/index.php/tools-and-resources) for the Brazilian Portuguese language developed by researchers at [NILC/ICMC](http://www.nilc.icmc.usp.br/).
    - `/ontologies` contains resources made available by [@francielleavargas](https://github.com/francielleavargas) with [aspect hierarchies for different product domains](https://github.com/francielleavargas/Aspect-based-Opinion-Mining).

## Installation

### Install using yaourt (Arch Linux / Manjaro)

There is a script available to install all dependencies needed using the **yaourt** package manager. To use the script run:

`sh install-dependencies.sh`

#### Install the UGCNormal and its dependencies

This project uses a fork from [UGCNormal](https://github.com/avanco/UGCNormal/), a normalizer tool developed for the Brazilian Portuguese language. More information about it and the corresponding published paper can be found [here](https://github.com/avanco/UGCNormal/).

Inside the main project folder, clone the available fork repository by running:

`git clone https://github.com/guimaraescca/UGCNormal.git`

The language normalizer used, UGCNormal, has its own dependencies, to install them using **yaourt** run:

`sh install-ugcnormal-dependencies.sh `

### Install using pip [Deprecated]

To install the dependencies using **pip** from the `requirements.txt`, run:

`pip install requirements.txt`
