
from typing_extensions import TypeAlias
import sys
import os
from pathlib import Path
import shutil
import tempfile
import argparse
import ast
from ast import Constant
import astunparse
PathLike = Union[(str, os.PathLike)]

def mkdir_of_file(file_path):
    '\\n    creates parent directory of the file\\n    '
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)

def read_text(path, encoding='utf-8'):
    return Path(path).read_text(encoding=encoding, errors='ignore')

def write_text(result_path, text, encoding='utf-8'):
    mkdir_of_file(result_path)
    Path(result_path).write_text(text, encoding=encoding, errors='ignore')
_DOCSTRING_START = ("'" + '"')
'chars the docstring can start after unparse'

class NewLineProcessor(ast.NodeTransformer):
    "class for keeping '\\n' chars inside python strings during ast unparse"

    def visit_Constant(self, node):
        if isinstance(node.value, str):
            node.value = node.value.replace('\\n', '\\n')
        return node

class TypeHintRemover(ast.NodeTransformer):
    'ast tree transformer which removes all annotations functional from the code'

    def visit_FunctionDef(self, node):
        node.returns = None
        if node.args.args:
            for arg in node.args.args:
                arg.annotation = None
        self.generic_visit(node)
        return node

    def visit_AnnAssign(self, node):
        if (node.value is None):
            return None
        return ast.Assign([node.target], node.value)

    def visit_Import(self, node):
        node.names = [n for n in node.names if (n.name != 'typing')]
        return (node if node.names else None)

    def visit_ImportFrom(self, node):
        return (node if (node.module != 'typing') else None)

def clean_py(file_from, file_to, filter_empty_lines=True, filter_docstrings=True, filter_annotations=True):
    '\\n    remove comments and other data from python files\\n\\n    Args:\\n        file_from:\\n        file_to:\\n        filter_empty_lines: remove empty lines too\\n        filter_docstrings: remove docstrings too\\n        filter_annotations: remove annotations too\\n\\n    '
    p = Path(file_from)
    assert p.exists(), p
    assert (p.suffix == '.py'), file_from
    with open(file_from) as f:
        tree = ast.parse(f.read())
    if filter_annotations:
        tree = TypeHintRemover().visit(tree)
    tree = NewLineProcessor().visit(tree)
    lines = astunparse.unparse(tree).split('\\n')
    if filter_empty_lines:
        lines = (l for l in lines if l)
    if filter_docstrings:
        lines = (l for l in lines if (l.lstrip()[:1] not in _DOCSTRING_START))
    write_text(file_to, '\\n'.join(lines))

def clean_py_deep(dir_from, dir_to, keep_nonpy=('.pyx',), verbose=True, dry_run=False, **clean_py_kwargs):
    '\\n    Performs recursive clean_py with directories structure keeping\\n\\n    Args:\\n        dir_from:\\n        dir_to:\\n        keep_nonpy: non-python extensions for files which must be just copied, other files will be skipped\\n        verbose: whether to show process stats\\n        dry_run: whether to not perform any file creation operations\\n        **clean_py_kwargs:\\n\\n    '
    inpath = Path(dir_from)
    outpath = Path(dir_to)
    keep_nonpy = (set() if (keep_nonpy is None) else set(keep_nonpy))
    assert inpath.exists(), inpath
    _skipped = _copied = _processed = 0
    for p in inpath.rglob('*'):
        if p.is_dir():
            continue
        t = (outpath / p.relative_to(inpath))
        suff = t.suffix
        if (suff != '.py'):
            if (suff in keep_nonpy):
                if (not dry_run):
                    mkdir_of_file(t)
                    shutil.copyfile(p, t)
                _copied += 1
            else:
                _skipped += 1
        else:
            if (not dry_run):
                clean_py(p, t, **clean_py_kwargs)
            _processed += 1
    if verbose:
        print(f'Total files:         {((_skipped + _copied) + _processed)}\n skipped non-python: {_skipped}\n  copied non-python: {_copied}\n   processed python: {_processed}')

def clean_py_main(src, dst=None, keep_nonpy=('.pyx',), filter_empty_lines=True, filter_docstrings=True, filter_annotations=True, quiet=False, dry_run=False):
    '\\n    perform cleaning process from src to dst\\n    Args:\\n        src: python file path or path to directory with files\\n        dst: destination file or directory; empty means to print to stdout\\n        keep_nonpy: additional file extensions to transfer between src and dst directories (to not ignore)\\n        filter_empty_lines: whether to remove empty lines\\n        filter_docstrings: whether to remove docstrings\\n        filter_annotations: whether to remove annotations\\n        quiet: do not process output\\n        dry_run: do not perform any file creation operations\\n\\n    Returns:\\n\\n    '
    assert (not (quiet * dry_run)), (quiet, dry_run, '--quiet and --dry-run cannot be true both')
    verbose = (not quiet)
    src = Path(src)
    assert src.exists(), src
    if src.is_file():
        assert (src.suffix == '.py'), src
    filter_kwargs = dict(filter_empty_lines=filter_empty_lines, filter_docstrings=filter_docstrings, filter_annotations=filter_annotations)
    if dst:
        dst = Path(dst)
        if src.is_file():
            if (dst.exists() and dst.is_dir()):
                dst = (dst.parent / src.name)
            if verbose:
                print(f'Clean {str(src)} -> {str(dst)}')
            if (not dry_run):
                clean_py(src, dst, **filter_kwargs)
        else:
            if dst.exists():
                assert dst.is_dir(), f'src {str(src)} if dir, but dst {str(dst)} is not'
            if verbose:
                print(f'Clean directory {str(src)} -> {str(dst)}')
            clean_py_deep(src, dst, keep_nonpy=keep_nonpy, verbose=verbose, dry_run=dry_run, **filter_kwargs)
    else:
        assert (not dry_run), '--dry-run for no destination is not supported'
        assert src.is_file(), 'source as directory for no destination is not supported'
        import time
        dst = os.path.join(tempfile.gettempdir(), f'clean-py-no-dst{time.time()}')
        clean_py(src, dst, **filter_kwargs)
        print(read_text(dst))
        os.unlink(dst)
parser = argparse.ArgumentParser(prog='clean-py', description='Cleanses *.py files from comments, empty lines, annotations and docstrings', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('source', type=str, help='python file path or path to directory with files')
parser.add_argument('--destination', '-d', type=str, default=None, help='destination file or directory; empty means to print to stdout')
parser.add_argument('--keep-nonpy', '-k', nargs='+', type=str, default='', help='additional file extensions to transfer between src and dst directories (to not ignore)')
parser.add_argument('--keep-empty-lines', '-e', action='store_true', help='Whether to not remove empty lines')
parser.add_argument('--keep-docstrings', '-s', action='store_true', help='Whether to not remove docstrings')
parser.add_argument('--keep-annotations', '-a', action='store_true', help='Whether to not remove annotations')
parser.add_argument('--quiet', '-q', action='store_true', help='Do not print processing info')
parser.add_argument('--dry-run', '-n', action='store_true', help='Whether to run without performing file processing operations')

def main(args=None):
    kwargs = parser.parse_args((args or sys.argv[1:]))
    clean_py_main(kwargs.source, kwargs.destination, keep_nonpy=kwargs.keep_nonpy.split(), filter_docstrings=(not kwargs.keep_docstrings), filter_annotations=(not kwargs.keep_annotations), filter_empty_lines=(not kwargs.keep_empty_lines), quiet=kwargs.quiet, dry_run=kwargs.dry_run)
if (__name__ == '__main__'):
    main()
