---
name: linux-speed-optimizer
description: >
  Use when the user asks to optimize, speed up, tune, or make a Linux system
  faster — laptops, desktops, or servers. Analyzes hardware, kernel and boot
  parameters, memory/swap/zram, storage, services, GPU, desktop environment,
  and network; proposes a prioritized, risk-labeled optimization plan;
  applies ONLY user-approved changes; verifies every change and documents
  rollback. Idempotent: re-running on the same system converges, never
  duplicates config, never re-installs. Analyze-only mode is available.
  Do NOT use for application code, containers, or website performance.
---

# Linux Speed Optimizer

Analyze first. Approve first. Apply only approved changes. Verify everything.
Rollback must always be documented before a change is applied.

This skill drives a full system-performance audit and safe optimization of a
Linux machine. It is distro- and agent-agnostic: detect the real environment
before choosing commands. It must converge when run twice on the same system.

## 0. Operating principles

1. **Analyze-only until approved.** No writes, no restarts, no installs before
   the user approves a concrete plan. Offer an explicit analyze-only mode.
2. **Idempotency.** Every action is guarded by a state check (grep, `systemctl
   is-enabled`, `dpkg -s`, `apt-cache policy`, `sysctl` readback). If the target
   state already exists, do nothing. Re-running MUST produce the same result.
3. **Evidence over cargo cult.** Never apply a tuning value just because it is
   popular. Each recommendation must be justified by what the analysis found
   (e.g., swappiness depends on zram vs disk swap; page-cluster only matters
   with swap; c-state limiting trades battery for latency).
4. **Security tradeoffs are explicit approvals.** Anything that reduces
   security (e.g., `mitigations=off`) or reliability (c-state caps, custom
   kernels) is presented as a labeled tradeoff and approved separately.
5. **Ask per service.** Never blanket-disable daemons. Docker, databases, or
   Bluetooth may be actively used. Ask for each one; show RAM/boot cost.

## 1. Preflight

- Check privilege: `sudo -n true`. If sudo needs a password, ask the user to
  run `sudo -v` in their own terminal to cache credentials. NEVER ask for,
  store, echo, or log a password.
- Record baseline: `uname -a`, `/etc/os-release`, uptime, kernel cmdline
  (`cat /proc/cmdline`).
- Detect package manager: `apt` / `dnf` / `pacman` / `zypper` / `apk`.
- Detect init: `ps -p 1 -o comm=`. systemd is assumed below; adapt if not.
- Detect desktop: `ls /usr/share/xsessions/`, `$XDG_CURRENT_DESKTOP`.

## 2. Analysis (read-only)

Gather the full picture in parallel batches. Do not skip domains — a hidden
bottleneck is usually in the one you skipped.

### 2a. Hardware & kernel
```bash
uname -a; lscpu | head -30; free -h; cat /proc/swaps; cat /proc/cmdline
lspci | grep -iE 'vga|3d|network'; cat /sys/class/dmi/id/product_name 2>/dev/null
```

### 2b. Storage
```bash
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT,ROTA
mount | grep -E ' / | /home| /tmp'
cat /sys/block/*/queue/scheduler 2>/dev/null
df -h / /home /tmp 2>/dev/null
```
Notes: `ROTA=0` = SSD (fstrim/`discard` relevant); `ROTA=1` = HDD. Check
`noatime` vs `relatime` in mount options. Check `fstrim.timer` / `fstrim -v`
dry run on SSD.

### 2c. Memory pressure (the most common laptop bottleneck)
```bash
free -h; zramctl 2>/dev/null; cat /proc/meminfo | grep -E 'MemTotal|SwapTotal|SwapFree'
ps aux --sort=-%mem | head -12; ps aux --sort=-%cpu | head -8
```
Check whether swap is actually in use (SwapUsed > 0), zram vs disk swap
priority, and the memory footprint of always-on daemons.

