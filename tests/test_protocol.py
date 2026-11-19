import numpy as np

import evaluate_arms
from features import STAGE_ONE_BLOCKS, Frame, stage_one_scores
from tuning import TRIALS, sample_configs


def synthetic_frame() -> Frame:
    steps = np.repeat(np.arange(1, 50), 4)
    labels = np.tile([1, 0, -1, 0], 49)
    n = len(steps)
    return Frame(np.arange(n), steps, labels, np.zeros((n, 3)), np.zeros((n, 2)))


def test_stage_one_never_scores_a_block_with_a_model_that_saw_it():
    frame = synthetic_frame()
    calls = []

    def fit_predict(train, score):
        calls.append((train.copy(), score.copy()))
        return np.zeros(score.sum())

    stage_one_scores(frame, fit_predict)
    assert len(calls) == len(STAGE_ONE_BLOCKS) + 1
    for train, score in calls:
        assert not (train & score).any()
        assert set(frame.steps[train]).isdisjoint(set(frame.steps[score]))
        assert frame.steps[train].max() <= 29
        assert (frame.labels[train] != -1).all()


def test_evaluation_steps_are_scored_by_a_model_trained_on_all_training_steps():
    frame = synthetic_frame()
    calls = []
    stage_one_scores(frame, lambda train, score: calls.append((train, score)) or np.zeros(score.sum()))
    train, score = calls[-1]
    assert set(frame.steps[score]) == set(range(30, 50))
    assert set(frame.steps[train]) == set(range(1, 30))


def test_search_space_is_reproducible_and_shared_across_arms():
    assert sample_configs(3) == sample_configs(3)
    assert sample_configs(3) != sample_configs(4)
    configs = sample_configs(0)
    assert len(configs) == TRIALS
    for c in configs:
        assert 0.01 <= c["learning_rate"] <= 0.3
        assert 50 <= c["max_iter"] <= 500
        assert 15 <= c["max_leaf_nodes"] <= 127
        assert 10 <= c["min_samples_leaf"] <= 200
        assert 1e-4 <= c["l2_regularization"] <= 10
        assert 0.5 <= c["max_features"] <= 1.0
        assert c["class_weight"] in (None, "balanced")


def test_precision_at_k_and_its_ceiling():
    scores = np.array([0.9, 0.8, 0.7, 0.6, 0.5, 0.4])
    positives = np.array([True, False, True, False, False, False])
    assert evaluate_arms.tp_at(scores, positives, 3) == 2
    index = {35: np.arange(6)}
    m = evaluate_arms.period_metrics(scores, positives, index, 3)
    assert m["precision_at_k_pooled"] == 2 / 3
    assert m["precision_at_k_ceiling"] == 2 / 3


def test_ties_break_by_node_order_not_at_random():
    scores = np.array([0.5, 0.5, 0.5])
    positives = np.array([False, True, True])
    assert evaluate_arms.tp_at(scores, positives, 1) == 0
