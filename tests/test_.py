
from typing import Tuple, Dict, List, Any

import pytest

from pathlib import Path
import sys

PROJECT_DIR = Path(__file__).parents[1]
sys.path.append(str(PROJECT_DIR))

from py_code_cleaner.py_code_cleaner import read_text, clean_py, PathLike


@pytest.mark.parametrize('inpath', [PROJECT_DIR / 'tests' / 'input' / 'code1.py'])
@pytest.mark.parametrize(
    'filter_params',
    [
        dict(
            filter_empty_lines=True,
            filter_docstrings=True,
            filter_annotations=True
        ),
        dict(
            filter_empty_lines=False,
            filter_docstrings=True,
            filter_annotations=True
        ),
        dict(
            filter_empty_lines=True,
            filter_docstrings=False,
            filter_annotations=True
        ),
        dict(
            filter_empty_lines=True,
            filter_docstrings=True,
            filter_annotations=False
        ),
        dict(
            filter_empty_lines=True,
            filter_docstrings=False,
            filter_annotations=False
        ),
        dict(
            filter_empty_lines=False,
            filter_docstrings=True,
            filter_annotations=False
        ),
        dict(
            filter_empty_lines=False,
            filter_docstrings=False,
            filter_annotations=True
        ),
        dict(
            filter_empty_lines=False,
            filter_docstrings=False,
            filter_annotations=False
        ),
    ]
)
def test_clean_py(inpath: PathLike, filter_params: Dict):

    inpath = Path(inpath)

    stem = inpath.stem + '__' + '-'.join(f"{k}={v * 1}" for k, v in filter_params.items()) + '.py'

    outpath = inpath.parents[2] / 'tmp' / stem

    goldpath = inpath.parents[1] / 'output' / stem

    clean_py(inpath, outpath, **filter_params)

    assert read_text(outpath) == read_text(goldpath)

    print()




