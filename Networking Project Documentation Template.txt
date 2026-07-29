# Network Project Documentation

> **Project Name:**  
> **Version:** 1.0  
> **Author:**  Nicholas Williams
> **Date Created:**  July 29th 2026
> **Last Updated:**  
> **Status:** Planning / In Progress / Complete

---

# 1. Project Overview

## Objective

Describe what this project is intended to accomplish.

### Example

- Build a multi-site enterprise network
- Implement VLAN segmentation
- Configure inter-VLAN routing
- Provide secure WAN connectivity
- Enable centralized DHCP

---

# 2. Learning Objectives

- [ ]
- [ ]
- [ ]
- [ ]

Example:

- Learn static routing
- Configure Layer 3 switches
- Understand trunking
- Practice subnetting
- Deploy DHCP relay

---

# 3. Network Requirements

## Functional Requirements

- Users can communicate within VLANs
- Internet connectivity
- Remote site connectivity
- DHCP for clients
- DNS resolution

## Non-functional Requirements

- Easy to expand
- Secure
- Fault tolerant
- Easy to troubleshoot

---

# 4. Network Topology

## Topology Type

- Star
- Extended Star
- Mesh
- Partial Mesh
- Ring
- Hybrid

### Why this topology?

Explain why it was chosen.

---

## Advantages

-

-

-

## Drawbacks / Limitations

-

-

-

Examples

- Single point of failure at core switch
- Router failure disconnects branch office
- No redundancy
- Static routing requires manual updates

---

# 5. Physical Layout

## Sites

| Site | Purpose |
|-------|----------|
| HQ | Main Office |
| Branch A | Sales |
| Branch B | Warehouse |

---

## Devices

| Device | Model | Purpose |
|----------|--------|---------|
| R1 | Cisco 2911 | WAN Router |
| SW1 | Cisco 3560 | Layer 3 Switch |
| SW2 | Cisco 2960 | Access Switch |

---

# 6. Logical Network Design

## VLANs

| VLAN | Name | Subnet | Gateway |
|-------|------|---------|----------|
| 10 | Management | | |
| 20 | Servers | | |
| 30 | Users | | |
| 40 | Voice | | |

---

## IP Addressing Plan

| Network | CIDR | Gateway |
|----------|------|----------|
| | | |
| | | |
| | | |

---

## WAN Links

| Connection | Network |
|------------|---------|
| HQ ↔ Branch A | |
| HQ ↔ Branch B | |

---

# 7. Routing Design

## Routing Method

- Static
- OSPF
- EIGRP
- RIP
- BGP

Why?

---

## Routing Table Summary

| Device | Routes |
|---------|---------|
| R1 | |
| SW1 | |

---

# 8. Layer 2 Design

## Access Ports

| Interface | VLAN | Device |
|------------|------|---------|
| | | |

---

## Trunk Links

| Interface | Native VLAN | Allowed VLANs |
|------------|--------------|---------------|
| | | |

---

## STP

Mode:

Root Bridge:

Notes:

---

# 9. Layer 3 Design

SVIs

| VLAN | Interface | IP |
|-------|-----------|----|
| | | |

---

Default Routes

```
ip route ...
```

---

Static Routes

```
ip route ...
```

---

Dynamic Routing Configuration

```
router ospf 1
```

---

# 10. Services

## DHCP

Server:

Pools:

Excluded Addresses:

Relay (IP Helper):

---

## DNS

Server

Purpose

---

## NTP

Server

---

## Syslog

Server

---

## SNMP

Community

Version

---

# 11. Security

## Device Security

- Enable secret
- Console password
- SSH only
- Disable Telnet

---

## VLAN Security

- Native VLAN changed
- Unused ports shutdown
- Port Security

---

## ACLs

| ACL | Purpose |
|------|----------|
| | |

---

## Other Security

-

-

-

---

# 12. Configuration Checklist

## Basic Configuration

- [ ] Hostname
- [ ] Domain Name
- [ ] Enable Secret
- [ ] SSH
- [ ] Banner
- [ ] Save Config

---

## Interfaces

- [ ] Descriptions
- [ ] IP Addresses
- [ ] Duplex
- [ ] Speed
- [ ] Shutdown removed

---

## Switching

- [ ] VLANs created
- [ ] Trunks configured
- [ ] Access ports assigned
- [ ] STP verified

---

## Routing

- [ ] Default routes
- [ ] Static routes
- [ ] Dynamic routing
- [ ] Routing table verified

---

## Services

- [ ] DHCP
- [ ] DNS
- [ ] NTP
- [ ] Syslog

---

## Security

- [ ] ACLs
- [ ] SSH
- [ ] Passwords
- [ ] Port Security

---

## Verification

- [ ] Ping
- [ ] Traceroute
- [ ] show ip route
- [ ] show vlan
- [ ] show interfaces trunk
- [ ] show spanning-tree
- [ ] show ip interface brief

---

# 13. Testing

## Connectivity Tests

| Test | Expected | Result |
|-------|----------|---------|
| PC1 → Gateway | Success | |
| PC1 → Server | Success | |
| Site A → Site B | Success | |

---

## Failure Tests

Disconnect:

Expected Result:

Actual Result:

---

# 14. Troubleshooting Log

| Issue | Cause | Resolution |
|--------|-------|------------|
| | | |

---

# 15. Lessons Learned

## What Went Well

-

-

-

## Challenges

-

-

-

## How I Solved Them

-

-

-

## What I Would Improve

-

-

-

---

# 16. Scalability

Future Improvements

- OSPF
- HSRP
- EtherChannel
- Redundant Core
- Firewall
- VPN
- IPv6
- Wireless
- Network Monitoring

---

# 17. Commands Used

```
show ip route
show vlan brief
show interfaces trunk
show ip interface brief
show running-config
show startup-config
show spanning-tree
show cdp neighbors
show arp
show mac address-table
ping
traceroute
```

---

# 18. File Information

Packet Tracer File:

Configuration Backups:

Network Diagram:

Screenshots:

---

# 19. Final Review

## Project Summary

Write a brief overview of what was accomplished.

---

## Skills Practiced

- VLANs
- Trunking
- Layer 3 Switching
- Static Routing
- OSPF
- DHCP
- ACLs
- WAN Design
- Network Documentation
- Troubleshooting


# 20. References

Cisco Documentation

RFCs

Books

YouTube Videos

Other Resources