**Project Name:** 06-MultiSite-Static-Routing-Lab
**Version:** 1.0
**Author:** Nicholas Williams
**Date Created:** August 12th 2026
**Last Updated:** August 12th 2026
**Status:** In Progress

# 1. Objective

Build a multi-site enterprise network using routers, Layer 2 switches, IPv4 addressing, point-to-point WAN links, and static routing.

## Goals

* Configure three separate network sites.
* Configure LAN addressing for each site.
* Configure point-to-point routed WAN links.
* Configure static routes between sites.
* Configure default gateways for end devices.
* Verify directly connected and static routes.
* Verify end-to-end connectivity between sites.
* Use `ping` and `traceroute` to identify packet paths.
* Analyze routing tables using `show ip route`.
* Troubleshoot common static-routing failures.
* Understand the limitations of static routing in a multi-site environment.

---

# 2. Network Topology

## Topology Type

This topology uses three routers connected through a triangular WAN topology.

Each router provides connectivity to a separate LAN. Static routes are manually configured on each router to allow traffic to reach the remote LANs.

## Advantages

* Simple to understand and configure.
* No dynamic routing protocol is required.
* Provides predictable routing behavior.
* Useful for learning how routers make forwarding decisions.
* Appropriate for small and relatively stable networks.

## Limitations

* Routes must be manually configured.
* Network changes require manual updates.
* Configuration becomes increasingly complex as the number of networks grows.
* Static routes do not automatically adapt to link failures.
* Troubleshooting becomes more difficult as the topology expands.

---

# 3. Physical Layout

```text
                         R1
                       /    \
                      /      \
                     /        \
                    R2--------R3
                    |          |
                   SW2        SW3
                    |          |
                  Users      Users
                  
                    |
                   SW1
                    |
                  Users
```

## Devices

| Device | Model                | Purpose                     |
| ------ | -------------------- | --------------------------- |
| R1     | Cisco Router         | Site 1 Router               |
| R2     | Cisco Router         | Site 2 Router               |
| R3     | Cisco Router         | Site 3 Router               |
| SW1    | Cisco Layer 2 Switch | Site 1 Access Switch        |
| SW2    | Cisco Layer 2 Switch | Site 2 Access Switch        |
| SW3    | Cisco Layer 2 Switch | Site 3 Access Switch        |
| PC1    | End Device           | Site 1 Connectivity Testing |
| PC2    | End Device           | Site 2 Connectivity Testing |
| PC3    | End Device           | Site 3 Connectivity Testing |

---

# 4. Network Addressing

## LAN Assignments

| Site   | Network      | Router IP | Purpose    |
| ------ | ------------ | --------- | ---------- |
| Site 1 | 10.0.10.0/24 | 10.0.10.1 | Site 1 LAN |
| Site 2 | 10.0.20.0/24 | 10.0.20.1 | Site 2 LAN |
| Site 3 | 10.0.30.0/24 | 10.0.30.1 | Site 3 LAN |

## WAN Assignments

| Connection | Network       | Router A   | Router B    |
| ---------- | ------------- | ---------- | ----------- |
| R1 ↔ R2    | 10.0.100.0/30 | 10.0.100.1 | 10.0.100.2  |
| R1 ↔ R3    | 10.0.100.4/30 | 10.0.100.5 | 10.0.100.6  |
| R2 ↔ R3    | 10.0.100.8/30 | 10.0.100.9 | 10.0.100.10 |

---

## End Device Addressing

| Device | Network | IP Address    | Default Gateway |
| ------ | ------- | ------------- | --------------- |
| PC1    | Site 1  | 10.0.10.10/24 | 10.0.10.1       |
| PC2    | Site 2  | 10.0.20.10/24 | 10.0.20.1       |
| PC3    | Site 3  | 10.0.30.10/24 | 10.0.30.1       |

---

# 5. Routing Design

Each router is directly connected to its local LAN and to two WAN links.

Static routes are used to reach remote LAN networks.

| Router | Destination  | Next Hop    |
| ------ | ------------ | ----------- |
| R1     | 10.0.20.0/24 | 10.0.100.2  |
| R1     | 10.0.30.0/24 | 10.0.100.6  |
| R2     | 10.0.10.0/24 | 10.0.100.1  |
| R2     | 10.0.30.0/24 | 10.0.100.10 |
| R3     | 10.0.10.0/24 | 10.0.100.5  |
| R3     | 10.0.20.0/24 | 10.0.100.9  |

The routers will therefore contain three types of relevant routes:

* **Connected routes** — networks directly attached to the router.
* **Local routes** — the router's own interface addresses.
* **Static routes** — manually configured routes to remote networks.

---

# 6. Configuration Order

The following order was used to configure the routers, LANs, WAN links, and static routes.

## 1. Configure Basic Router Settings

Set the hostname and disable DNS lookup.

### R1

```cisco
hostname R1
no ip domain-lookup
```

### R2

```cisco
hostname R2
no ip domain-lookup
```

### R3

```cisco
hostname R3
no ip domain-lookup
```

