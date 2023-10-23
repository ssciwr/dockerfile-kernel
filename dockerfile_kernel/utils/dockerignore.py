from fnmatch import fnmatch
import os


def dockerignore(docker_ignore_dir: str, rules: list[str]):
    """Helper function to be added to `shutil.copytree` as the ignore function"""

    def ignore_function(directory: str, contents: list[str]):
        # Path from docker_ignore_dir to the current directory
        rel_path = os.path.relpath(directory, docker_ignore_dir)
        if rel_path == ".":
            rel_path = ""

        ignore: list[str] = []
        for content in contents:
            add_to_ignore = False
            rel_file_path = os.path.join(rel_path, content)
            for rule in rules:
                match, negated = match_dockerignore(rel_file_path, rule)
                if match and negated:
                    add_to_ignore = False
                elif match and not negated:
                    add_to_ignore = True
            if add_to_ignore:
                ignore.append(content)
        return ignore

    return ignore_function


def match_dockerignore(path: str, pattern: str):
    is_negated = False
    if pattern.startswith("!"):
        pattern = pattern[1:]
        is_negated = True

    # Special case **
    # Start matching from the right (default for fnmatch)
    if pattern.startswith("**"):
        root_pattern = pattern.removeprefix("**").removeprefix(os.path.sep)
        return (fnmatch(path, pattern) or fnmatch(path, root_pattern), is_negated)

    # Use segments to match from the left side
    pattern_segments = pattern.split(os.path.sep)
    path_segments = path.split(os.path.sep)

    # The pattern is not suitable for a path if longer than it
    if len(pattern_segments) > len(path_segments):
        return (False, is_negated)

    for pattern_seg, path_seg in zip(pattern_segments, path_segments):
        if not fnmatch(path_seg, pattern_seg):
            return (False, is_negated)

    return (True, is_negated)


def preporcessed_dockerignore(directory):
    """Read the `.dockerignore` and return its preprocessed rules"""
    di_path: str | None = None
    di_file: str | None = None
    for filename in os.listdir(directory):
        if filename.endswith(".dockerignore"):
            di_file = filename
            di_path = os.path.join(directory, filename)

    if di_path is None:
        return []
    with open(di_path, "r") as dockerignore:
        rules = dockerignore.readlines()

    preprocessed_rules: list[str] = []
    for rule in rules:
        pp_rule = preprocess_rule(rule)
        if pp_rule is not None:
            preprocessed_rules.append(pp_rule)

    # Add rule to include .dockerignore at the end of the rule list
    preprocessed_rules.append(f"!{di_file}")
    return preprocessed_rules


def preprocess_rule(rule: str):
    """
    Preprocess dockerignore rules.

    As described [here](https://docs.docker.com/engine/reference/builder/#dockerignore-file) the docker daemon uses Go's [filepath.Clean](https://pkg.go.dev/path/filepath#Clean) to do so.

    `os.path.normpath()` yields a similar (if not same) result. For simplicity and until there is an error regarding this, we will use this method.
    """
    # Remove comments
    if rule.startswith("#"):
        return None
    # Remove ! as this is just a prefix for a path
    processed_rule = os.path.normpath(rule).removeprefix("!").strip().removeprefix("!")
    # The root of the context is considered to be both the working and the root directory
    processed_rule = processed_rule.removeprefix(os.path.sep)
    # Add ! back
    if rule.lstrip().startswith("!"):
        processed_rule = "!" + processed_rule

    return processed_rule
