__version__ = version = "dev"
__version_tuple__ = version_tuple = "dev"

# this will be generate automatically when published by hatchling and hatch-vcs according to the git tag.
# For example if the tag was "release/v0.0.0a0", The generated file will look like this:

# # file generated by setuptools_scm
# # don't change, don't track in version control
# TYPE_CHECKING = False
# if TYPE_CHECKING:
#     from typing import Tuple, Union
#     VERSION_TUPLE = Tuple[Union[int, str], ...]
# else:
#     VERSION_TUPLE = object

# version: str
# __version__: str
# __version_tuple__: VERSION_TUPLE
# version_tuple: VERSION_TUPLE

# __version__ = version = '0.0.0a0'
# __version_tuple__ = version_tuple = (0, 0, 0)
