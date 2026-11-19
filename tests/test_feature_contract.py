import pytest

from loaders import ELLIPTIC
from loaders.contract import ContractError, check_feature_groups


def test_local_group_is_93_features_without_time_step():
    local = ELLIPTIC.feature_groups["local"]
    assert len(local) == 93
    assert "time_step" not in local


def test_aggregate_group_is_72_features():
    assert len(ELLIPTIC.feature_groups["aggregate"]) == 72


def test_local_plus_time_step_matches_prd_count():
    assert len(ELLIPTIC.feature_groups["local"]) + 1 == ELLIPTIC.expected.feature_groups["local_including_time_step"]


def test_groups_are_disjoint():
    check_feature_groups(ELLIPTIC.feature_groups)


def test_time_step_in_a_group_is_rejected():
    with pytest.raises(ContractError):
        check_feature_groups({"local": ("local_01", "time_step")})


def test_overlapping_groups_are_rejected():
    with pytest.raises(ContractError):
        check_feature_groups({"local": ("a", "b"), "aggregate": ("b", "c")})
