from aws_train.tags import PROJECT_TAG, with_project_tag


def test_project_tag_value() -> None:
    assert PROJECT_TAG == {"Key": "project", "Value": "aws-train"}


def test_with_project_tag_alone() -> None:
    assert with_project_tag() == [PROJECT_TAG]


def test_with_project_tag_keeps_extra_tags() -> None:
    extra = [{"Key": "step", "Value": "03"}]

    assert with_project_tag(extra) == [PROJECT_TAG, {"Key": "step", "Value": "03"}]


def test_with_project_tag_does_not_duplicate_it() -> None:
    tags = with_project_tag([PROJECT_TAG])

    assert tags.count(PROJECT_TAG) == 1
    assert len(tags) == 1


def test_with_project_tag_cannot_be_overridden() -> None:
    tags = with_project_tag([{"Key": "project", "Value": "other"}])

    assert tags == [PROJECT_TAG]


def test_with_project_tag_returns_a_fresh_list() -> None:
    first = with_project_tag()
    first.append({"Key": "x", "Value": "y"})

    assert with_project_tag() == [PROJECT_TAG]