### 2d. Boot
```bash
systemd-analyze; systemd-analyze blame | head -15; systemd-analyze critical-chain
grep -E 'GRUB_TIMEOUT|GRUB_CMDLINE' /etc/default/grub
systemctl list-unit-files --state=enabled --no-pager
```

### 2e. GPU & display
```bash
lspci -k | grep -A3 -iE 'vga|3d'
# compositor state per DE (example, Xfce):
xfconf-query -c xfwm4 -p /general/use_compositing 2>/dev/null
```

### 2f. Power & thermals
```bash
for z in /sys/class/thermal/thermal_zone*/; do echo "$z $(cat $z/type) $(cat $z/temp)"; done
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null
cat /sys/devices/system/cpu/cpu0/cpuidle/state*/name 2>/dev/null
systemctl is-active tlp thermald 2>/dev/null
```

### 2g. Existing tuning (critical for idempotency)
```bash
grep -rn . /etc/sysctl.d/*.conf /etc/sysctl.conf 2>/dev/null | grep -v '^#'
ls /etc/sysctl.d/; cat /etc/default/zramswap /etc/default/earlyoom 2>/dev/null
```
Check for key collisions: within `/etc/sysctl.d`, files load in lexicographic
order and the LAST file wins. When adding or changing keys, either edit the
winning file or name the new file so it loads after (e.g. `99z-...conf`), then
verify with a live `sysctl` readback.

### 2h. Findings table

Produce a table like:

| Domain | Finding | Impact | Risk | Effort |
|---|---|---|---|---|
| Memory | 1.4G of 5.7G swap in use on 4G RAM | High | Low | Low |

Label each row: impact (high/med/low), risk (low/med/high), effort. Only
high-impact, low-risk items go into the default plan; risky items are optional
packages.

## 3. Approval gate

Present the plan as **packages** (e.g., memory/swap, boot cleanup, services,
GPU, kernel parameters, custom kernel, hardware advice). Ask the user to
approve each package with the question tool. Rules:

- Never apply an unapproved package.
- For every service disable, show what it is and its boot/RAM cost, and ask.
- Security-relevant items (`mitigations=off`, disabling ufw/apparmor) are
  their own package and require explicit approval.
- Custom kernel installs are their own package with a revert path shown.
- Hardware advice (e.g., "add a RAM stick") is reported, not applied.

## 4. Applying changes (idempotent recipes)

Every recipe: **guard → apply → verify**. If the guard shows the target state
already exists, skip. Use `grep -q` / `test -f` / `systemctl is-enabled`
guards; never blindly overwrite config files.

### 4.1 sysctl tuning

Guard: grep the target key across `/etc/sysctl.d/*.conf` and `/etc/sysctl.conf`
first. Respect load order (last file wins). Write a drop-in ONLY for keys that
are missing or conflicting, using a filename that sorts after existing files
(e.g. `99z-linux-optimizer.conf`) OR edit the existing winning file in place —
never both, never duplicate keys.

```bash
# Example drop-in: only write keys that are absent/conflicting
grep -q '^vm.swappiness=' /etc/sysctl.d/99z-linux-optimizer.conf 2>/dev/null \
  || echo 'vm.swappiness=100' | sudo tee -a /etc/sysctl.d/99z-linux-optimizer.conf
sudo sysctl --system >/dev/null
/sbin/sysctl vm.swappiness   # readback MUST match
```

Common justified settings (only when analysis supports them):
- `vm.swappiness=100` + `vm.vfs_cache_pressure=50` — only with zram swap on a
  low-RAM system (keeps anon pages compressed instead of evicting cache).
  With disk-only swap, prefer swappiness 10–30.
- `vm.page-cluster=0` — helps zram swap latency (no readahead for compressed
  pages).
- `vm.dirty_background_ratio=5` / `vm.dirty_ratio=10` — lower writeback bursts
  on low-RAM systems.
- `vm.dirty_writeback_centisecs=1500` — fewer wakeups on laptops.

### 4.2 zram (swap-in-RAM)

