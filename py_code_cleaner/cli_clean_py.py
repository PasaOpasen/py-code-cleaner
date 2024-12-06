
from typing import Optional, Sequence

import sys
import argparse

from .py_code_cleaner import clean_py_main


#region CLI

parser = argparse.ArgumentParser(
    prog='clean-py',
    description='Cleanses *.py files from comments, empty lines, annotations and docstrings',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
parser.add_argument('source', type=str, help='python file path or path to directory with files')

parser.add_argument(
    '--destination', '-d', type=str, default=None,
    help='destination file or directory; empty means to print to stdout'
)

parser.add_argument(
    '--keep-nonpy', '-k',
    nargs="+",
    type=str, default='',
    help='additional file extensions to transfer between src and dst directories (to not ignore)'
)

parser.add_argument(
    '--keep-empty-lines', '-e',
    action='store_true',
    help='Whether to not remove empty lines'
)

parser.add_argument(
    '--keep-docstrings', '-s',
    action='store_true',
    help='Whether to not remove docstrings'
)

parser.add_argument(
    '--keep-annotations', '-a',
    action='store_true',
    help='Whether to not remove annotations'
)

parser.add_argument(
    '--quiet', '-q',
    action='store_true',
    help='Do not print processing info'
)

parser.add_argument(
    '--dry-run', '-n',
    action='store_true',
    help='Whether to run without performing file processing operations'
)


def main(args: Optional[Sequence[str]] = None):
    kwargs = parser.parse_args(args or sys.argv[1:])

    clean_py_main(
        kwargs.source, kwargs.destination,
        keep_nonpy=kwargs.keep_nonpy.split(),
        filter_docstrings=not kwargs.keep_docstrings,
        filter_annotations=not kwargs.keep_annotations,
        filter_empty_lines=not kwargs.keep_empty_lines,
        quiet=kwargs.quiet,
        dry_run=kwargs.dry_run
    )


#endregion


if __name__ == '__main__':
    main()



