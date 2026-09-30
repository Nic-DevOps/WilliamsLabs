# Lab 11 — Firewalls & Security

**Project Name:** 11-Firewalls-Security-Lab  
**Author:** Nicholas Williams  
**Date Created:** September 22nd, 2026  
**Last Updated:** September 28th, 2026  
**Status:** In Progress — HQ firewall (FTDv) build complete (OSPF, baseline connectivity, SSH mgmt); Site A/Site B redesigned to use ASAv instead of FTDv (CML resource constraints); Site A/B builds not started; real access policy at HQ still pending

---

# 1. Objectives

- Insert a Cisco firewall at the LAN edge of each site — HQ, Site A, and Site B.
- Deploy each firewall as a routed Layer 3 hop that participates directly in OSPF, not a transparent/bridged device.
- Preserve the multi-site HSRP/routing design from Lab 6 and the OSPF design from Lab 8 wherever possible.
- Establish SSH management access to each firewall, consistent with the SSH/Net-Mgmt approach from Lab 9. **[HQ: done]**
- Apply baseline security policy without breaking existing OSPF adjacencies or inter-site connectivity.
- **Platform mix (decided 2026-09-28)**: HQ runs **FTDv** (managed via FDM); Site A and Site B run **ASAv** (managed via traditional CLI) instead of FTDv, due to CML resource constraints — see Section 3a below.

---

# 2. Network Overview

Lab 11 builds on the multi-site OSPF infrastructure from Lab 8 and the network-services/management design from Lab 9. It inserts one firewall per site inline between each site's core switch(es) and its site router.

### Path to WAN (per site)

**Core Switch(es) → Firewall → Site Router → Hub-Router01**

- **HQ**: 2 core switches, previously EtherChannel-bundled to a single site router. Firewall platform: **FTDv**.
- **Site A / Site B**: 1 core switch each, single uplink to their own site router. Firewall platform: **ASAv**.

### Placement Rationale

The site router handles inter-site routing via Hub-Router01, so placing the firewall on the core-switch side of it means every packet crossing the LAN/WAN boundary — inbound or outbound, inter-site or otherwise — passes through the firewall first. This also keeps the firewall closest to what it protects and avoids touching the site router's existing routing setup toward Hub-Router01.

### HQ EtherChannel Change

