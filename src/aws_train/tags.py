"""The Project Tag every demo resource carries, so the Teardown can find it."""

from collections.abc import Iterable

Tag = dict[str, str]

PROJECT_TAG_KEY = "project"
PROJECT_TAG_VALUE = "aws-train"
PROJECT_TAG: Tag = {"Key": PROJECT_TAG_KEY, "Value": PROJECT_TAG_VALUE}


def with_project_tag(extra: Iterable[Tag] = ()) -> list[Tag]:
    """Return a new tag list that starts with the Project Tag.

    Any tag in ``extra`` using the project key is dropped, so the Project Tag can
    neither be duplicated nor overridden.
    """
    return [dict(PROJECT_TAG), *(dict(tag) for tag in extra if tag["Key"] != PROJECT_TAG_KEY)]
