# Lab 11 — Network Security: Firewall, ACLs, and NAT

Project Name: 11-Network-Security-Firewall-Lab
Author: Nicholas Williams
Date Created: September 26th, 2026
Last Updated: September 26th, 2026
Status: In Progress

# 1. Overview

Up to Lab 10, every VLAN and site in WilliamsLabs can reach every other one: inter-VLAN routing on the HQ core switches and OSPF between sites move traffic freely, with no policy on what is allowed. This lab adds security controls to that flat routed network. A firewall is placed in front of the HQ server VLAN so that AD-01 (Lab 10) only accepts the ports Active Directory actually needs, access control lists (ACLs) restrict traffic between user, guest, and management VLANs, and NAT at the hub router gives internal hosts controlled internet access.

TODO: Expand once the firewall platform and placement are finalized.

# 2. Environment

Component | Value
---|---
Firewall | TODO (platform, version, where it runs)
Protected segment | HQ server VLAN, 10.10.50.0/24
Protected hosts | AD-01 (10.10.50.50), DHCP server (Lab 09)
Test client | Windows client on the HQ user VLAN (VLAN 10), 10.10.10.100/24
Edge / NAT | TODO (hub router, outside interface)

Addressing follows the lab's `10.<site>.<vlan>.<host>` convention.

# 3. Objectives

- [ ] Choose and deploy the firewall, and document where it sits in the topology
- [ ] Place the firewall in front of the HQ server VLAN (10.10.50.0/24)
- [ ] Build a default-deny rule set for the server VLAN, allowing only required services
- [ ] Apply ACLs between VLANs (e.g. isolate Guest from internal VLANs, restrict access to Net-Mgmt)
- [ ] Restrict SSH/SNMP management access to the management VLAN
- [ ] Configure NAT/PAT at the hub router for internet access
- [ ] Enable logging for denied traffic
- [ ] Verify allowed traffic still works (domain logon, DNS, DHCP relay, GPO) and blocked traffic is dropped

# 4. Topology

TODO: Add topology diagram.

<!-- Images live in the shared assets folder: ../assets/11-Network-Security-Firewall-Lab/ -->

# 5. Steps

## 5.1 Firewall Deployment

TODO: Install and base configuration (interfaces, zones, management access).

## 5.2 Server VLAN Rule Set

Starting point for the rule set, based on the ports AD-01 needs (from Lab 10):

Service | Protocol / Port | Source
---|---|---
DNS | TCP/UDP 53 | Internal client VLANs
Kerberos | TCP/UDP 88 | Internal client VLANs
Kerberos password change | TCP/UDP 464 | Internal client VLANs
NTP (W32Time) | UDP 123 | Internal client VLANs
RPC endpoint mapper | TCP 135 | Internal client VLANs
LDAP | TCP/UDP 389 | Internal client VLANs
SMB (SYSVOL/NETLOGON) | TCP 445 | Internal client VLANs
Global Catalog | TCP 3268 | Internal client VLANs
RPC dynamic range | TCP 49152–65535 | Internal client VLANs
DHCP relay | UDP 67 | Core switch / router relay addresses
Everything else | Any | Deny and log

TODO: Refine sources per VLAN (e.g. Guest gets no access to the server VLAN).

## 5.3 Inter-VLAN ACLs

TODO: ACLs on the core switch SVIs and site routers.

## 5.4 Management Plane Hardening

TODO: Limit VTY (SSH) and SNMP access to the management VLAN with ACLs.

## 5.5 NAT

TODO: NAT/PAT configuration at the hub router.

# 6. Verification and Testing

- [ ] The client on VLAN 10 still logs on to the domain, resolves DNS, and receives the Corp Users - Baseline GPO
- [ ] DHCP relay still delivers leases to client VLANs at all sites
- [ ] Ports not in the rule set are blocked from the client to AD-01 (e.g. `Test-NetConnection 10.10.50.50 -Port 3389`)
- [ ] Guest VLAN cannot reach internal VLANs
- [ ] SSH to network devices works only from the management VLAN
- [ ] Internal hosts reach the internet through NAT
- [ ] Denied traffic appears in the firewall logs

TODO: Commands and results.

# 7. Summary and Future Improvements

TODO.