Detect the config mechanism per distro:
- zram-tools (Debian/Ubuntu): `/etc/default/zramswap` — set `PERCENT`/`SIZE`,
  `ALGO=zstd` (balance) or `lz4` (speed), keep `PRIORITY` above disk swap.
- zram-generator (Fedora/Arch/Systemd): `/etc/systemd/zram-generator.conf`.
- systemd-swap: `/etc/systemd/swap.conf`.

Guard: only edit if the value differs, and only restart the service
(`systemctl restart zramswap` or `systemctl daemon-reload && systemctl start
systemd-zram-setup@zram0`) if a change was made. Verify with `zramctl`.
Reasonable ceiling: 50–80% of RAM (zram consumes RAM itself, compressed).

### 4.3 earlyoom / oomd

```bash
grep -q -- '-m 5' /etc/default/earlyoom || sudo sed -i \
  's|^EARLYOOM_ARGS=.*|EARLYOOM_ARGS="-m 5 -s 5"|' /etc/default/earlyoom
# restart only if the file actually changed; verify: ps -ef | grep earlyoom
```
Debian/Ubuntu: package `earlyoom`. Fedora: `systemd-oomd` is default (prefer
it there). Arch: `earlyoom` in AUR/extra.

### 4.4 Services & timers

Guard with `systemctl is-enabled <unit>` — skip if already disabled. Only
disable units the user approved. Common safe candidates: `ModemManager`,
`NetworkManager-wait-online`, `bluetooth`, `avahi-daemon`, host DB servers if
the workload runs elsewhere (e.g., MariaDB in Docker). Verify with
`systemctl is-enabled` and re-check boot time via `systemd-analyze`.

### 4.5 Kernel command line (GRUB)

```bash
grep -q 'i915.enable_fbc=1' /etc/default/grub \
  || sudo sed -i 's|^GRUB_CMDLINE_LINUX_DEFAULT="\(.*\)"|GRUB_CMDLINE_LINUX_DEFAULT="\1 i915.enable_fbc=1"|' /etc/default/grub
grep -q '^GRUB_TIMEOUT=1$' /etc/default/grub \
  || sudo sed -i 's|^GRUB_TIMEOUT=.*|GRUB_TIMEOUT=1|' /etc/default/grub
sudo update-grub
sudo grep -c 'i915.enable_fbc=1' /boot/grub/grub.cfg   # must be > 0
```
Rules:
- GRUB_TIMEOUT=0/1 only if the system is single-OS or the user accepts no
  menu; 1 is the safe compromise.
- C-state limiting (`processor.max_cstate=1 intel_idle.max_cstate=0`) reduces
  latency but hurts battery and idle temperature — label the tradeoff.
- `mitigations=off` is a SECURITY tradeoff — only keep it if already present
  or explicitly approved; never introduce it silently.
- Intel-only params (FBC): check the GPU vendor first (`lspci`).
- Verify the generated `grub.cfg` actually contains the parameter; also check
  `/boot/grub2/grub.cfg` or EFI paths on non-Debian distros.

### 4.6 Desktop compositor

Only when the analysis shows a weak iGPU (Intel HD 5xx or older, no discrete
GPU) and a compositor is running:
```bash
# Xfce example
xfconf-query -c xfwm4 -p /general/use_compositing -s false  # guard: only if true
```
Verify with readback. Other DEs: disable picom/compton via their config or
GNOME/KDE settings — never delete configs, only toggle the running state.

### 4.7 Custom kernel (optional package, distro-specific)

- Determine CPU microarchitecture level: `lscpu | grep -o 'avx2'` present ⇒
  x86-64-v3 is safe; only AVX ⇒ v2; none ⇒ v1. Never install v3 on v2 hardware.
- Debian/Ubuntu: XanMod (`https://xanmod.org`, repo key + `linux-xanmod-x64vX`)
  or Liquorix. Fedora: kernel-bore or XanMod COPR. Arch: `linux-xanmod` or
  `linux-zen` (official, easier). 
- Check Secure Boot first: `mokutil --sb-state`. Unsigned kernels require
  Setup Mode or MOK enrollment.
