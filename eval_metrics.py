from collections import Counter, defaultdict


def get_scores(data, compare_function, ident_to_anno):
    # 3. Precision / Recall / F1-Score, only boundary matching (tag-switching)
    boundary_matching = {}
    #all_results["boundary_matching"] = boundary_matching
    for type, d in data.items():
        predictions = d["predictions"]
        ground_truth = d["gold"]
        boundary_matching[type] = {}
        t_p = 0.
        f_p = 0.
        f_n = 0.
        for gt in ground_truth:
            if gt.get("boundary_matches") is not None and any([compare_function(gt, ident_to_anno[m]) for m in gt.get("boundary_matches").split(" ")]):
                t_p += 1.
            else:
                f_n += 1.
        for pred in predictions:
            if not pred.boundary_matches or not all([compare_function(gt, pred) for gt in pred.boundary_matches]):
                f_p += 1.
        print(t_p, f_n, f_p)
        precision = t_p / (t_p + f_p) if (t_p + f_p) > 0. else 0.
        recall = t_p / (t_p + f_n) if (t_p + f_p) > 0. else 0.
        f1 = 2 / ((1. / precision) + (1. / recall)) if precision > 0. and recall > 0. else 0.
        boundary_matching[type]["precision"] = precision
        boundary_matching[type]["recall"] = recall
        boundary_matching[type]["f1"] = f1
    # calculate weighted average (not sure if this is exactly correct, we simply weight by their counts)
    boundary_matching["weighted_avg"] = {
        "precision": 0,
        "recall": 0,
        "f1": 0
    }
    counts = {}
    for type, d in data.items():
        counts[type] = len(d["gold"])
    total_counts = sum(counts.values())
    for type, count in counts.items():
        counts[type] = count / total_counts
        boundary_matching[type]["weight"] = counts[type]
    for type in data:
        boundary_matching["weighted_avg"]["precision"] += boundary_matching[type]["precision"] * counts[type]
        boundary_matching["weighted_avg"]["recall"] += boundary_matching[type]["recall"] * counts[type]
        boundary_matching["weighted_avg"]["f1"] += boundary_matching[type]["f1"] * counts[type]
    return boundary_matching


def get_scores_custom(data, compare_function, aggregation_function, ident_to_anno):
        # 3. Precision / Recall / F1-Score, only boundary matching (tag-switching)
    boundary_matching = {}
    #all_results["boundary_matching"] = boundary_matching
    for type, d in data.items():
        aggregation_scores = defaultdict(Counter)
        predictions = d["predictions"]
        ground_truth = d["gold"]
        for gt in ground_truth:
            if gt.get("boundary_matches") is not None and any([compare_function(gt, ident_to_anno[m]) for m in gt.get("boundary_matches").split(" ")]):
                aggregation_scores[aggregation_function(gt)]["t_p"] += 1
            else:
                aggregation_scores[aggregation_function(gt)]["f_n"] += 1
        boundary_matching[type] = {}
        for key, counter in aggregation_scores.items():
            t_p = counter["t_p"]
            f_n = counter["f_n"]
            recall = t_p / (t_p + f_n) if t_p > 0. else 0.
            boundary_matching[type][key] = recall
    return boundary_matching


def get_boundary_scores(data):
    # 3. Precision / Recall / F1-Score, only boundary matching (tag-switching)
    boundary_matching = {}
    #all_results["boundary_matching"] = boundary_matching
    for type, d in data.items():
        predictions = d["predictions"]
        ground_truth = d["gold"]
        boundary_matching[type] = {}
        t_p = 0.
        f_p = 0.
        f_n = 0.
        for gt in ground_truth:
            if gt.get("boundary_matches") is not None and gt.get("boundary_matches"):
                t_p += 1.
            else:
                f_n += 1.
        for pred in predictions:
            if not pred.boundary_matches:
                f_p += 1.
        print(t_p, f_n, f_p)
        precision = t_p / (t_p + f_p) if (t_p + f_p) > 0. else 0.
        recall = t_p / (t_p + f_n) if (t_p + f_p) > 0. else 0.
        f1 = 2 / ((1. / precision) + (1. / recall)) if precision > 0. and recall > 0. else 0.
        boundary_matching[type]["precision"] = precision
        boundary_matching[type]["recall"] = recall
        boundary_matching[type]["f1"] = f1
    # calculate weighted average (not sure if this is exactly correct, we simply weight by their counts)
    boundary_matching["weighted_avg"] = {
        "precision": 0,
        "recall": 0,
        "f1": 0
    }
    counts = {}
    for type, d in data.items():
        counts[type] = len(d["gold"])
    total_counts = sum(counts.values())
    for type, count in counts.items():
        counts[type] = count / total_counts
        boundary_matching[type]["weight"] = counts[type]
    for type in data:
        boundary_matching["weighted_avg"]["precision"] += boundary_matching[type]["precision"] * counts[type]
        boundary_matching["weighted_avg"]["recall"] += boundary_matching[type]["recall"] * counts[type]
        boundary_matching["weighted_avg"]["f1"] += boundary_matching[type]["f1"] * counts[type]
    return boundary_matching


