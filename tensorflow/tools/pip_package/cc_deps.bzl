def _transitive_cc_deps_impl_old(ctx):
    outputs = _get_transitive_cc_deps([], ctx.attr.deps)

    #print(outputs)
    return DefaultInfo(files = outputs)

def _transitive_cc_deps_impl(ctx):
    srcs = []
    for i in ctx.attr.deps:
        #print(i.name)
        temp = []
        #print(i[DefaultInfo])
        #print(i[DefaultInfo].data_runfiles.files.to_list())
        #print(i[DefaultInfo].default_runfiles.files.to_list())
        #print(i[DefaultInfo].files_to_run)
        #for s in i[DefaultInfo].to_list():
        for s in i[OutputGroupInfo]._hidden_top_level_INTERNAL_.to_list():
            #print(s.basename)
            #print(s.dirname)
            if s.dirname.startswith("bazel-out/k8-opt/bin/_solib_k8/"):
                continue
            if s.dirname.startswith("external/pypi"):
                continue
            if s.basename.startswith("_solib_k8/"):
                continue
            if not s.basename.endswith(".so") and not s.basename.endswith(".pyi") and not s.basename.endswith(".pyd"):
                continue
            if s.basename.startswith("libtensorflow_Spython_"):
                continue
            #if not s.basename.startswith("libtensorflow_framework.so.2") \
            #and not s.basename.startswith("lib_pywrap_tensorflow_internal.so") \
            #and s.basename.:
            temp.append(s)
            #print(s.basename)
            #print(s.dirname)
        srcs.extend(temp)
    return DefaultInfo(files=depset(
        srcs,
    ))

_transitive_cc = rule(
    attrs = {
        "deps": attr.label_list(
            allow_files = True,
            providers = [OutputGroupInfo],
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
    #for dep in deps:
    #    print(dep[OutputGroupInfo]._hidden_top_level_INTERNAL_)
    return depset(
        src,
        transitive = [dep[OutputGroupInfo]._hidden_top_level_INTERNAL_ for dep in deps],
    )
