"""
The start of an all new evaluation algorithm. 
The idea of this evaluation is to get results for specific tags
in our nested tagging structure. To facilitate this in an intuitive way,
the gold data is represented as xml trees.

This evaluation script is written for the BeNASch annotation scheme,
but should easily fittable to other systems of nested tagging.
"""

from lxml import etree as et
from typing import Optional, List, Tuple
import json
import eval_metrics, sample as sample_funcs
import pprint as pp


GROUND_TRUTH = "./gt_24_04_30.xml"
PREDICTION_FILE = "./prediction_files/simple.jsonl"


class Annotation(object):
    def __init__(self, ident, text, start, end, labels, confidence, head):
        self.id: str = ident
        self.text: List[str] = text
        self.start: int = start
        self.end: int = end
        self.tags: dict = labels
        self.confidence: float = confidence
        self.head: Annotation = head
        self.boundary_matches = []
        self.head_matches = []

    def __str__(self) -> str:
        return f"{self.text} ({str(self.tags)}, {self.start}, {self.end})"
    
    def __repr__(self) -> str:
        return f"{self.text} ({str(self.tags)}, {self.start}, {self.end})"


def create_annotation(anno, ident, head=False):
    tags = {}
    info = anno["labels"][0]["value"].split(";")
    if head:
        tags = {"head": ""}
    else:
        for i in info:
            key, value = i.split(":")
            tags[key] = value
    if "head" in anno:
        head = create_annotation(anno["head"], ident + "_head", head=True)
    else:
        head = None
    annotation = Annotation(ident, anno["text"], anno["start_pos"], anno["end_pos"], tags, anno["labels"][0]["confidence"], head)
    return annotation


def read_prediction_file(infile):
    corpus = []
    ident_to_anno = {}
    with open(infile, mode="r", encoding="utf8") as inf:
        for i, line in enumerate(inf):
            document = []
            annos = json.loads(line)
            for j, anno in enumerate(annos):
                annotation = create_annotation(anno, f"{i}_{j}")
                ident_to_anno[f"{i}_{j}"] = annotation
                document.append(annotation)
            corpus.append(document)
    return corpus, ident_to_anno


def match_annos(predictions, gt, evaluation_categories):
    """
    For each prediction, look through all gt tags
    and see if they match it. 
    Most important measure is boundary, but we
    will also note matches where boundary fits, but
    type(s) was incorrectly guessed.
    """
    for prediction, gold in zip(predictions, gt.findall("./Document")):
        #print(gold.get("document_text"))
        #print(prediction)
        gold_elems = []
        for _, (_, expr) in evaluation_categories.items():
            #print(expr)
            gold_elems.extend(gold.xpath(expr))
        for pred in prediction:
            #match = gold.xpath(f".//*[@char_start='{pred.start}' and @char_end='{pred.end}']")
            #for m in match:
            for m in gold_elems:
                if not (m.get("char_start") == str(pred.start) and m.get("char_end") == str(pred.end)):
                    continue
                #print(pred)
                #print(et.tostring(m))
                pred.boundary_matches.append(m)
                if "boundary_matches" in m.attrib:
                    m.set("boundary_matches", m.get("boundary_matches") + " " + pred.id)
                else:
                    m.set("boundary_matches", pred.id)
            if pred.head is not None:
                #match = gold.xpath(f".//*[@char_head_start='{pred.head.start}' and @char_head_end='{pred.head.end}']")
                #for m in match:
                for m in gold_elems:
                    if not (m.get("head_char_start") == str(pred.head.start) and m.get("head_char_end") == str(pred.head.end)):
                        continue
                    pred.head_matches.append(m)
                    if "head_matches" in m.attrib:
                        m.set("head_matches", m.get("head_matches") + " " + pred.id)
                    else:
                        m.set("head_matches", pred.id)