---

## 2. Configure Site 1 LAN

Configure the LAN-facing interface on R1.

```cisco
interface GigabitEthernet0/0
ip address 10.0.10.1 255.255.255.0
no shutdown
```

Verify:

```cisco
show ip interface brief
```

---

## 3. Configure Site 2 LAN

Configure the LAN-facing interface on R2.

```cisco
interface GigabitEthernet0/0
ip address 10.0.20.1 255.255.255.0
no shutdown
```

Verify:

```cisco
show ip interface brief
```

---

## 4. Configure Site 3 LAN

Configure the LAN-facing interface on R3.

```cisco
interface GigabitEthernet0/0
ip address 10.0.30.1 255.255.255.0
no shutdown
```

Verify:

```cisco
show ip interface brief
```

---

## 5. Configure R1 ↔ R2 WAN Link

### R1

```cisco
interface GigabitEthernet0/1
ip address 10.0.100.1 255.255.255.252
no shutdown
```

### R2

```cisco
interface GigabitEthernet0/1
ip address 10.0.100.2 255.255.255.252
no shutdown
```

Verify:

```cisco
show ip interface brief
```

Test connectivity:

```cisco
R1# ping 10.0.100.2
```

---

## 6. Configure R1 ↔ R3 WAN Link

### R1

```cisco
interface GigabitEthernet0/2
ip address 10.0.100.5 255.255.255.252
no shutdown
```

### R3

```cisco
interface GigabitEthernet0/1
ip address 10.0.100.6 255.255.255.252
no shutdown
```

Verify:

```cisco
show ip interface brief
```

Test connectivity:

```cisco
R1# ping 10.0.100.6
```

---

## 7. Configure R2 ↔ R3 WAN Link

### R2

```cisco
interface GigabitEthernet0/2
ip address 10.0.100.9 255.255.255.252
no shutdown
```

### R3

```cisco
interface GigabitEthernet0/2
ip address 10.0.100.10 255.255.255.252
no shutdown
```

Verify:

```cisco
show ip interface brief
```

Test connectivity:

```cisco
R2# ping 10.0.100.10
```

---

## 8. Verify Directly Connected Routes

Before configuring static routes, examine the routing tables.

```cisco
show ip route
```

R1 should have directly connected routes similar to:

```text
C    10.0.10.0/24
C    10.0.100.0/30
C    10.0.100.4/30
```

R2 should have:

```text
C    10.0.20.0/24
C    10.0.100.0/30
C    10.0.100.8/30
```

R3 should have:

```text
C    10.0.30.0/24
C    10.0.100.4/30
C    10.0.100.8/30
```

At this point, the routers know about their directly connected networks but do not yet know how to reach the remote LANs.

---

## 9. Configure Static Routes on R1

R1 requires routes to the Site 2 and Site 3 LANs.

```cisco
ip route 10.0.20.0 255.255.255.0 10.0.100.2
ip route 10.0.30.0 255.255.255.0 10.0.100.6
```

Verify:

```cisco
show ip route
```

The routes should appear as:

```text
S    10.0.20.0/24 [1/0] via 10.0.100.2
S    10.0.30.0/24 [1/0] via 10.0.100.6
```

---

## 10. Configure Static Routes on R2

R2 requires routes to the Site 1 and Site 3 LANs.

```cisco
ip route 10.0.10.0 255.255.255.0 10.0.100.1
ip route 10.0.30.0 255.255.255.0 10.0.100.10
```

Verify:

```cisco
show ip route
```

---

## 11. Configure Static Routes on R3

R3 requires routes to the Site 1 and Site 2 LANs.

```cisco
ip route 10.0.10.0 255.255.255.0 10.0.100.5
ip route 10.0.20.0 255.255.255.0 10.0.100.9
```

Verify:

```cisco
show ip route
```

---

## 12. Configure End Devices

Assign the appropriate static addressing to each PC.

### PC1

```text
IP Address:      10.0.10.10
Subnet Mask:     255.255.255.0
Default Gateway: 10.0.10.1
```

### PC2

```text
IP Address:      10.0.20.10
Subnet Mask:     255.255.255.0
Default Gateway: 10.0.20.1
```

### PC3

```text
IP Address:      10.0.30.10
Subnet Mask:     255.255.255.0
Default Gateway: 10.0.30.1
```

---

# 7. Verify Configuration and Save Changes

## Verify Interface Status

On each router:

```cisco
show ip interface brief
```

All required interfaces should be:

```text
Status: up
Protocol: up
```

---

## Verify Routing Tables

```cisco
show ip route
```

Confirm that each router contains:

* Connected routes
* Local routes
* Static routes

Static routes should be identified by:

```text
S
```

---

## Test WAN Connectivity

### R1

```cisco
ping 10.0.100.2
ping 10.0.100.6
```

### R2

```cisco
ping 10.0.100.1
ping 10.0.100.10
```

### R3

```cisco
ping 10.0.100.5
ping 10.0.100.9
```

---

## Test LAN Gateway Connectivity

### PC1 → Site 1 Gateway

