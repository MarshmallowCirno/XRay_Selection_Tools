import importlib
import pathlib
import types
from collections.abc import Iterator


def _module_children(module: types.ModuleType, package_dir: pathlib.Path) -> Iterator[types.ModuleType]:
    """Yields child modules of parent module within the specified package directory."""
    for attr in vars(module).values():
        if not isinstance(attr, types.ModuleType):
            continue
        if not (filename := getattr(attr, "__file__", None)):
            continue
        if package_dir not in pathlib.Path(filename).parents:
            continue
        yield attr


def _package_modules(package: types.ModuleType) -> list[types.ModuleType]:
    """Returns a list of all modules within a package, including submodules."""
    assert package.__file__ is not None
    package_dir = pathlib.Path(package.__file__).parent
    modules: list[types.ModuleType] = []
    stack: list[tuple[types.ModuleType, Iterator[types.ModuleType]]] = [
        (package, _module_children(package, package_dir))
    ]
    visited: set[str] = set()

    # Postorder traversal
    while stack:
        current_module, children = stack[-1]
        try:
            child = next(children)
            if child.__file__ in visited:
                continue
            assert child.__file__ is not None
            visited.add(child.__file__)
            stack.append((child, _module_children(child, package_dir)))
        except StopIteration:
            modules.append(current_module)
            stack.pop()

    return modules


def reload_package_modules(package: types.ModuleType) -> None:
    """Reloads all modules within a package."""
    assert hasattr(package, "__package__")
    for module in _package_modules(package):
        importlib.reload(module)
