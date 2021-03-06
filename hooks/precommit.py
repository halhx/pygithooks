#!/usr/bin/env python
"""
precommit.py

Runner of python-based precommit hooks.
"""

import atexit
import copy
import os
import shutil
import sys
import tempfile

from check_comment import CheckComment
from check_indentation import CheckIndentation
from check_pep8 import CheckPep8
from check_tabs import CheckTabs
from util import get_config, run_command, run_piped_commands


def is_file_type(filename,  filetype):
    """
    Check if the file is of a certain type, eg. *.py, *.scala, etc.
    """
    return os.path.splitext(filename)[1] == "." + filetype

def changed_files(include_added_files=True):
    """
    Return a generator of filenames changed in this commit. Excludes files that were just deleted.
    """
    diff_filter = "CMRTUXB"
    if include_added_files:
        diff_filter += "A"

    git_diff_command = "git diff-index --name-only --diff-filter=%s HEAD" % diff_filter
    git_out, git_err, git_rc = run_command(git_diff_command)

    if git_err or git_rc:
        print "# Internal hook error:\n%s\n%s\n" % (git_out, git_err)
        sys.exit(1)

    cleaned_filenames = [filename.strip() for filename in git_out.splitlines()]
    for filename in cleaned_filenames:
        if len(filename) > 0:
            yield filename


def make_temp_copy(temp_dir_with_slash, filename):
    """
    Create a temporary copy of a file from the index.
    """
    # TODO: Once all the hooks can take straight text rather than files, just return text.

    temp_filename = os.path.join(temp_dir_with_slash, filename)
    if os.path.isfile(temp_filename):
        os.remove(temp_filename)

    git_cat_command = "git show :%(f)s" % dict(f=filename)
    git_out, git_err, git_rc = run_command(git_cat_command)

    if git_err or git_rc:
        print("# Internal hook error:\n%(out)s\n%(err)s\n" % dict(out=git_out, err=git_err))
        sys.exit(1)

    try:
        os.makedirs(os.path.dirname(temp_filename))
    except OSError:
        # dir already exists
        pass

    with open(temp_filename, "wb") as temp_outfile:
        temp_outfile.write(git_out)

    return temp_filename


def main():
    #hooks = [CheckTabs(), CheckIndentation()]
    hooks = [CheckComment()]

    #debug = get_config("debug", as_bool=True, default=False)
    debug = False # @TODO: hard code for now, use get_config later on
    

    incremental = get_config("incremental", as_bool=True, default=False)
    incremental_verbose = get_config("incremental.verbose", as_bool=True, default=False)

    if debug:
        print "Starting hooks, incremental %s, hooks [%s]" % (incremental, ", ".join(map(str, hooks)))

    # create temp directory for getting copies of files from staging.
    # TODO: Make all the hooks operate on strings instead of files, and get rid of this.
    temp_dir = tempfile.mkdtemp()
    temp_dir_with_slash = temp_dir + os.sep

    atexit.register(shutil.rmtree, temp_dir, True)  # clean up after ourselves

    failure_encountered = False

    if incremental:
        # Incremental checking requires checking the previous version of a
        # file for errors, but if the file was added, we can't do that.
        # Get a list of non-added changed files here to check against.
        modified_files = frozenset(changed_files(include_added_files=False))

    for filename in changed_files():
        if debug:
            print "Examining %s" % filename

        if not is_file_type(filename,  'scala'):
            if debug:
                print "Skipping %s, not a scala file" % filename
            continue

        relevant_hooks = [hook for hook in hooks if hook.should_process_file(filename)]
        
        if debug:
            print "relevant hooks are: ", relevant_hooks
        if not relevant_hooks:
            if debug:
                print "Skipping %s, no relevant hooks" % filename
            continue

        if incremental and filename in modified_files:
            head_temp_filename = make_temp_copy(temp_dir_with_slash, filename)
            incremental_hooks = copy.copy(relevant_hooks)
            if os.path.isfile(head_temp_filename):
                # This is not a newly added file, so check whether it used to fail the hooks.
                for relevant_hook in relevant_hooks:
                    head_passes, unused_error_message = relevant_hook.file_passes(head_temp_filename, original_filename=filename)
                    if not head_passes:
                        # Incremental checking was requested, and current HEAD doesn't pass,
                        # so don't bother checking this file with this hook.
                        incremental_hooks.remove(relevant_hook)
                        if incremental_verbose:
                            print "Hook %s failed on current HEAD for file %s" % (relevant_hook, filename)
            relevant_hooks = incremental_hooks

        if not relevant_hooks:
            if debug:
                print "Skipping %s, no relevant hooks (after incremental check)" % filename
            continue

        temp_filename = make_temp_copy(temp_dir_with_slash, filename)
        for relevant_hook in relevant_hooks:
            passes, error_message = relevant_hook.file_passes(temp_filename, original_filename=filename)            
            print(filename + " --> " + error_message)
            if not passes:
                failure_encountered = True
                break

    return int(failure_encountered)

if __name__ == '__main__':
    sys.exit(main())
