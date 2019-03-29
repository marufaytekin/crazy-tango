from tasks import *

log = logging.getLogger(__name__)


def print_tree_symbol(c, indent=1):
    """
        Use ASCII symbols to represent Sequence, Selector, Task, etc.
    """
    if isinstance(c, Selector):
        print("    " * indent, "--?"),
    elif isinstance(c, (Sequence, Iterator)):
        print("    " * indent, "-->"),
    elif isinstance(c, ParallelOne):
        print("    " * indent, "==?"),
    elif isinstance(c, ParallelAll):
        print("    " * indent, "==>"),
    elif isinstance(c, Loop):
        print("    " * indent, "<->"),
    elif isinstance(c, Invert):
        print("    " * indent, "--!"),
    else:
        print("    " * indent, "--|"),
    print(c.name)


def print_phpsyntax_tree(tree):
    """
        Print an output compatible with ironcreek.net/phpSyntaxTree
    """
    import queue
    q = queue.Queue()
    indent = 10

    q.put(tree)
    while q.not_empty:
        item = q.get()
        s = ""
        for c in item.children:
            s = s + " " * indent + c.name
            q.put(c)
        print(s)
        indent -= 1


def print_tree(tree, indent=0, use_symbols=False):
    """
        Print an ASCII representation of the tree
    """
    if use_symbols:
        if indent == 0:
            print_tree_symbol(tree, indent)
            indent += 1

        for c in tree.children:
            print_tree_symbol(c, indent)

            try:
                if c.children:
                    print_tree(c, indent + 1, use_symbols)
            except:
                pass
    else:
        for c in tree.children:
            print("    " * indent, "-->", c.name)

            try:
                if c.children:
                    print_tree(c, indent + 1)
            except:
                pass
