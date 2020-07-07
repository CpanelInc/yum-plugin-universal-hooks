#!/usr/bin/env bash

HOOK_DIRS='
/etc/dnf/universal-hooks/transaction
/etc/dnf/universal-hooks/pkgs/zsh/transaction
/etc/dnf/universal-hooks/multi_pkgs/transaction/zs__WILDCARD__
'

for d in $HOOK_DIRS; do
    hook_script=$d/test-hook.sh

    mkdir -pv $d
    cat >$hook_script <<"EOH"
#!/usr/bin/env bash

echo "the $0 script with args: $*"

pkg_list=${1#--pkg_list=}
if [ -n "$pkg_list" ]; then
    echo "pkg_list:"
    cat $pkg_list
fi

echo done
EOH

    chmod +x $hook_script
done