- Guard: `dpkg -s linux-xanmod-x64v3` / `pacman -Q linux-xanmod` — skip if
  already installed.
- NEVER remove the distro kernel — it stays as the GRUB fallback and revert
  path. Document revert: boot fallback + `apt purge` / `pacman -R`.
- After install, verify the new kernel ships modules for the machine's actual
  devices: `find /lib/modules/<ver>/kernel -name 'i915.ko' -o -name
  'rtl8821ae.ko'` etc. before recommending a reboot.

## 5. Verification matrix

Verify AFTER every change with readbacks, not assumptions:

| Change | Verify with |
|---|---|
| sysctl | `/sbin/sysctl <key>` matches target |
| zram | `zramctl` shows expected size/algorithm |
| earlyoom | `ps -ef | grep earlyoom` shows new args |
| service disable | `systemctl is-enabled <unit>` = disabled |
| GRUB params | `grep <param> /boot/grub/grub.cfg` count > 0 |
| compositor | `xfconf-query -c xfwm4 -p /general/use_compositing` = false |
| package install | `dpkg -s`/`pacman -Q` present, kernel in GRUB menu |
| system integrity | `sudo apt-get check` / `sudo dnf check` / `pacman -Qk` clean |

Also re-run `free -h` and `systemd-analyze` to show before/after numbers when
they changed (e.g., swap usage, boot time).

## 6. Report & handoff

End with:
- **Applied** table (change, before, after).
- **Needs reboot** list (GRUB/kernel/FBC changes; nothing else needs one).
- **Rollback table**: exact commands to undo each change (e.g., revert sed,
  `systemctl enable`, `apt purge`).
- **Hardware advice**: if RAM < 8G with swap in use, state plainly that adding
  RAM is the highest-impact upgrade; verify stick count via `dmidecode -t
  memory` when possible.
- **Honest expectations**: label expected gains (e.g., "UI snappiness", "less
  swap thrash") — never promise benchmark numbers.

## 7. Idempotency guarantees

Before finishing, re-run the guards and confirm: no duplicate config lines
appear after a second run, no package was re-installed, no service was
re-disabled (already disabled), no file gained a second copy of a key, and the
final `sysctl`/`systemctl`/`zramctl` readbacks are stable. The skill is
convergent: state unchanged ⇒ no action.

## 8. Distribution matrix (adapt commands)

| Concern | Debian/Ubuntu | Fedora | Arch | openSUSE |
|---|---|---|---|---|
| zram | zram-tools (`/etc/default/zramswap`) | zram-generator | zram-generator | zram-generator |
| OOM guard | `earlyoom` | `systemd-oomd` (built-in) | `earlyoom` | `earlyoom` |
| GRUB regen | `update-grub` | `grub2-mkconfig -o /boot/grub2/grub.cfg` | `grub-mkconfig -o /boot/grub/grub.cfg` | `update-bootloader` |
| Custom kernel | XanMod/Liquorix repos | XanMod COPR / `kernel-bore` | `linux-zen`/`linux-xanmod` | `kernel-bore` |
| Check pkgs | `apt-get check` | `dnf check` | `pacman -Qk` | `zypper verify` |

If the bootloader is systemd-boot (EFI), kernel params go in
`/etc/kernel/cmdline` instead of GRUB.

## 9. What NOT to do

- No cargo-cult sysctls: every value must map to an analysis finding.
- No `mitigations=off`, `nosmt`, or security-disabling flags without explicit
  approval.
- No blanket service purges; ask per service.
- No destructive storage ops (fstab rewrites, format, resize) — out of scope.
- Don't blindly set `vm.swappiness` high on disk-swap-only systems.
- Don't remove the fallback (distro) kernel when installing a custom one.
- Never store, echo, or log passwords; never run `sudo` with a password in a
  command string that gets written to disk.
- Don't chase micro-benchmarks; optimize the actual workload found in `ps`.
- If a change requires a reboot, say so — never reboot the machine unasked.