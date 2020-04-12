import git
from pathlib import Path
import subprocess
import re
import uuid
import codecs
import config


def run(command: str, cwd=None) -> str:
    working_dir = cwd
    if cwd is not None:
        p = Path(cwd)
        if p.is_file():
            working_dir = p.parent

    return subprocess.run(
        command, shell=True, cwd=working_dir, stdout=subprocess.PIPE
    ).stdout.decode("utf-8")


class LOC(object):
    files_num = 0
    blank_num = 0
    comment_num = 0
    code_num = 0

    def __init__(self, files_num=0, blank_num=0, comment_num=0, code_num=0):
        self.files_num = files_num
        self.blank_num = blank_num
        self.comment_num = comment_num
        self.code_num = code_num


def _convert_cloc_line_to_object(line) -> LOC:
    split_line = line.strip().split()
    files_num = int(split_line[1])
    blank_num = int(split_line[2])
    comment_num = int(split_line[3])
    code_num = int(split_line[4])
    return LOC(files_num, blank_num, comment_num, code_num)


def get_java_sloc(path: str, commit_id=None):
    return get_java_loc(path, commit_id).code_num


def get_java_loc(path: str, commit_id=None):
    if commit_id is None:
        output = run("cloc --include-lang=C '{}'".format(path))
    else:
        output = run("cloc --include-lang=C '{}' {}".format(path, commit_id), cwd=path)
    pattern = ".*C.*"
    m = re.search(pattern, output)
    result = LOC()
    if m is not None:
        line = m.group(0)
        result = _convert_cloc_line_to_object(line)

    return result


def get_java_loc_diff(old_path: str, new_path: str):
    output = run("cloc --diff --diff-timeout 1000 '{}' '{}'".format(old_path, new_path))
    pattern = ".*C(\s.*){4}"
    m = re.search(pattern, output)
    same = LOC()
    modified = LOC()
    added = LOC()
    removed = LOC()

    if m is not None:
        lines = m.group(0).split("\n")
        lines.pop(0)
        for line in lines:
            line_type = line.split()[0]
            loc_detail = _convert_cloc_line_to_object(line)
            if line_type == "same":
                same = loc_detail
            elif line_type == "modified":
                modified = loc_detail
            elif line_type == "added":
                added = loc_detail
            elif line_type == "removed":
                removed = loc_detail

    return {"same": same, "modified": modified, "added": added, "removed": removed}


def get_spec_commit(commit_hash: str):
    git_repo = get_project_repository("/home/keyur/Desktop/LinuxWorkingGit/linux")
    return git_repo.commit(commit_hash)


def get_project_repository(path: str):
    repository = git.Repo(path)
    assert not repository.bare
    return repository


def get_diff_between_commits(parent_commit, head_commit):
    return parent_commit.diff(head_commit, create_patch=False)


def generate_hex_uuid_4() -> str:
    """Generate UUID (version 4) in hexadecimal representation.
    :return: hexadecimal representation of version 4 UUID.
    """
    return str(uuid.uuid4().hex)


def generate_random_file_name_with_extension(file_extension: str) -> str:
    return "{}.{}".format(generate_hex_uuid_4(), file_extension)


def is_c_file(file_path: str):
    if file_path.endswith(".c"):
        return True
    else:
        return False


def is_file_exists(file_path: str) -> bool:
    path = Path(file_path)
    return path.exists()


def delete_if_exists(file_path: str):
    path = Path(file_path)
    if path.exists():
        path.unlink()


def update_log_loc(component, added, deleted, modified):
    if component == "core":
        config.core_add += added
        config.core_del += deleted
        config.core_mod += modified
    if component == "fs":
        config.fs_add += added
        config.fs_del += deleted
        config.fs_mod += modified
    if component == "driver":
        config.driver_add += added
        config.driver_del += deleted
        config.driver_mod += modified
    if component == "net":
        config.net_add += added
        config.net_del += deleted
        config.net_mod += modified
    if component == "arch":
        config.arch_add += added
        config.arch_del += deleted
        config.arch_mod += modified
    if component == "misc":
        config.misc_add += added
        config.misc_del += deleted
        config.misc_mod += modified
    if component == "firmware":
        config.firmware_add += added
        config.firmware_del += deleted
        config.firmware_mod += modified


