#!/usr/bin/env bash

HOOK_DIRS='
/etc/yum/universal-hooks/posttrans
/etc/yum/universal-hooks/pkgs/zsh/posttrans
/etc/yum/universal-hooks/multi_pkgs/posttrans/zs__WILDCARD__
'

if [ -x "/usr/bin/dnf" ];
then
HOOK_DIRS='
/etc/dnf/universal-hooks/transaction
/etc/dnf/universal-hooks/pkgs/zsh/transaction
/etc/dnf/universal-hooks/multi_pkgs/transaction/zs__WILDCARD__
'
fi

for d in $HOOK_DIRS; do
    hook_script=$d/test-hook.sh

    mkdir -pv $d
    cat >$hook_script <<"EOH"
#!/usr/bin/env bash

echo "Universal Hook Fired: “$0” with args: $*"

pkg_list=${1#--pkg_list=}
if [ -n "$pkg_list" ]; then
    echo "pkg_list:"
    cat $pkg_list
fi

echo " … done ($0)"
echo ""
EOH

    chmod +x $hook_script
done
