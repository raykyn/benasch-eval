from lxml import etree as et

def head_correct_but_not_full_span(data):
    for type, d in data.items():
        print("="*20, type.upper(), "="*20)
        predictions = d["predictions"]
        #ground_truth = d["gold"]
        for pred in predictions:
            if pred.head_matches:
                for gt in pred.head_matches:
                    if gt not in pred.boundary_matches:
                        print(pred)
                        print(pred.head)
                        print(gt.get("head_text"))
                        print(gt.xpath(".//ancestor::Document")[0].get("document_text")[int(gt.get("char_start")):int(gt.get("char_end"))])
                        #print(et.tostring(gt))


def full_span_correct_but_not_head(data):
    for type, d in data.items():
        print("="*20, type.upper(), "="*20)
        predictions = d["predictions"]
        #ground_truth = d["gold"]
        for pred in predictions:
            if pred.boundary_matches:
                for gt in pred.boundary_matches:
                    if gt not in pred.head_matches:
                        print(pred)
                        print(pred.head)
                        print(gt.get("head_text"))
                        print(gt.xpath(".//ancestor::Document")[0].get("document_text")[int(gt.get("char_start")):int(gt.get("char_end"))])
                        #print(et.tostring(gt))