```text
ping 10.0.10.1
```

### PC2 → Site 2 Gateway

```text
ping 10.0.20.1
```

### PC3 → Site 3 Gateway

```text
ping 10.0.30.1
```

---

## Test Inter-Site Connectivity

### Site 1 → Site 2

```text
PC1 → 10.0.20.10
```

### Site 1 → Site 3

```text
PC1 → 10.0.30.10
```

### Site 2 → Site 1

```text
PC2 → 10.0.10.10
```

### Site 2 → Site 3

```text
PC2 → 10.0.30.10
```

### Site 3 → Site 1

```text
PC3 → 10.0.10.10
```

### Site 3 → Site 2

```text
PC3 → 10.0.20.10
```

---

# 8. Trace Packet Paths

Use `traceroute` from the routers:

```cisco
traceroute 10.0.30.10
```

Or from end devices:

```text
tracert 10.0.30.10
```

For example, traffic from Site 1 to Site 3 should follow:

```text
PC1
 ↓
R1
 ↓
R3
 ↓
PC3
```

Traffic from Site 1 to Site 2 should follow:

```text
PC1
 ↓
R1
 ↓
R2
 ↓
PC2
```

This demonstrates how the static routing table determines the next hop for a packet.

---

# 9. Static Route Concepts

## Next-Hop Static Route

The preferred configuration in this lab uses the next-hop address.

Example:

```cisco
ip route 10.0.20.0 255.255.255.0 10.0.100.2
```

This tells R1:

```text
To reach 10.0.20.0/24,
send the packet to 10.0.100.2.
```

---

## Exit-Interface Static Route

A static route can also specify an exit interface.

```cisco
ip route 10.0.20.0 255.255.255.0 GigabitEthernet0/1
```

This tells the router which interface to use to forward the packet.

---

## Default Route

A default route is used when no more specific route exists.

```cisco
ip route 0.0.0.0 0.0.0.0 <next-hop>
```

The default route appears in the routing table as:

```text
S*
```

A default route is particularly useful for networks where one router acts as an exit point toward an upstream network or the Internet.

---

# 10. Troubleshooting Exercises

## Exercise 1 — Remove a Static Route

Remove R1's route to Site 3:

```cisco
no ip route 10.0.30.0 255.255.255.0 10.0.100.6
```

Test:

```text
PC1 → PC3
```

Use:

```cisco
show ip route
```

Determine why the connection fails.

Restore the route:

```cisco
ip route 10.0.30.0 255.255.255.0 10.0.100.6
```

---

## Exercise 2 — Incorrect Next Hop

Change one static route to use an incorrect next-hop address.

Example:

```cisco
ip route 10.0.30.0 255.255.255.0 10.0.100.2
```

Test connectivity and determine why the route does not work as expected.

Use:

```cisco
show ip route
ping
traceroute
```

Restore the correct next hop afterward.

---

## Exercise 3 — Incorrect Default Gateway

Change PC1's default gateway to an incorrect address.

Test:

```text
PC1 → 10.0.10.1
PC1 → 10.0.20.10
```

Determine why communication with remote networks fails.

Restore:

```text
10.0.10.1
```

---

## Exercise 4 — Shut Down a WAN Interface

Administratively shut down one WAN interface.

Example:

```cisco
interface GigabitEthernet0/1
shutdown
```

Observe:

```cisco
show ip interface brief
show ip route
```

Test connectivity afterward.

Restore the interface:

```cisco
no shutdown
```

---

# 11. Questions

1. Why can R1 reach R2's WAN interface without a static route?

2. Why can't R1 initially reach the `10.0.20.0/24` network?

3. What does the `S` designation represent in `show ip route`?

4. What does the `S*` designation represent?

5. What happens when a router receives a packet for a network that does not exist in its routing table?

6. Why is a return route required for successful two-way communication?

7. What is the difference between a next-hop static route and an exit-interface static route?

8. Why do static routes become difficult to manage as a network grows?

9. What happens to the static route when its next-hop interface becomes unavailable?

10. How would a dynamic routing protocol improve this network?

11. What advantage does the triangular R1-R2-R3 topology provide?

12. If the R1-R3 link fails, can traffic from Site 1 still reach Site 3 with the current static routing configuration? Explain why or why not.

---

# 12. Future Improvements

| Improvement            | Description                                                                               |
| ---------------------- | ----------------------------------------------------------------------------------------- |
| OSPF                   | Replace manually configured routes with dynamic route exchange between the three routers. |
| Floating Static Routes | Configure backup static routes with a higher administrative distance.                     |
| DHCP                   | Provide automatic IP addressing to hosts at each site.                                    |
| DNS                    | Add centralized or distributed name resolution.                                           |
| WAN Redundancy         | Configure alternate WAN paths between sites.                                              |
| ACLs                   | Control traffic between sites using access control lists.                                 |
| NAT                    | Provide Internet connectivity through an edge router.                                     |
| Monitoring             | Add logging, SNMP, or network monitoring to observe WAN and routing status.               |

---

