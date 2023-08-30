# contributing to `firefox_bookmarks`

## code of conduct

Please read and follow our [Code of Conduct](https://github.com/BURG3R5/firefox-bookmarks/blob/develop/.github/CODE_OF_CONDUCT.md) to keep our community approachable and respectable.

## setting up your development environment

1. Get `poetry`:

   1. `^1.5.1`
   2. [instructions](https://python-poetry.org/docs/)

2. Fork this repo and clone it:

   1. [fork](https://github.com/BURG3R5/firefox-bookmarks/fork)
   2. `git clone git@github.com:YOUR_USERNAME/firefox-bookmarks.git`
   3. `cd firefox-bookmarks`

3. Get dependencies:

   1. `poetry install`
   2. `poetry shell`

4. Set up and run the pre-commit hook:

   1. `pre-commit install`
   2. `pre-commit run --all`

5. Run the tests:
   1. `pytest`

## new features

You can _request_ a new feature by [submitting an issue](https://github.com/BURG3R5/firefox-bookmarks/issues/new) to our GitHub Repository. If you would like to _implement_ a new feature, please submit an issue with a proposal for your work first, to be sure that we can use it. Please consider what kind of change it is:

- For a **major feature**, first open an issue and outline your proposal so that it can be discussed. This will also allow us to better coordinate our efforts, prevent duplication of work, and help you to craft the change so that it is successfully accepted into the project.
- **Small features** can be crafted and directly [submitted as a Pull Request](https://github.com/BURG3R5/firefox-bookmarks/compare).

## commit messages

We follow the [Angular commit message guidelines](https://github.com/angular/angular/blob/22b96b96902e1a42ee8c5e807720424abad3082a/CONTRIBUTING.md#-commit-message-guidelines)

## formatting

We use [YAPF](https://github.com/google/yapf) and [isort](https://pycqa.github.io/isort/) for formatting our code. Please run the pre-commit hooks before submitting your PR for review.
