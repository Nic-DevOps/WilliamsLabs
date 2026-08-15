**Project Name:** 06-MultiSite-Static-Routing-Lab
**Version:** 1.0
**Author:** Nicholas Williams
**Date Created:** August 12th 2026
**Last Updated:** August 15th 2026
**Status:** In Progress

# 1. Objective

Extend the existing Williams Labs enterprise network by connecting the primary campus to additional branch locations using routed WAN links and static routing.

The previous lab established a resilient Layer 3 campus network using Layer 3 switching, inter-VLAN routing, HSRP, Rapid PVST+, and EtherChannel.

As the organization grows beyond a single location, the existing infrastructure must be extended to provide connectivity between geographically separate networks.

This lab introduces routed WAN links and manually configured static routes while preserving the existing VLAN, Layer 3 switching, and HSRP infrastructure.

## Goals

- Extend the existing enterprise network to multiple locations.
- Configure routed WAN links between sites.
- Configure separate IP networks for each site.
- Configure static routes between remote networks.
- Configure default routes where appropriate.
- Understand next-hop routing between multiple routers.
- Verify end-to-end connectivity between sites.
- Use `show ip route` to examine static and connected routes.
- Use `traceroute` to observe the path between sites.
- Troubleshoot missing and incorrect static routes.
- Understand the limitations of manually configured routing as the network grows.

---

# 2. Network Topology

## Topology Type

This topology extends the existing Layer 3 campus network into a multi-site environment.

The primary campus retains the redundant Layer 3 core switches and HSRP configuration from Lab 5. Additional routers represent branch locations and provide routed WAN connections between the sites.

Static routes are used to provide connectivity between the LAN networks at each location.

## Advantages

- Extends the existing enterprise network to multiple locations.
- Static routes provide predictable and deterministic routing.
- The routing table clearly demonstrates how routers learn remote networks.
- Routed WAN links provide a foundation for future dynamic routing protocols.
- The existing HSRP and Layer 3 campus design remains intact.

## Limitations

- Static routes must be manually configured and maintained.
- Adding additional sites increases the number of routes that must be managed.
- Changes to the topology require manual routing updates.
- Static routing does not automatically adapt to link failures.
- The design will become increasingly difficult to scale as additional locations are added.

---

# 3. Physical Layout


## Devices

| Device | Model | Purpose |
|---|---|---|
| CORE SW1 | Cisco 3560 Layer 3 Switch | Primary Core Switch |
| CORE SW2 | Cisco 3560 Layer 3 Switch | Secondary Core Switch |
| ACCESS SW1 | Cisco 2950 Switch | Primary Campus Access Layer |
| ACCESS SW2 | Cisco 2950 Switch | Primary Campus Access Layer |
| ACCESS SW3 | Cisco 2950 Switch | Primary Campus Access Layer |
| ACCESS SW4 | Cisco 2950 Switch | Primary Campus Access Layer |
| R1 | Cisco Router | Primary Campus WAN Router |
| R2 | Cisco Router | Branch 1 WAN Router |
| R3 | Cisco Router | Branch 2 WAN Router |
| PC1-PC10 | End Devices | Primary Campus User Connectivity |
| Branch PCs | End Devices | Remote Site Connectivity Testing |

---

# 4. VLAN Design

The existing VLAN design from Lab 5 remains unchanged at the primary campus.

## VLAN Assignments

| VLAN | Name | Network | Default Gateway | Purpose |
|------|--------------|---------------|----------------|----------------|
| 10 | SALES | 10.0.10.0/24 | 10.0.10.1 | User workstations and devices for the Sales department |
| 20 | ENGINEERING | 10.0.20.0/24 | 10.0.20.1 | User workstations and devices for the Engineering department |
| 30 | HR | 10.0.30.0/24 | 10.0.30.1 | User workstations and devices for the HR department |
| 40 | MANAGEMENT | 10.0.40.0/24 | 10.0.40.1 | Manager and executive user devices |
| 999 | Unused VLAN | N/A | N/A | Unused native VLAN for trunk security |

---

## VLAN Addressing

The primary campus end devices retain the addressing from Lab 5.

| Device | VLAN | IP Address | Default Gateway |
|---|---|---|---|
| Manager PC 1 | VLAN 40 | 10.0.40.10/24 | 10.0.40.1 |
| Sales PC 1 | VLAN 10 | 10.0.10.10/24 | 10.0.10.1 |
| Sales PC 2 | VLAN 10 | 10.0.10.11/24 | 10.0.10.1 |
| Engineering PC 1 | VLAN 20 | 10.0.20.10/24 | 10.0.20.1 |
| Engineering PC 2 | VLAN 20 | 10.0.20.11/24 | 10.0.20.1 |
| Engineering PC 3 | VLAN 20 | 10.0.20.12/24 | 10.0.20.1 |
| Manager PC 2 | VLAN 40 | 10.0.40.11/24 | 10.0.40.1 |
| Engineering PC 4 | VLAN 20 | 10.0.20.13/24 | 10.0.20.1 |
| Engineering PC 5 | VLAN 20 | 10.0.20.14/24 | 10.0.20.1 |
| HR PC 1 | VLAN 30 | 10.0.30.10/24 | 10.0.30.1 |
| HR PC 2 | VLAN 30 | 10.0.30.11/24 | 10.0.30.1 |