def evaluate(predictions, gt, categories, ident_to_anno):
    # filter predictions and ground truths by categories
    relevant_dict = {}
    for cat, (pred_filter, expr) in categories.items():
        relevant_predictions = []
        for prediction in predictions:
            for key, value in pred_filter.items():
                if key not in prediction.tags or prediction.tags[key] != value:
                    break
            else:
                relevant_predictions.append(prediction)
        print(len(relevant_predictions))
        relevant_gold = gt.xpath(expr)
        relevant_dict[cat] = {"predictions": relevant_predictions, "gold": relevant_gold}
    boundary_scores = eval_metrics.get_boundary_scores(relevant_dict)
    head_scores = eval_metrics.get_head_boundary_scores(relevant_dict)
    scores = eval_metrics.get_scores(relevant_dict, lambda x, y: x.get("entity_type").split("_")[0] == y.tags["ent"], ident_to_anno)
    #aggregated_scores = eval_metrics.get_scores_custom(relevant_dict, lambda x, y: x.get("entity_type").split("_")[0] == y.tags["ent"], lambda x: x.tag, ident_to_anno)
    aggregated_scores = eval_metrics.get_scores_custom(relevant_dict, lambda x, y: x.get("entity_type").split("_")[0] == y.tags["ent"], lambda x: (x.tag, x.getparent().tag), ident_to_anno)

    print("="*20, "ONLY BOUNDARIES", "="*20)
    pp.pprint(boundary_scores)
    print("="*20, "ONLY HEAD BOUNDARIES", "="*20)
    pp.pprint(head_scores)
    print("="*20, "CLASSIC", "="*20)
    pp.pprint(scores)
    print("="*20, "AGGREGATED", "="*20)
    pp.pprint(aggregated_scores)


def sample(predictions, gt, categories, ident_to_anno):
    # filter predictions and ground truths by categories
    relevant_dict = {}
    for cat, (pred_filter, expr) in categories.items():
        relevant_predictions = []
        for prediction in predictions:
            for key, value in pred_filter.items():
                if key not in prediction.tags or prediction.tags[key] != value:
                    break
            else:
                relevant_predictions.append(prediction)
        print(len(relevant_predictions))
        relevant_gold = gt.xpath(expr)
        relevant_dict[cat] = {"predictions": relevant_predictions, "gold": relevant_gold}
    print("="*30, "HEAD CORRECT, FULL SPAN WRONG", "="*30)
    sample_funcs.head_correct_but_not_full_span(relevant_dict)
    print("="*30, "FULL SPAN CORRECT, HEAD WRONG", "="*30)
    sample_funcs.full_span_correct_but_not_head(relevant_dict)


if __name__ == "__main__":
    preds, ident_to_anno = read_prediction_file(PREDICTION_FILE)
    preds_flat = [anno for doc in preds for anno in doc]
    gt = et.parse(GROUND_TRUTH)

    print(len(gt.findall("./Document")), len(preds))

    # this must be fitted to the tags the model was trained on
    evaluation_categories = {
        "Persons": ({"ent": "per"}, ".//*[starts-with(@entity_type,'per')]"),
        "Organizations": ({"ent": "org"}, ".//*[starts-with(@entity_type,'org')]"),
        "Locations": ({"ent": "loc"}, ".//*[starts-with(@entity_type,'loc')]"),
        "GPEs": ({"ent": "gpe"}, ".//*[starts-with(@entity_type,'gpe')]"),
        #"values": ({"val": "per"}, ".//*[starts-with(@entity_type,'per')"),
    }

    match_annos(preds, gt, evaluation_categories)

    print(preds[0][3])
    print(preds[0][3].head)
    print(et.tostring(preds[0][3].boundary_matches[0]))
    print(et.tostring(preds[0][3].head_matches[0]))

    evaluate(preds_flat, gt, evaluation_categories, ident_to_anno)
    #sample(preds_flat, gt, evaluation_categories, ident_to_anno)


