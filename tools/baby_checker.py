"""This baby checker checks two things:
1. Is the LLMs codegen completed for each benchmark?
2. Warn the code that are not compilable (it could be some impl issues).
"""

import ast
import os
import traceback

from termcolor import colored


def get_all_python_files(folder):
    # return a list of full-path python files
    py_files = []
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith(".py"):
                py_files.append(os.path.join(root, file))
    return py_files


def syntax_check(code, verbose=False):
    try:
        ast.parse(code)
        return True
    except SyntaxError as e:
        if verbose:
            traceback.print_exc()
        return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", type=str, required=True)
    parser.add_argument("--dataset", type=str, default="humaneval")
    parser.add_argument("--nsample", type=int, default=200)
    parser.add_argument("--verbose", action="store_true")

    args = parser.parse_args()

    if args.dataset == "humaneval":
        ntask = 164
        print(colored("==============================", "blue"))
        print(colored(" ::: Checking completeness... ", "blue"))
        print(colored(" ::::: All tasks complete?    ", "blue"))
        ndone = 0
        for i in range(ntask):
            task_folder = os.path.join(args.folder, f"HumanEval_{i}")
            if not os.path.exists(task_folder):
                print(colored(f" ⚠️ HumanEval_{i} is missing!", "red"))
                continue
            # get the # of .py files under task_folder
            nfiles = len(get_all_python_files(task_folder))
            if nfiles != args.nsample:
                print(
                    colored(
                        f" ⚠️ HumanEval_{i} only has {nfiles} samples! But {args.nsample} are expected.",
                        "red",
                    )
                )
                continue
            ndone += 1
        if ntask != ndone:
            ntbd = ntask - ndone
            print(colored(f" ::::: ⚠️ {ntbd}/{ntask} tasks incomplete!", "red"))
        else:
            print(colored(f" ::::: All {ntask} tasks complete!", "green"))

        print(colored("==============================", "blue"))
        print(colored(" ::: Checking compilation...  ", "blue"))
        print(colored(" ::::: All code compilable?   ", "blue"))
        for i in range(ntask):
            task_folder = os.path.join(args.folder, f"HumanEval_{i}")
            # folder must exist
            if not os.path.exists(task_folder):
                continue

            for pyf in get_all_python_files(task_folder):
                if not syntax_check(open(pyf).read(), args.verbose):
                    simple_name = pyf.replace(
                        os.path.join(args.folder, "HumanEval_"), ""
                    )
                    print(colored(f" ⚠️ {simple_name} is not compilable!", "red"))
    else:
        raise NotImplementedError
