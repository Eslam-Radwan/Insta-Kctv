from pprint import pprint
import logging
logger = logging.getLogger(__name__)


internal_representation =  '''{
                        "Document Title": "TITLE",
                        "Document Authors": ["AUTHOR 1", "AUTHOR 2", ... "AUTHOR N"],
                        "SECTION TITLE 1": {
                        "Figures": [
                            {"Name": "Figure/Table K", "Caption": "CAPTION OF FIGURE/TABLE K"}
                        ],
                        "Content": [
                            "SENTENCE 1",
                            "SENTENCE 2",
                            ...
                            "SENTENCE N"
                        ]
                        },
                        "SECTION TITLE 2": {
                        "Figures": [
                            {"Name": "Figure/Table K", "Caption": "CAPTION OF FIGURE/TABLE K"}
                        ],
                        "Content": [
                            "SENTENCE 1",
                            "SENTENCE 2",
                            ...
                            "SENTENCE N"
                        ]
                        },...   
                         "SECTION TITLE N": {
                        "Figures": [
                            {"Name": "Figure/Table K", "Caption": "CAPTION OF FIGURE/TABLE K"}
                        ],
                        "Content": [
                            "SENTENCE 1",
                            "SENTENCE 2",
                            ...
                            "SENTENCE N"
                        ]
                        }
                        }'''

internal_representation_no_figures =  '''{
                        "Document Title": "TITLE",
                        "Document Authors": ["AUTHOR 1", "AUTHOR 2", ... "AUTHOR N"],
                        "SECTION TITLE 1": {
                        "Content": [
                            "SENTENCE 1",
                            "SENTENCE 2",
                            ...
                            "SENTENCE N"
                        ]
                        },
                        "SECTION TITLE 2": {
                        "Content": [
                            "SENTENCE 1",
                            "SENTENCE 2",
                            ...
                            "SENTENCE N"
                        ]
                        },...   
                         "SECTION TITLE N": {
                        "Content": [
                            "SENTENCE 1",
                            "SENTENCE 2",
                            ...
                            "SENTENCE N"
                        ]
                        }
                        }'''



headers_only =  '''[ SECTION TITLE 1, SECTION TITLE 2, .... SECTION TITLE N]'''

