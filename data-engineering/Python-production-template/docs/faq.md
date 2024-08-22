???+ Question
    # Explain these GitHub workflows yaml files?
    - `dev.yml`: define dev workflow, run on every push and pull requests to master,
    basically run all the tests against multiple versions and platforms.
    - `preview.yml`: define stage & preview workflow, run on every push to master, publish dev build to TestPyPI.
    - `release.yml`: define release & publish workflow, run on every tag push, create GitHub release,
    publish docs to GitHub Pages and built package to PyPI.


???+ Question
    # Why not travis CI?
    Travis CI is a great service, however, github actions is super convenient, less configuration
    , better integration. Less configuration, less error prone.

???+ Question
    # Why not read the docs?
    Same reason as above. GitHub Pages is convenient than read the docs, it requires no
    further configuration, except access token. As to read the docs, you need to
    write v2 config file, plus several settings on web pages.

???+ Question
    # Why mkdocs over sphinx?
    Though powerful, reStructured Text and Sphinx is way toi tedious. With extension,
    you'll find almost all features are available in mkdocs, in a neat and productive
    way. Poetry and Markdown, are the two key factors driven me develop this template.

???+ Question
    # What are the configuration items?

    Here is a list:

    ```
    ## Templated Values

    The following appear in various parts of your generated project.

    project_name
    The name of your new Python package project. This is used in
    documentation, so spaces and any characters are fine here.

    project_slug
    The name of your Python package for PyPI, also as the repository name of GitHub.
    Typically, it is the slugified version of project_name.

    pkg_name
    The namespace of your Python package. This should be Python import-friendly.

    conda_base_dir
    This shows the install directory of your conda package. Used to build your conda environment post install

    conda_env_name
    Set this value to determin your conda env name, defaults to variation on your package name

    project_short_description
    A 1-sentence description of what your Python package does.

    full_name
    Your full name.

    email
    Your email address.

    github_username
    Your GitHub username.

    version
    The starting version number of the package.

    python_version
    Base python version you'd like the package to use. 

    docstrings_style
    one of `google, numpy, pep257`. It's required by flake8-docstrings.

    use_mypy
    If use mypy for static type check in pre-commit hooks and tox.

    install_precommit_hooks
    If you choose yes, then cookiecutter will install pre-commit hooks for you.



    ## Options

    The following package configuration options set up different features
    for your project.

    install_precommit_hooks
    Add checks to run with each git commit. Examples include linting and pytest.

    command_line_interface
    Whether to create a console script using Python Click. Console script
    entry point will match the project_slug. Options: \['click', "No
    command-line interface"\]
    ```

    except above settings, for CI/CD, you'll also need configure gitub repsitory secrets
    at page repo > settings > secrtes, and add the following secrets:

    - PERSONAL_TOKEN (required for publishing document to git pages)
    - TEST_PYPI_API_TOKEN (required for publishing dev release to testpypi)
    - PYPI_API_TOKEN (required for publish )