---

# 5. Site Addressing

The existing primary campus networks are extended by adding separate networks for each branch.

## Site LANs

| Site | Network | Purpose |
|---|---|---|
| Primary Campus | 10.0.10.0/24 - 10.0.40.0/24 | Existing enterprise VLANs |
| Branch 1 | 10.0.20.0/24 | Branch 1 LAN |
| Branch 2 | 10.0.30.0/24 | Branch 2 LAN |

> The branch networks should remain distinct from any existing VLAN networks in the primary campus when the final topology is implemented. Addressing can be adjusted if required by the topology.

## WAN Links

| Link | Network | Device A | Device B |
|---|---|---|---|
| Primary ↔ Branch 1 | 10.0.100.0/30 | R1: 10.0.100.1 | R2: 10.0.100.2 |
| Primary ↔ Branch 2 | 10.0.100.4/30 | R1: 10.0.100.5 | R3: 10.0.100.6 |

---

# 6. Routing Design

The primary campus continues to use Layer 3 switching and HSRP for local inter-VLAN routing.

The WAN routers provide connectivity between locations.

Static routes are configured on the routers so that each router knows how to reach networks that are not directly connected.

The routing relationship is:

                    Branch 1
                   10.1.20.0/24
                        |
                       R2
                        |
                10.0.100.0/30
                        |
                        R1
                        |
                10.0.100.4/30
                        |
                       R3
                        |
                   Branch 2
                   10.2.30.0/24
                        |
                  Primary Campus
             10.0.10.0/24 - 10.0.40.0/24

---

# 7. Configuration Order

The existing infrastructure from Lab 5 should be recreated first.

The following configuration sections contain only the changes required to extend that infrastructure into a multi-site network.

## 1. Configure the WAN Routers

Configure basic settings on R1, R2, and R3.

    hostname R1
    no ip domain-lookup

Repeat for R2 and R3 using the appropriate hostname.

---

## 2. Configure R1 WAN Interfaces

R1 provides the WAN connections from the primary location to the branch routers.

### R1 → Branch 1

    interface g0/0
    ip address 10.0.100.1 255.255.255.252
    no shutdown

### R1 → Branch 2

    interface g0/1
    ip address 10.0.100.5 255.255.255.252
    no shutdown

Verify:

    show ip interface brief

Test directly connected WAN neighbors:

    ping 10.0.100.2
    ping 10.0.100.6

---

## 3. Configure R2

R2 represents Branch 1.

Configure the WAN interface:

    interface g0/0
    ip address 10.0.100.2 255.255.255.252
    no shutdown

Configure the Branch 1 LAN interface:

    interface g0/1
    ip address 10.1.20.1 255.255.255.0
    no shutdown

Verify:

    show ip interface brief

Test connectivity to R1:

    ping 10.0.100.1

---

## 4. Configure R3

R3 represents Branch 2.

Configure the WAN interface:

    interface g0/0
    ip address 10.0.100.6 255.255.255.252
    no shutdown

Configure the Branch 2 LAN interface:

    interface g0/1
    ip address 10.2.30.1 255.255.255.0
    no shutdown

Verify:

    show ip interface brief

Test connectivity to R1:

    ping 10.0.100.5

---

## 5. Configure Static Routes

Static routes must be configured so each router knows how to reach networks that are not directly connected.

### R1 — Routes to Branch Networks

R1 needs routes to the LAN networks behind R2 and R3.

    ip route 10.1.20.0 255.255.255.0 10.0.100.2
    ip route 10.2.30.0 255.255.255.0 10.0.100.6

Verify:

    show ip route

Expected routes:

    S    10.1.20.0/24 [1/0] via 10.0.100.2
    S    10.2.30.0/24 [1/0] via 10.0.100.6

---

### 6. Configure R2 Static Routes

R2 needs routes to the primary campus networks.

    ip route 10.0.10.0 255.255.255.0 10.0.100.1
    ip route 10.0.20.0 255.255.255.0 10.0.100.1
    ip route 10.0.30.0 255.255.255.0 10.0.100.1
    ip route 10.0.40.0 255.255.255.0 10.0.100.1

R2 can also reach Branch 2 through R1:

    ip route 10.2.30.0 255.255.255.0 10.0.100.1

Verify:

    show ip route

---

### 7. Configure R3 Static Routes

R3 needs routes to the primary campus networks.

    ip route 10.0.10.0 255.255.255.0 10.0.100.5
    ip route 10.0.20.0 255.255.255.0 10.0.100.5
    ip route 10.0.30.0 255.255.255.0 10.0.100.5
    ip route 10.0.40.0 255.255.255.0 10.0.100.5