FTDv (the image behind CML's NGFWv node) does not support EtherChannel/port-channel configuration — confirmed via Cisco documentation; this is only supported on physical Firepower appliance models (e.g. 1010–3140 series), not the virtual image. As a result, HQ's EtherChannel is replaced with:

- Two independent point-to-point links on the inside: Core-SW1 ↔ Firewall and Core-SW2 ↔ Firewall (each its own routed interface, subnet, and OSPF adjacency).
- A single point-to-point link on the outside: Firewall ↔ Site Router.

This preserves independent paths from both core switches into the firewall. The firewall-to-router hop becomes a single link — a deliberate single point of failure, accepted as a tradeoff for this lab.

---

# 3. OSPF Design (Extending Lab 8)

Continuing Lab 8's design: single **Area 0**, OSPF **process 1** everywhere, `passive-interface default` with `no passive-interface` on router-to-router/firewall-facing links only, router-IDs following the **`10.<site>.255.<device>`** convention (confirmed against live device output). Firewalls join the same OSPF domain as new routed hops, regardless of platform (FTDv or ASAv).

> **Router-ID convention correction (2026-09-28):** Verified against `show ip ospf` on live devices — HQ-CoreSW1 is `10.10.255.10`, HQ-CoreSW02 is `10.10.255.11`, SiteB-CoreSW01 is `10.30.255.10`, SiteB-Router01 is `10.30.255.1`. The actual pattern is `10.<site-octet>.255.<device>` (site octet = second octet of that site's LAN `/16`: `10`=HQ, `20`=Site A, `30`=Site B; device: `.1`=router, `.10`=CoreSW01, `.11`=CoreSW02). All firewall router-IDs corrected to match.

### New Infrastructure Subnets

Carved from the existing `10.0.100.0/24` infra block. The old direct Core-SW↔Router /30s (`.0/30`, `.4/30`, `.8/30`, `.12/30`) are decommissioned and freed; Router↔ISP links (`.16/30`, `.20/30`, `.24/30`) are untouched.

| Link | Network | Device A | Device B |
|---|---|---|---|
| HQ CoreSW01 ↔ HQ-Firewall01 | `10.0.100.28/30` | HQ-CoreSW01: `.29` | HQ-Firewall01: `.30` |
| HQ CoreSW02 ↔ HQ-Firewall01 | `10.0.100.32/30` | HQ-CoreSW02: `.33` | HQ-Firewall01: `.34` |
| HQ-Firewall01 ↔ HQ-Router01 | `10.0.100.36/30` | HQ-Firewall01: `.37` | HQ-Router01: `.38` |
| SiteA CoreSW01 ↔ SiteA-Firewall01 | `10.0.100.40/30` | SiteA-CoreSW01: `.41` | SiteA-Firewall01: `.42` |
| SiteA-Firewall01 ↔ SiteA-Router01 | `10.0.100.44/30` | SiteA-Firewall01: `.45` | SiteA-Router01: `.46` |
| SiteB CoreSW01 ↔ SiteB-Firewall01 | `10.0.100.48/30` | SiteB-CoreSW01: `.49` | SiteB-Firewall01: `.50` |
| SiteB-Firewall01 ↔ SiteB-Router01 | `10.0.100.52/30` | SiteB-Firewall01: `.53` | SiteB-Router01: `.54` |

### Router IDs

Extends the `10.<site>.255.<device>` scheme; device `.20` is reserved for firewalls. Applies to both FTDv and ASAv.

| Device | Platform | Router ID |
|---|---|---|
| HQ-Firewall01 | FTDv | `10.10.255.20` ✅ live, confirmed FULL adjacencies |
| SiteA-Firewall01 | ASAv | `10.20.255.20` (planned) |
| SiteB-Firewall01 | ASAv | `10.30.255.20` (planned) |

### OSPF Configuration Notes — FTD/FDM (HQ only)

- FTD's OSPF Smart CLI object structure: `router ospf 1` → enable `router-id` line → enable `area 0` → enable `configure area 0 properties` → enable the nested `network <network-object> area 0` line, which can be duplicated (hover for `+`) to add multiple network statements. One `network` line per subnet, referencing a network object (not raw CIDR).
- FTD has no Loopback0 interface — the router ID is set directly in the OSPF process object (single process-wide setting, not per-interface, confirmed via Cisco's official FTD configuration guide).
- ASA/FTD OSPF `network` statements use a **regular subnet mask** (`255.255.255.252`), not an IOS-style wildcard mask (`0.0.0.3`).
- The `tag-interface` option on a `network` line is optional — it's just a safety guard that blocks accidental interface IP changes while that network is in the routing process. Left unset for this build.
- `log-adj-changes` is a logging-only setting (no effect on OSPF behavior) — left enabled at default (brief).
- Verify OSPF adjacencies reach `FULL` on every new firewall-facing link *before* applying any security policy — confirmed this the hard way (see Section 6 log).

### OSPF Configuration Notes — ASAv CLI (Site A / Site B, planned)

ASAv uses direct CLI syntax, much closer to the IOS-style commands already used on switches/routers — no Smart CLI object wrapper:

```
router ospf 1
 router-id 10.20.255.20
 network 10.0.100.40 255.255.255.252 area 0
 network 10.0.100.44 255.255.255.252 area 0
```

- Same regular-subnet-mask rule as FTD (not IOS wildcard mask).
- `router-id` is set directly under the `router ospf` process, same one-line approach as FTD.
- No zones/network-objects layer to configure — the `network` statement references the interface's actual subnet directly, like IOS.

---

# 3a. Platform Mix Decision — FTDv (HQ) vs. ASAv (Site A/B)

**Decided 2026-09-28.** Originally planned to run FTDv/NGFWv at all three sites. Discovered CML resource limits make running three FTDv instances simultaneously impractical — confirmed via Cisco's official FTDv KVM deployment guide that FTDv requires a **minimum of 4 vCPU / 8 GB RAM per instance**. Running 3× that is too heavy for the lab environment.

**Resolution**: Keep FTDv at HQ (already fully built and working). Use **ASAv** at Site A and Site B — a much lighter-weight Cisco firewall platform, confirmed via Cisco's official ASA Virtual Getting Started Guide:

| | FTDv (HQ) | ASAv (Site A / Site B) |
|---|---|---|
| Minimum resources | 4 vCPU / 8 GB RAM | 2 vCPU / 2 GB RAM (practically 2 vCPU / 4 GB once above 1 vCPU, per Cisco's 9.13(1)+ guidance) |
| Management | FDM (web GUI) | Traditional CLI (SSH/console), ASDM optional GUI |
| Interface config | Security Zones (assigned from the zone object's edit page) | `nameif` + `security-level` per interface |
| Policy model | Access Control Policy — **implicit default-deny**, zero rules = all transit traffic blocked | Traditional ASA model — **high-to-low security-level traffic permitted by default**, low-to-high denied by default (opposite default-posture from FTD) |
| OSPF config | Smart CLI object referencing network objects | Direct CLI `network <ip> <mask> area <id>`, same style as IOS/FTD but no object layer |
| SSH/mgmt | SSH allowed by default from any source on Mgmt0/0, `admin` account | Requires explicit `ssh <subnet> <mask> <if-name>` + local `username`/AAA config, same as traditional IOS-style setup |

**Practical implication for the Site A/B build**: because ASA's default security-level behavior already permits inside→outside traffic, Site A/B should **not** need HQ's "zero rules = total lockout" workaround (the `TEMP-Allow-All-Baseline-Test` rule) just to get baseline OSPF/ping passing — as long as the inside interface (core-switch-facing) is given a higher security-level than the outside interface (router-facing). An explicit `access-list`/`access-group` will still be needed for anything crossing low→high, and for any tightened policy either way.

---

# 4. Management — SSH Access

Reuses Lab 9's existing per-site **Net-Mgmt VLAN (VLAN 50)**, already used for SSH to switches/routers and SNMP polling into Prometheus/Grafana.

| Site | Net-Mgmt Subnet | Firewall Mgmt IP | Platform |
|---|---|---|---|
| HQ | `10.10.50.0/24` | `10.10.50.40` ✅ live, SSH confirmed working | FTDv |
| Site A | `10.20.50.0/24` | `10.20.50.40` (planned) | ASAv |
| Site B | `10.30.50.0/24` | `10.30.50.40` (planned) | ASAv |

VLAN 50 carries no DHCP scope — fully static, so addresses are assigned by hand. At HQ, `.1` in VLAN 50 is the HSRP virtual gateway, `.2`/`.3` are the core switches, and `.10`–`.49` is the network-device range (per Lab 10). `.20` and `.25` are used by the Provisioning and SNMP Monitoring VMs at HQ (DHCP01 was at `.22` until it moved to the Server VLAN as `10.10.20.22`), so HQ-Firewall01 takes `.40`, and `.40` is the standard firewall mgmt address at Site A and Site B as well. Each site's full `/16` (including VLAN 50) is already advertised into OSPF as a single summary network statement, so mgmt traffic is routable across the whole multi-site domain with no new mgmt network or special reachability path required.

Each firewall connects to its site's VLAN 50 via a dedicated interface into an access port on the core switch (HQ: CoreSW01 Gi2/3 → Firewall Mgmt0/0) — mirroring how physical Firepower appliances use a separate Management0/0 port. Site A/B (ASAv) will use the same VLAN-50-access-port pattern, though ASAv typically manages via a regular data interface rather than a dedicated Management0/0 (to be confirmed during build).

### Day-0 Bootstrap — HQ (CML NGFWv)

CML passes a JSON day-0 config to the NGFWv node on first boot. The `IPv4*` fields configure the Management0/0 interface, so they carry the VLAN 50 mgmt addressing above. `ManageLocally: Yes` enables local management via FDM, and the FMC fields stay blank.

```json
{
    "EULA": "accept",
    "Hostname": "HQ-Firewall01",
    "AdminPassword": "<ADMIN_PASSWORD>",
    "FirewallMode": "routed",
    "DNS1": "10.10.50.50",
    "DNS2": "",
    "DNS3": "",
    "IPv4Mode": "manual",
    "IPv4Addr": "10.10.50.40",
    "IPv4Mask": "255.255.255.0",
    "IPv4Gw": "10.10.50.1",
    "IPv6Mode": "disabled",
    "IPv6Addr": "",
    "IPv6Mask": "",
    "IPv6Gw": "",
    "FmcIp": "",
    "FmcRegKey": "",
    "FmcNatId": "",
    "ManageLocally": "Yes"
}
```

Field | Value | Reason
---|---|---
`Hostname` | HQ-Firewall01 | Matches the device naming used in NetBox and the OSPF tables
`FirewallMode` | routed | The firewall is a Layer 3 OSPF hop, not transparent
`DNS1` | 10.10.50.50 | AD-01 (Lab 10), the internal DNS server
`IPv4Addr` / `IPv4Mask` | 10.10.50.40 / 255.255.255.0 | Firewall mgmt IP in HQ VLAN 50
`IPv4Gw` | 10.10.50.1 | HQ VLAN 50 HSRP virtual gateway (core switches are .2/.3), so mgmt survives a core switch failure
`ManageLocally` | Yes | Local FDM management

The template's default `AdminPassword` is replaced with a unique password before first boot. The real password is kept out of this repo. This JSON format is specific to FTDv/NGFWv — the Site A/B ASAv builds are configured by CLI instead (see SSH Auth below).

### SSH Auth — ✅ HQ (FTDv) confirmed working

Unlike IOS, FTD's Management interface allows SSH **by default, from any source IP**, using the `admin` account and whatever password was set during the initial setup wizard — no separate `username`/`crypto key`/`line vty` config needed (confirmed via Cisco's official FDM System Settings guide). Access is controlled by Device > System Settings > Management Access > Management Interface tab, which lists allowed protocols (SSH/HTTPS) and source networks — defaults to allowing SSH from anywhere unless explicitly restricted.

Successfully connected via `ssh admin@10.10.50.40` from the management network.

### SSH Auth — Site A / Site B (ASAv, planned)

ASAv does **not** allow SSH by default the way FTD's Mgmt interface does — it needs explicit CLI configuration, closer to the IOS pattern already used on switches/routers:

```
username admin password <pw> privilege 15
aaa authentication ssh console LOCAL
ssh 10.20.50.0 255.255.255.0 <mgmt-if-nameif>
ssh timeout 30
crypto key generate rsa modulus 2048
```

- **Future hardening item**: restrict the Management Access List (FTD) / `ssh` source statement (ASA) to VLAN 50's subnet only — HQ is currently open to any source, not done yet, low priority while still in build/test mode.
- Extend Prometheus/Grafana monitoring to the firewalls once FTDv's SNMP/metrics export options are confirmed (see Open Questions). ASAv supports traditional `snmp-server` CLI config, same as IOS — likely simpler to integrate than FTDv.

---

# 5. Open Questions / To Decide

- **Site A router-ID migration (to do before the Site A build)**: SiteA-Router01 (`10.255.2.1`) and SiteA-CoreSW01 (`10.255.2.10`) still use the original Lab 8 scheme. Migrate them to `10.20.255.1` and `10.20.255.10` so Site A matches the `10.<site>.255.<device>` convention used by HQ, Site B, and the planned SiteA-Firewall01 (`10.20.255.20`). See the Lab 8 update note.

- **Base policy (HQ/FTDv)**: default-deny with explicit allow rules, or start permissive and tighten? *(Currently running a temporary allow-all rule — see Section 6 log. Real policy design still pending — this is the next major piece of work.)*
- **Base policy (Site A/B, ASAv)**: default security-level behavior (high→low permit) may avoid needing a temporary allow-all rule, but an explicit ACL will still be needed for low→high traffic and for any tightened policy — to be confirmed during build.
- **Management platform**: local firewall management (FDM) or centralized (FMC-style)? *(Resolved: using FDM locally for HQ's FTDv; Site A/B ASAv managed via CLI, ASDM optional.)*
- **Logging/monitoring**: FTDv's SNMP/metrics setup differs from IOS `snmp-server community` — not yet investigated. ASAv likely closer to IOS-native SNMP.
- **Management Access List hardening**: restrict SSH/HTTPS source to VLAN 50 only instead of default "any" — not done yet (HQ); Site A/B `ssh` source statement should be scoped to VLAN 50 from the start.

---

# 6. Build Log — HQ (chronological)

1. **Cabling**: Firewall connected inline at HQ — mgmt link (CoreSW01 Gi2/3 → Firewall Mgmt0/0, VLAN 50), two inside links (CoreSW01 Gi2/2 → Firewall Eth0/2, CoreSW02 Gi2/1 → Firewall Eth0/1), one outside link (Firewall Eth0/0 → Router01 Gi0/3).
2. **Firewall interfaces configured** via FDM: Eth0/0 (outside) `10.0.100.37/30`, Eth0/1 (inside-coresw02) `10.0.100.34/30`, Eth0/2 (inside-coresw01) `10.0.100.30/30`, Mgmt0/0 `10.10.50.40/24`.
3. **Gotcha**: CoreSW02's firewall-facing port (Gi2/1) initially came up as a Layer 2 access port still in VLAN 50 (leftover from mgmt-link config copy/paste) — required `no switchport` to convert to routed before it would take an IP.
4. **Switch/router-side OSPF** configured and verified up/up: CoreSW01 Gi2/2, CoreSW02 Gi2/1, Router01 Gi0/3 — all with `network ... area 0` (wildcard mask) and `no passive-interface`.
5. **Firewall-side OSPF** configured via Smart CLI object: process 1, router-id `10.10.255.20`, area 0, three network objects (`NET-HQ-FW-CoreSW01`, `NET-HQ-FW-CoreSW02`, `NET-HQ-FW-Router01`) each in a `network ... area 0` line. Deployed successfully.
6. **OSPF verified FULL on all three firewall-facing links** — confirmed via `show ospf neighbor` (firewall) and `show ip ospf neighbor` (CoreSW01, CoreSW02, Router01). All three show FULL/BDR or FULL/DR as expected.
7. **Decommissioned old direct Core-SW↔Router links** (the pre-firewall EtherChannel-era paths) that were still up and bypassing the firewall entirely — shut down + removed IP + removed OSPF network statement on CoreSW01, CoreSW02, and both corresponding interfaces on Router01. Done via console access (not the live SSH session) to avoid self-lockout, one device at a time.
8. **SSH to Router01 broke** after decommissioning the old links — root-caused to the firewall's Access Control Policy having **zero rules configured**, so the implicit default-deny blocked all transit traffic (only self-originated traffic from the firewall itself, e.g. its own pings, was unaffected). Security zones (`inside_zone`, `outside_zone`) were already correctly populated with the right interfaces — the issue was purely the missing access rule, not zone membership.
9. **Fix applied**: added a temporary rule `TEMP-Allow-All-Baseline-Test` (Source Zone: Any → Destination Zone: Any, Action: Allow) to restore full pass-through while baseline connectivity is being validated. **This rule must be replaced with a real default-deny + explicit-allow policy in step 7 of the build order below — it is not a permanent fix.**
10. **Confirmed fixed**: `show ip ospf neighbor` on Router01 now shows exactly two neighbors — the firewall (`10.10.255.20`) and Hub-Router01 (`10.0.255.1`, untouched) — the two stale direct adjacencies to CoreSW01/02 are gone. Ping and SSH to Router01 restored via the firewall path.
11. **SSH to the firewall's own management interface confirmed working** — `10.10.50.40`, default `admin` account, no extra config needed (FTD allows SSH to Mgmt0/0 by default from any source, unlike IOS's require-explicit-config approach).
12. **Design change (2026-09-28)**: Realized CML cannot run three FTDv instances simultaneously (4 vCPU/8GB minimum each). Decided to keep FTDv at HQ and switch Site A/Site B to **ASAv** instead — see Section 3a for full rationale and platform comparison.

**Current state**: HQ firewall is fully inline, OSPF-adjacent on all links, old bypass paths removed, baseline connectivity (ping/SSH) confirmed working through the firewall under the temporary allow-all rule, and SSH management access to the firewall itself confirmed working. **Not yet done at HQ**: full inter-site (Site A/B) connectivity retest, and replacing the temporary rule with real policy. **Site A/Site B**: not yet started, now planned as ASAv builds.

---

# 7. Planned Build Order (status)

1. Cabling — **HQ: done.** Site A/B: not started.
2. Firewall mgmt access (console → static mgmt IP → SSH) — **HQ: done.** Site A/B: not started (ASAv CLI-based SSH setup, see Section 4).
3. Firewall interface configuration — **HQ: done** (FDM). Site A/B: not started (ASAv `nameif`/`security-level` CLI, see Section 3a).
4. OSPF on firewall-facing links (switches/router + firewall) — **HQ: done, verified FULL.** Site A/B: not started (ASAv direct CLI, see Section 3 OSPF notes).
5. Verify OSPF neighbors FULL before any policy — **HQ: done.** Site A/B: pending build.
6. Re-verify Lab 6/Lab 8 baseline end-to-end with firewall passing all traffic — **HQ: baseline ping/SSH confirmed via temporary allow-all rule; full inter-site (Site A/B) retest still outstanding.**
7. Apply baseline security policy (start restrictive, one site at a time) — **HQ: not started. Currently running temporary allow-all rule as a stand-in — needs replacing. This is the next major piece of work.** Site A/B: ASAv's default security-level behavior may reduce urgency here, but explicit ACLs still needed — see Section 3a.
8. Retest inter-site connectivity and routing-failure scenarios with firewalls in place — **Not started.**
9. Document final ruleset and all changes from baseline — **Ongoing (this doc).**

**Site A and Site B builds have not started** — everything above is HQ-only so far. Both will use **ASAv** instead of the originally planned FTDv.

---

# 8. Future Improvements

| # | Improvement | Description |
|---|---|---|
| 1 | FMC Centralized Management | Move from local/FDM management to FMC if the CML environment supports it, for a more realistic enterprise management model (HQ/FTDv only — not applicable to ASAv). |
| 2 | OSPF Authentication | Add MD5/SHA OSPF authentication at the firewall-facing links, following up on the OSPF security risks flagged in Lab 8. |
| 3 | HQ Outside Redundancy | Explore options (dynamic routing-based failover, a second physical firewall) to remove the single point of failure on the firewall-to-router link at HQ. |
| 4 | Firewall Monitoring | Integrate FTDv/ASAv health/traffic metrics into the existing Prometheus/Grafana stack. |
| 5 | Automation | Use Ansible to standardize firewall policy deployment across sites (would need separate playbooks/modules for FTD vs. ASA given the differing management models). |
| 6 | Mgmt Access Hardening | Restrict each firewall's management access (FTD Management Access List / ASA `ssh` source statement) to VLAN 50 only instead of the current default "any source." |
| 7 | ASDM for Site A/B | Optionally deploy ASDM for a GUI management option on the ASAv firewalls, if desired alongside CLI. |

---

# Notes

- HQ interface naming on the FTDv/FDM side uses `EthernetX/X`, not `GigabitEthernetX/X` like the IOS core switches/routers. ASAv interface naming (Site A/B, to be confirmed) is typically `GigabitEthernetX/X`, closer to IOS.
- FTD's zone-to-interface assignment happens on the **Security Zone object's** edit screen (Objects > Security Zones), not from the interface's own edit page — opposite of what might be assumed coming from other platforms. ASAv has no zone concept at all — policy is tied directly to `nameif`/`security-level` and interface-applied ACLs.
- A firewall with zero access control rules on FTD blocks ALL transit traffic by default (implicit deny) — this is different from a router's default-permit behavior and is easy to mistake for a routing problem when troubleshooting. **ASAv is the opposite by default**: traffic from a higher security-level interface to a lower one is permitted without any ACL; only low→high traffic is denied by default. This is an important behavioral difference to keep in mind switching from the HQ (FTDv) build to Site A/B (ASAv).
- FDM's Deploy action persists configuration — no `write memory` equivalent needed unless working directly at the underlying FTD CLI outside of FDM. **ASAv still uses traditional `write memory`/`copy running-config startup-config`** to persist CLI changes — don't assume FDM's auto-persist behavior carries over.
- FTD's Management interface allows SSH by default from any source IP, using the `admin` account and the password set during initial setup — no separate SSH-enablement config needed, unlike IOS. **ASAv requires explicit SSH enablement** (`username`, `aaa authentication ssh console LOCAL`, `ssh <subnet> <mask> <nameif>`, `crypto key generate rsa`) — same pattern as IOS devices in this lab.
- **Platform-mix rationale**: CML could not run three FTDv instances simultaneously (4 vCPU/8GB minimum each). ASAv's much lighter footprint (2 vCPU/2-4GB) let the lab keep all three sites running concurrently while preserving FTDv/FDM experience at HQ for the more "modern NGFW" workflow.

<!-- Images live in the shared assets folder: ../assets/11-Firewalls-Security-Lab/ -->