def get_head_boundary_scores(data):
    # 3. Precision / Recall / F1-Score, only boundary matching (tag-switching)
    boundary_matching = {}
    #all_results["boundary_matching"] = boundary_matching
    for type, d in data.items():
        predictions = d["predictions"]
        ground_truth = d["gold"]
        boundary_matching[type] = {}
        t_p = 0.
        f_p = 0.
        f_n = 0.
        for gt in ground_truth:
            if gt.get("head_matches") is not None and gt.get("head_matches"):
                t_p += 1.
            else:
                f_n += 1.
        for pred in predictions:
            if not pred.head_matches:
                f_p += 1.
        print(t_p, f_n, f_p)
        precision = t_p / (t_p + f_p) if (t_p + f_p) > 0. else 0.
        recall = t_p / (t_p + f_n) if (t_p + f_p) > 0. else 0.
        f1 = 2 / ((1. / precision) + (1. / recall)) if precision > 0. and recall > 0. else 0.
        boundary_matching[type]["precision"] = precision
        boundary_matching[type]["recall"] = recall
        boundary_matching[type]["f1"] = f1
    # calculate weighted average (not sure if this is exactly correct, we simply weight by their counts)
    boundary_matching["weighted_avg"] = {
        "precision": 0,
        "recall": 0,
        "f1": 0
    }
    counts = {}
    for type, d in data.items():
        counts[type] = len(d["gold"])
    total_counts = sum(counts.values())
    for type, count in counts.items():
        counts[type] = count / total_counts
        boundary_matching[type]["weight"] = counts[type]
    for type in data:
        boundary_matching["weighted_avg"]["precision"] += boundary_matching[type]["precision"] * counts[type]
        boundary_matching["weighted_avg"]["recall"] += boundary_matching[type]["recall"] * counts[type]
        boundary_matching["weighted_avg"]["f1"] += boundary_matching[type]["f1"] * counts[type]
    return boundary_matching


def score_by_length(gold_tags, pred_tags, all_results, tag_types):
    # 4. Tag length performances
    # this is in effect the calculation of classic scores with a filter to only regard
    # very specific tags for the purpose of that calculation

    tag_length_eval = {}
    all_results["tag_length_eval"] = tag_length_eval

    for type in tag_types:
        tag_length_eval[type] = {}

        all_tag_lengths = [tag[2] - tag[1] for tag in gold_tags if tag[0] == type]
        all_tag_lengths_sum = sum(all_tag_lengths)
        all_tag_lengths_len = len(all_tag_lengths)
        average = all_tag_lengths_sum / all_tag_lengths_len
        #values = [average * 0.25, average * 0.5, average * 0.75, average, (max(all_tag_lengths) - average) * 0.25 + average, (max(all_tag_lengths) - average) * 0.5 + average, (max(all_tag_lengths) - average) * 0.75 + average, max(all_tag_lengths)]
        values = [10, 20, 40, 80, 160, 320]
        #values = range(max(all_tag_lengths))
        for i, value in enumerate(values):
            tag_length_eval[type][value] = {}

            if i == 0:
                min_value = 0
            else:
                min_value = values[i-1]

            valid_gold = [g for g in gold_tags if g[0] == type and g[2] - g[1] > min_value and g[2] - g[1] <= value]
            valid_pred = [g for g in pred_tags if g[0] == type and g[2] - g[1] > min_value and g[2] - g[1] <= value]
            tag_length_eval[type][value]["count"] = len(valid_gold)

            t_p = 0.
            f_p = 0.
            f_n = 0.
            for tag in valid_gold:
                if tag in valid_pred:
                    t_p += 1.
                else:
                    f_n += 1.
            for tag in valid_pred:
                if tag not in valid_gold:
                    f_p += 1.
            precision = t_p / (t_p + f_p) if (t_p + f_p) > 0. else 0.
            recall = t_p / (t_p + f_n) if (t_p + f_n) > 0. else 0.
            f1 = 2 / ((1. / precision) + (1. / recall)) if precision > 0. and recall > 0. else 0.
            tag_length_eval[type][value]["precision"] = precision
            tag_length_eval[type][value]["recall"] = recall
            tag_length_eval[type][value]["f1"] = f1

def score_by_depth(gold_tags, pred_tags, all_results, tag_types, depth_list):
    """
    Filter the gold tags by their depth. 
    Currently only recall is correctly calculated!
    """
    tag_length_eval = {}
    all_results["tag_depth_eval"] = tag_length_eval

    for type in tag_types:
        tag_length_eval[type] = {}

        for i, value in enumerate(range(max(depth_list)+1)):
            tag_length_eval[type][value] = {}

            valid_gold = [g for g, d in zip(gold_tags, depth_list) if g[0] == type and d == value]
            valid_pred = [g for g in pred_tags if g[0] == type]
            tag_length_eval[type][value]["count"] = len(valid_gold)

            t_p = 0.
            f_p = 0.
            f_n = 0.
            for tag in valid_gold:
                if tag in valid_pred:
                    t_p += 1.
                else:
                    f_n += 1.
            for tag in valid_pred:
                if tag not in valid_gold:
                    f_p += 1.
            precision = t_p / (t_p + f_p) if (t_p + f_p) > 0. else 0.
            recall = t_p / (t_p + f_n) if (t_p + f_n) > 0. else 0.
            f1 = 2 / ((1. / precision) + (1. / recall)) if precision > 0. and recall > 0. else 0.
            #tag_length_eval[type][value]["precision"] = precision
            tag_length_eval[type][value]["recall"] = recall
            #tag_length_eval[type][value]["f1"] = f1