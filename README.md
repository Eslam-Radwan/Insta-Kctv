# Knowledge-Centric Templatic Views of Documents
This repo provides the prompts, code & references to data from our paper: "Knowledge-Centric Templatic Views of Documents" (EMNLP 2024).

## Overview
**Knowledge-Centric Templatic Views of Documents (KCTV)** is a process to transform documents from one form (or view) to another using Large Language Models (LLMs) in a unified way. For instance, it can take an academic paper as a source input document and generate an output that is a set of slides or a poster. The system uses an intermediate structured knowledge-centric representation that encapsulates the source document, which can then be used to generate multiple types of target documents. Other than a brief description of the style and properties of the target document, no other input or prompt engineering is required.

The primary intended use for this package is academic research; it allows other researchers in the field to replicate, evaluate or build on the original work in our paper, using the code and prompts we are releasing.

## Requirements
1. Install package by running `$ python setup.py clean install` or `$ pip install -e .` for developer mode.

2. Install PDFFigures by following the installation instructions [here](https://github.com/allenai/pdffigures2)

3. Create an [Azure Form Recognizer Endpoint](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/overview?view=doc-intel-3.1.0). Export the endpoint and key as an environment variable:

```
$ export FORMRECOGNIZER_ENDPOINT="ENDPOINT"
$ export FORMRECOGNIZER_KEY="KEY"
```

4. If using the Open AI API, export the key and org as environment variables:

```
$ export OPENAI_KEY="KEY"
$ export OPENAI_ORG="ORG"
```

5. If using the Azure Open AI API, export the endpoint, key, and api verison:
```
$ export AZURE_OPENAI_ENDPOINT="ENDPOINT"
$ export AZURE_OPENAI_KEY="KEY"
$ export OPENAI_API_VERSION="2022-12-01"
```

## How to run generations
```
$ python kctv/main.py {/path/to/input-doc} {output-doc-name} \
--model-name {gpt35 | gpt35-16k | gpt4 | gpt4-32k} \
--service-name {azure | openai} \
--max-req-per-min {default=100} \
--temperature {default=0.0} \ 
--which-template {poster | blog | socialmedia | slides | all | none} 
--skip-internal-rep # Optional flag to skip SURe
```

## How to run evaluation
To run the evaluation as a script, run
```
$ python kctv/eval.py {bert-score|rouge-1,rouge-L} {/path/to/reference/doc} {/path/to/predicted/doc/} 
```

Reference doc: a csv file with each row being one frame for the reference doc. If there are multiple columns, the script takes the max over the columns. 

Predicted doc: a generated latex file

You can also run the evaluation as a library:
```{python}
from kctv import eval

scores = eval.score(
    [/path/to/ref0, /path/to/ref1, ...]
    [/path/to/pred0, /path/to/pred, ...],
    {bert-score|rouge-1,rouge-L}
)
```

## Data
To reproduce our results, you'll need access to the following datasets:
1. [Longsumm](https://aclanthology.org/2020.sdp-1.24v2.pdf)
2. [iPoster](https://www.jstage.jst.go.jp/article/tjsai/30/1/30_30_112/_pdf)
3. [Doc2PPT](https://tsujuifu.github.io/pubs/aaai22_doc2ppt.pdf)

List of the subset of data we used for evaluation can be found in `data_splits/`

## Evaluation
KCTV was evaluated using a unified novel approach that we proposed, on three types of documents: slides, posters, and blog posts using the public DOC2PPT, Paper-Poster, and LongSumm datasets respectively. In each case, the inputs were scientific articles and the outputs were documents of the corresponding types. The evaluation showed that our method of generating a Structured Unified Representation led to improvements in performance across each task. We also conducted a human evaluation to validate both our document generation method and evaluation framework, and found that humans preferred the output yielded by our method 82% of the time. Moreover, our evaluation metric correlated more highly with human preference than other popular metrics, such as ROUGE and BERTScore. More details of evaluation, metrics and findings can be found in our paper: "Knowledge-Centric Templatic Views of Documents" (EMNLP 2024).

## Tips
Temperature is an LLM setting that controls the outputs of KCTV. In most of our experiments we have set the temperature to 0, but some controlled diversity with higher temperature settings may be appropriate for other applications, along with other risk mitigating factors like prompt guardrails and data post-processing and validation – for ensuring output quality.

## Risks and Limitations
KCTV has been tested primarily in the domain of academic papers and associated outputs (slides, blog posts, posters), and its performance in other domains (such as transforming a resume into a cover letter) has not been extensively tested. Additionally, the system uses LaTeX as the output format for documents, and its performance with other structured or unstructured outputs has not been extensively evaluated. Also, the system has been developed and tested for the textual content of documents and as such is not designed to work with other media (such as images, tables etc.) in documents. Moreover, this approach leverages generative LLMs in order to both build the intermediate representation and generate the output documents and is thus bound by the same concerns around hallucination and trustworthiness of all LLM applications.

Users should be aware of these limitations and adjust their expectations and usage of the system accordingly. Specifically, they should carefully check accuracy and coverage of output documents, making necessary changes manually as appropriate, before using this system in any real-world setting.

## Citing this work
If you use this package in your work, please cite the following:

```bib
@InProceedings{cachola2024_kctv,
  author =  {Cachola, Isabel Alyssa and Cucerzan, Silviu and Herring, Allen and Mijovic, Vuksan and Oveson, Erik and Jauhar, Sujay Kumar},
  title =   {Knowledge-Centric Templatic Views of Documents},
  year =    {2024},  
  booktitle = {Findings of the 2024 Conference on Empirical Methods in Natural Language Processing (EMNLP)},
  url = {https://arxiv.org/pdf/2401.06945}
}
```

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft 
trademarks or logos is subject to and must follow 
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