R3 can also reach Branch 1 through R1:

    ip route 10.1.20.0 255.255.255.0 10.0.100.5

Verify:

    show ip route

---

### 8. Configure Branch End Devices

Configure the branch hosts with addresses from their respective LAN networks.

#### Branch 1 Host

    IP Address:      10.1.20.10
    Subnet Mask:     255.255.255.0
    Default Gateway: 10.1.20.1

#### Branch 2 Host

    IP Address:      10.2.30.10
    Subnet Mask:     255.255.255.0
    Default Gateway: 10.2.30.1

---

### 9. Verify Routing

Verify the routing table on each router:

    show ip route

Connected routes should appear as:

    C

Static routes should appear as:

    S

The objective is to understand that each router knows about:

Connected Networks

+

Static Routes

+

Default Route

---

### 10. Test End-to-End Connectivity

Test from the routers first.

#### R1

    ping 10.1.20.1
    ping 10.2.30.1

#### R2

    ping 10.0.10.2
    ping 10.2.30.1

#### R3

    ping 10.0.10.2
    ping 10.1.20.1

Then test from the end devices.

### Primary Campus → Branch 1

    ping 10.1.20.10

#### Primary Campus → Branch 2

    ping 10.2.30.10

#### Branch 1 → Primary Campus

    ping 10.0.10.10

#### Branch 2 → Primary Campus

    ping 10.0.10.10


# 12. Trace the Path

Use `traceroute` to observe how traffic travels between locations.

From R1:

    traceroute 10.1.20.10

From R2:

    traceroute 10.2.30.10

From an end device:

    tracert 10.2.30.10

The path should demonstrate that traffic passes through the appropriate WAN routers before reaching the remote network.

---

# 13. Test Default Routes

Configure a default route as an additional exercise.

Example:

    ip route 0.0.0.0 0.0.0.0 <next-hop>

Verify:

    show ip route

The route should appear as:

    S*

Compare the behavior of a specific static route with a default route.

---

# 14. Static Routing Troubleshooting

Deliberately introduce routing problems and troubleshoot them.

## Exercise 1 — Missing Route

Remove one of the static routes from R1.

    no ip route 10.1.20.0 255.255.255.0 10.0.100.2

Test connectivity to Branch 1.

Determine:

- Why the route disappeared.
- What happens to the packet.
- How the routing table changes.
- How connectivity can be restored.

---

## Exercise 2 — Incorrect Next Hop

Configure an incorrect next-hop address.

    ip route 10.1.20.0 255.255.255.0 10.0.100.6

Test connectivity and determine why the route does not reach the intended destination.

Restore the correct route afterward.

---

## Exercise 3 — Missing Return Route

Remove the route from a branch router back toward the primary campus.

Test connectivity from both directions.

Determine why:

Source → Destination

can fail even when the destination network is correctly configured.

Restore the missing return route.

---

# 15. Save Configuration

Save the completed configuration on each device.

    copy running-config startup-config

Verify:

    show startup-config

---

# 16. Verification Checklist

- [ ] Existing primary campus infrastructure recreated.
- [ ] R1 configured as the primary WAN router.
- [ ] R2 configured as Branch 1 router.
- [ ] R3 configured as Branch 2 router.
- [ ] WAN links configured.
- [ ] Branch LANs configured.
- [ ] Static routes configured.
- [ ] Routing tables verified.
- [ ] Primary campus can reach Branch 1.
- [ ] Primary campus can reach Branch 2.
- [ ] Branch 1 can reach the primary campus.
- [ ] Branch 2 can reach the primary campus.
- [ ] End-to-end connectivity verified.
- [ ] Traceroute performed.
- [ ] Default-route behavior explored.
- [ ] Static-route troubleshooting exercises completed.
- [ ] Configurations saved.

---

# 17. Future Improvements

The multi-site network now provides connectivity between multiple locations, but the routing design introduces a new operational problem.

Every remote network must be manually configured on the appropriate routers. As the organization adds more branches and redundant paths, the number of static routes will grow rapidly.

A change to the topology may also require administrators to manually update routing tables across multiple devices.

**Problem to solve:**

> How can the routers automatically learn about remote networks and adapt when the topology changes without requiring every route to be manually configured?

The next stage will replace the manually maintained routing relationships with **OSPF**, allowing routers to dynamically discover networks and calculate paths through the multi-site infrastructure.

| Improvement | Description |
|---|---|
| OSPF | Replace manually configured routes with dynamic routing so routers can automatically learn remote networks and adapt to topology changes. |
| OSPF Cost & Path Selection | Configure and examine OSPF metrics to understand how routers select preferred paths. |
| Route Summarization | Reduce the size of routing tables as the number of networks and locations grows. |
| WAN Redundancy | Add additional WAN paths between locations and allow dynamic routing to select an alternate path when a link fails. |
| DHCP Relay | Allow centralized DHCP services to provide addressing to hosts across the newly connected remote networks. |