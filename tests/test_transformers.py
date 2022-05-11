import pytest
from src.transformers import (
    transform_experiment,
    transform_data,
    transform_file,
    transform_material,
    transform_components,
    transform_process,
    transform_prerequisite_process,
    transform_process_ingredient,
    transform_process_product,
)
from tests.cases.case_transformers import (
    group_obj,
    collection_obj,
    public_flag,
    case_transform_experiment_true,
)


@pytest.mark.parametrize("parsed_experiments, expected", case_transform_experiment_true)
def test_transform_experiment_true(parsed_experiments, expected):
    actual = transform_experiment(
        group_obj, collection_obj, parsed_experiments, public_flag
    )
    assert all([a == b for a, b in zip(actual, expected)])


# @pytest.mark.parametrize("parsed_experiments, expected", case_transform_experiment_false)
# def test_transform_experiment_false(parsed_experiments, expected):
#     actual = transform_experiment(
#         group_obj, collection_obj, parsed_experiments, public_flag
#     )
#     assert all([a == b for a, b in zip(actual, expected)])
