def _transitive_cc_deps_impl(ctx):
    outputs = _get_transitive_cc_deps([], ctx.attr.deps)

    #print(outputs)
    return DefaultInfo(files = outputs)

_transitive_cc = rule(
    attrs = {
        "deps": attr.label_list(
            allow_files = True,
            providers = [DefaultInfo],
        ),
    },
    implementation = _transitive_cc_deps_impl,
)

def transitive_cc_deps(name, deps = [], **kwargs):
    _transitive_cc(name = name + "_gather", deps = deps)
    native.filegroup(name = name, srcs = [":" + name + "_gather"])

def _get_transitive_cc_deps(src, deps):
    """Obtain the header files for a target and its transitive dependencies.

      Args:
        src: a list of header files
        deps: a list of targets that are direct dependencies

      Returns:
        a collection of the transitive headers
      """
    return depset(
        src,
        transitive = [dep[DefaultInfo].files for dep in deps],
    )
