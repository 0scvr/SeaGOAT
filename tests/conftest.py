# pylint: disable=redefined-outer-name

import os
import tempfile
import shutil
from datetime import datetime, timedelta, timezone
import pytest
from git import Repo, Actor


class MockRepo(Repo):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fake_commit_date = datetime.now(timezone.utc) - timedelta(days=4)

    def tick_fake_date(self, days=0, hours=0):
        delta = timedelta(days=days, hours=hours)
        self.fake_commit_date += delta

    def add_fake_data(self):
        file_changes = [
            {
                "name": "file1.md",
                "contents": [
                    "# Markdown file\nThis is an example Markdown file.",
                    "# Markdown file\nThis is an example Markdown file. Updated.",
                ],
                "authors": [
                    Actor("John Doe", "jdoe@example.com"),
                    Actor("Alice Smith", "asmith@example.com"),
                ],
                "commit_messages": [
                    "Initial commit for Markdown file",
                    "Update to Markdown file",
                ],
            },
            {
                "name": "file2.py",
                "contents": [
                    "# This is an example Python file",
                    "# This is an updated example Python file",
                ],
                "authors": [
                    Actor("Alice Smith", "asmith@example.com"),
                    Actor("Charlie Brown", "cbrown@example.com"),
                ],
                "commit_messages": [
                    "Initial commit for Python file",
                    "Update to Python file",
                ],
            },
            {
                "name": "file3.py",
                "contents": ["# This is another example Python file"],
                "authors": [Actor("Charlie Brown", "cbrown@example.com")],
                "commit_messages": ["Initial commit for another Python file"],
            },
            {
                "name": "file4.js",
                "contents": [
                    "// This is an example JavaScript file",
                    "// This is an updated example JavaScript file",
                    "// This is a second updated example JavaScript file",
                ],
                "authors": [
                    Actor("John Doe", "jdoe@example.com"),
                    Actor("Alice Smith", "asmith@example.com"),
                    Actor("Charlie Brown", "cbrown@example.com"),
                ],
                "commit_messages": [
                    "Initial commit for JavaScript file",
                    "Update to JavaScript file",
                    "Second update to JavaScript file",
                ],
            },
        ]

        for file_change in file_changes:
            for i in range(len(file_change["contents"])):
                self.add_file_change_commit(
                    file_change["name"],
                    file_change["contents"][i],
                    file_change["authors"][i],
                    file_change["commit_messages"][i],
                )
                self.tick_fake_date(days=1)

    def add_file_change_commit(self, file_name, contents, author, commit_message):
        with open(
            os.path.join(self.working_dir, file_name), "w", encoding="utf-8"
        ) as output_file:
            output_file.write(contents)

        self.index.add([file_name])
        self.index.commit(
            commit_message,
            author=author,
            committer=author,
            author_date=self.fake_commit_date,
            commit_date=self.fake_commit_date,
            skip_hooks=True,
        )


@pytest.fixture
def repo():
    new_directory = tempfile.mkdtemp()
    repo = MockRepo.init(new_directory)
    repo.add_fake_data()
    yield repo
    shutil.rmtree(new_directory)
