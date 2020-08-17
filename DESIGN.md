# Universal Hooks for `yum` and `dnf`

## Target Audiences

1. Maintenance and security teams
2. Training and technical support
3. Managers and other internal key stakeholders
4. Future project/feature owners/maintainers

## Detailed Summary

CentOS 8 replaced `yum` with a new package manager named `dnf`. The `dnf` hook system is *not* backwards compatible with `yum` [[1]]. Third-parties may rely on the cPanel universal hooks plugin and it is difficult to know if they use hooks that are not available in `dnf`.

## Overall Intent

To have the same experience on `dnf` systems as `yum` as far as universal hooks go.

### Hooks must fire for `dnf` like they do for `yum`

Otherwise things will be left in weird state because the hooks do things like update configutation and restart services.

There is not a one-to-one mapping from `yum` “slots” to `dnf` hook points [[1]]. Fortunately we only use the `posttrans` slot which does exist in `dnf` as the `transaction` hook point. That is likely to be true of the majority of users. If not we have documentation thay can use to make a decision on what to do.

### Hook installers must install the scripts to the correct places

For example, our hooks are installed by the `ea-apache24-config-runtime` package.

For `yum` systems that package must install its scripts under `/etc/yum/universal-hooks` using the “slot” `posttrans`.

For `dnf` systems that package must install its scripts under `/etc/dnf/universal-hooks` using the `transaction` hook point.

### The plugin should just work on any supported OS

Existing code (ours and possibly 3rdparty) need to be considered.

## Maintainability

Estimate:

1. how much time and resources will be needed to maintain the feature in the future
2. how frequently maintenance will need to happen

Very little, the python API doesn’t change much and when it did they came up with a whole new system (i.e. `dnf`).

Its possible that `dnf` will add hook points whcih we can then support [[2]].

## Options/Decisions

| Approach | Pros    | Cons |
| ---------|---------|------|
| Have `yum-plugin-universal-hooks` install different things on `yum` and `dnf` systems  | Just Works. | - |
| ↑ |  It can `Provide: dnf-plugin-universal-hooks` on `dnf` systems for convenience without casing confusion on `yum` systems. | - |
| ↑ | Both versions live together so if a change is needed we are less likely to overlook one. | - |
| ↑ | - | The spec file has to operate on different files based on the OS. |
| Create a new package `dnf-plugin-universal-hooks` | Clear delination of `yum` and `dnf` | - |
| ↑ | - | Any place we (or 3rdparty) deal with the `yum-plugin-universal-hooks` package would need updated to choose the right package based onthe OS. |
| ↑ | - | That would be impossible on older versions. |
| ↑ | - | Even if it `Provides: yum-plugin-universal-hooks` there would be a chicken and egg battle as versions change. |

### Conclusion

We opted for `yum-plugin-universal-hooks` doing the right thing because it requires far less effort, will have no chicken and egg problem, and the if/else logic is encapsulated in one spot.

[1]: https://dnf.readthedocs.io/en/latest/api_vs_yum.html
[2]: https://dnf.readthedocs.io/en/latest/api_plugins.html