def print_stats():
    print("core")
    print("added " + str(config.core_add))
    print("deleted " + str(config.core_del))
    print("mod " + str(config.core_mod))

    print("fs")
    print("added " + str(config.fs_add))
    print("deleted " + str(config.fs_del))
    print("mod " + str(config.fs_mod))

    print("driver")
    print("added " + str(config.driver_add))
    print("deleted " + str(config.driver_del))
    print("mod " + str(config.driver_mod))

    print("net")
    print("added " + str(config.net_add))
    print("deleted " + str(config.net_del))
    print("mod " + str(config.net_mod))

    print("arch")
    print("added " + str(config.arch_add))
    print("deleted " + str(config.arch_del))
    print("mod " + str(config.arch_mod))

    print("misc")
    print("added " + str(config.misc_add))
    print("deleted " + str(config.misc_del))
    print("mod " + str(config.misc_mod))

    print("firmware")
    print("added " + str(config.firmware_add))
    print("deleted " + str(config.firmware_del))
    print("mod " + str(config.firmware_mod))


def get_component(filepath):
    core_files = ["init", "block", "ipc", "kernel", "lib", "mm", "virt"]
    fs_files = ["fs"]
    driver_files = ["crypto", "drivers", "sound", "security"]
    net_files = ["net"]
    arch_files = ["arch"]
    misc_files = [
        "Documentation",
        "scripts",
        "samples",
        "usr",
        "MAINTAINERS",
        "CREDITS",
        "README",
        ".gitignore",
        "Kbuild",
        "Makefile",
        "REPORTING-BUGS",
        ".mailmap",
        "COPYING",
        "tools",
        "Kconfig",
        "LICENSES",
        "certs",
        ".clang-format",
    ]
    firmware_files = ["firmware"]

    folder = filepath.split("/")[0]

    if folder in core_files:
        return "core"
    if folder in fs_files:
        return "fs"
    if folder in driver_files:
        return "driver"
    if folder in net_files:
        return "net"
    if folder in arch_files:
        return "arch"
    if folder in misc_files:
        return "misc"
    if folder in firmware_files:
        return "firmware"

    return ""


def generate_c_file_of_blob(file_blob):
    java_name = generate_random_file_name_with_extension("c")
    java_p = Path(java_name)
    java_p.write_bytes(file_blob.data_stream.read())
    return str(java_p.resolve())


def diff_inspector(commit_diff, head_commit_db):
    for file_diff in commit_diff:
        if file_diff.change_type == "A":
            try:
                handle_added_file(file_diff, head_commit_db)
            except:
                pass
        elif file_diff.change_type == "D":
            try:
                handle_deleted_file(file_diff, head_commit_db)
            except:
                pass
        elif file_diff.change_type == "M" or (
            file_diff.change_type.startswith("R")
            and file_diff.a_blob != file_diff.b_blob
        ):
            try:
                handle_updated_file(file_diff, head_commit_db)
            except:
                pass


def handle_added_file(file_diff, head_commit_db):
    sloc, component = handle_added_or_deleted_file(
        file_diff.b_path, file_diff.b_blob, "ADD", head_commit_db,
    )
    update_log_loc(component, sloc, 0, 0)


def handle_deleted_file(file_diff, head_commit_db):
    sloc, component = handle_added_or_deleted_file(
        file_diff.a_path, file_diff.a_blob, "DEL", head_commit_db,
    )
    update_log_loc(component, 0, sloc, 0)


def handle_added_or_deleted_file(file_path, file_blob, change_type, head_commit_db):
    file_logging_loc = 0
    component = get_component(file_path)
    if is_c_file(file_path):
        c_file = generate_c_file_of_blob(file_blob)
        file_logging_loc = get_java_sloc(c_file)
        delete_if_exists(c_file)
    return file_logging_loc, component


def handle_updated_file(file_diff, head_commit_db):
    if is_c_file(file_diff.a_path) and is_c_file(file_diff.b_path):
        component = get_component(file_diff.b_path)
        c_a_file = generate_c_file_of_blob(file_diff.a_blob)
        c_b_file = generate_c_file_of_blob(file_diff.b_blob)

        loc_diff = get_java_loc_diff(c_a_file, c_b_file)
        file_added_sloc = loc_diff["added"].code_num
        file_deleted_sloc = loc_diff["removed"].code_num
        file_updated_sloc = loc_diff["modified"].code_num

        delete_if_exists(c_a_file)
        delete_if_exists(c_b_file)
        update_log_loc(
            component, file_added_sloc, file_deleted_sloc, file_updated_sloc,
        )


if __name__ == "__main__":
    config.initialize()
    with open("commits", "r") as f:
        cc = f.readlines()
    for i in range(0, len(cc)):
        sha = cc[i]
        head_commit = get_spec_commit(sha)

        if head_commit.parents:
            for parent_commit in head_commit.parents:
                diff = get_diff_between_commits(parent_commit, head_commit)
                diff_inspector(diff, head_commit)
    print_stats()
