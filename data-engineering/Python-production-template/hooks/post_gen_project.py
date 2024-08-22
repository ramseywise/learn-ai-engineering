#!/usr/bin/env python
import logging
import os
import subprocess
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

PROJECT_DIRECTORY = os.path.realpath(os.path.curdir)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("cookiecutter_setup.log"), logging.StreamHandler()],
)


def remove_file(filepath):
    try:
        os.remove(os.path.join(PROJECT_DIRECTORY, filepath))
    except FileNotFoundError:
        pass


def execute(args, suppress_exception=False, cwd=None):
    cur_dir = os.getcwd()

    try:
        if cwd:
            os.chdir(cwd)

        result = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=not suppress_exception,
            cwd=cwd,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        if not suppress_exception:
            raise
        else:
            return e.stderr
    finally:
        os.chdir(cur_dir)


def init_git():
    logging.info("Initializing git repository, moving to development branch")
    # workaround for issue #1
    if not os.path.exists(os.path.join(PROJECT_DIRECTORY, ".git")):
        execute(["git", "config", "--global", "init.defaultBranch", "main"])
        execute(["git", "init"], cwd=PROJECT_DIRECTORY)
        execute(["git", "checkout", "-b", "development"], cwd=PROJECT_DIRECTORY)


def install_pre_commit_hooks():
    logging.info("Installing pre-commit hooks")
    execute([sys.executable, "-m", "pip", "install", "pre-commit==2.12.0"])
    execute([sys.executable, "-m", "pre_commit", "install"])


def check_conda_env_exists(env_name):
    # Run the command 'conda env list' and capture the output
    result = subprocess.run(["conda", "env", "list"], stdout=subprocess.PIPE, text=True)

    # Check if the environment name is in the output
    return env_name in result.stdout


def display_getting_started_message():
    print(
        """
        Your new python project '{{ cookiecutter.project_name }}' is ready! 
        
        To get started, you'll need to activate the conda environment 
        and install the dependencies:
        > cd {{ cookiecutter.project_slug }}
        > conda activate {{ cookiecutter.conda_env_name }}
        > poetry install -E doc -E dev -E test
        > poetry run tox

        More 
        """
    )


def create_conda_environment(env_name):
    exists = check_conda_env_exists(env_name)

    try:
        if exists:
            logging.info(
                f"Conda environment {env_name} already exists, skipping creation."
            )
            return
        else:
            logging.info(
                f"Creating Conda environment: {env_name}, with python version: {{ cookiecutter.python_version }}"
            )
            execute(
                [
                    "conda",
                    "create",
                    "--name",
                    env_name,
                    "python=3.10",
                    "-y",
                ]
            )

        logging.info(f"Installing Poetry in Conda environment: {env_name}")
        execute(
            ["conda", "install", "-n", env_name, "-c", "conda-forge", "poetry", "-y"]
        )

        logging.info("Configuring Poetry")
        execute(
            [
                "conda",
                "run",
                "-n",
                env_name,
                "poetry",
                "config",
                "virtualenvs.in-project",
                "true",
            ]
        )

    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to create Conda environment: {e}")
        execute(["conda", "env", "remove", "--name", env_name, "python=3.10", "-y"])

        if e.stdout:
            logging.error("Output:", e.stdout.decode())
        if e.stderr:
            logging.error("Error:", e.stderr.decode())

        sys.exit(1)


def check_internet_connection():
    ping_request = Request("http://www.google.com")
    try:
        _ = urlopen(ping_request, timeout=3)  # Attempt to contact a reliable website
        logging.info("Internet connection verified")
    except HTTPError as e:
        # In case of server being reachable but the request fails
        logging.error("Server could be reached but the request failed with HTTP Error.")
        sys.exit(1)
    except URLError as e:
        # In case of the server being unreachable
        logging.error(
            """
            You don't appear to be connected to the internet. This is required for Conda 
            environment creation.
            """
        )
        sys.exit(1)


if __name__ == "__main__":
    conda_env_name = "{{ cookiecutter.conda_env_name }}"
    logging.info(
        f"Beginning post-gen hook execution. Conda environment name: \
            {conda_env_name}"
    )

    if conda_env_name:
        logging.info(f"Checking internet connection")
        check_internet_connection()
        create_conda_environment(conda_env_name)

    if "no" in "{{ cookiecutter.command_line_interface|lower }}":
        logging.info("Removing CLI")
        cli_file = os.path.join("{{ cookiecutter.pkg_name }}", "cli.py")
        remove_file(cli_file)

    logging.info("Handling license preferences")
    if "Not open source" == "{{ cookiecutter.open_source_license }}":
        remove_file("LICENSE")

    try:
        init_git()
    except Exception as e:
        logging.error(e)

    if "{{ cookiecutter.install_precommit_hooks }}" == "y":
        try:
            install_pre_commit_hooks()
        except Exception as e:
            logging.error(str(e))
            logging.error(
                """
                Failed to install pre-commit hooks.
                Please run `pre-commit install`
                by your self. For more on pre-commit,
                please refer to https://pre-commit.com
                """
            )

    display_getting_started_message()
