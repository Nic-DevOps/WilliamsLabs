# Lab 10 — Active Directory Lab

Project Name: 10-Active-Directory-Lab
Author: Nicholas Williams
Date Created: September 19th, 2026
Last Updated: September 19th, 2026
Status: In Progress

# 1. Overview

This lab stands up a Windows Server 2022 domain controller and builds out core Active Directory Domain Services (AD DS): DNS, an OU structure, users/groups, and Group Policy. Windows Server 2022 will be downloaded (Microsoft evaluation ISO) and installed on a VM hosted in VMware (Workstation/ESXi), then promoted to a domain controller. Client machines will be joined to the domain to verify authentication and policy application.

# 2. Planned Environment

Component | Value
---|---
Hypervisor | VMware (Workstation/ESXi)
Server OS | Windows Server 2022, Standard/Datacenter (Server Core)
Computer Name | AD-DC01
Workgroup (pre-promotion) | WORKGROUP
Remote Management | Enabled
Site / VLAN | HQ, VLAN 50 (Net-Mgmt)
IP Address | 10.10.50.23/24
Default Gateway | 10.10.50.1
Domain Controller Role | AD DS, DNS
Client OS | Windows 10/11 (domain-joined)

AD-DC01 joins the existing HQ Net-Mgmt VLAN (10.10.50.0/24) established in Labs 06/09, alongside the DHCP server (10.10.50.22) and monitoring host (10.10.50.25), keeping it consistent with the lab's `10.<site>.<vlan>.<host>` addressing convention.

# 3. Objectives

- [x] Download Windows Server 2022 and build the VM in VMware
- [x] Install Windows Server 2022 (Server Core) and configure base networking (computer name, workgroup, remote management)
- [ ] Promote the server to a domain controller (AD DS)
- [ ] Configure DNS for the domain
- [ ] Create OU structure, users, and groups
- [ ] Configure Group Policy Objects (GPOs)
- [ ] Join client machines to the domain
- [ ] Verify authentication and policy application

# 4. Topology

TODO: Add topology diagram once the VM and domain are built.

<!-- Images live in the shared assets folder: ../assets/10-Active-Directory-Lab/
     Example: ![Topology Diagram](../assets/10-Active-Directory-Lab/topology.png) -->

# 5. Steps

## 5.1 VM and OS Installation

- Created a new VM in VMware and installed Windows Server 2022 (Server Core).
- Using the Server Configuration tool (`sconfig`) at the CLI, set:
  - Computer name: `AD-DC01`
  - Workgroup: `WORKGROUP` (pre-promotion; will be replaced once the server is promoted to a domain controller)
  - Remote Management: Enabled (allows management via Server Manager/PowerShell remoting from another machine)

## 5.2 Network Configuration

The VM's network adapter was moved off the default NAT/VMware network and onto the CML lab network so AD-DC01 can reach the rest of the HQ topology (previously 192.168.11.144 on VMware's default network).

A static IP was assigned within the HQ Net-Mgmt VLAN (10.10.50.0/24) using PowerShell at the Server Core CLI:

```powershell
Get-NetAdapter

New-NetIPAddress -InterfaceIndex <ifIndex> -IPAddress 10.10.50.23 -PrefixLength 24 -DefaultGateway 10.10.50.1
Set-DnsClientServerAddress -InterfaceIndex <ifIndex> -ServerAddresses 10.10.50.1
```

Verify:
```powershell
Get-NetIPAddress -InterfaceIndex <ifIndex>
Test-NetConnection 10.10.50.1
```

TODO: Continue documenting configuration steps as the lab progresses (AD DS role install, promotion to domain controller, DNS, OUs/users/groups, GPOs, client domain join).

# 6. Verification and Testing

TODO: Document testing/verification steps and results (e.g., domain login from a joined client, GPO application, DNS resolution).

# 7. Summary and Future Improvements

TODO.

## Future Improvements

Improvement | Description
---|---
DHCP Integration | Issue domain-aware DHCP options (DNS suffix, WPAD, etc.) once integrated with Lab 09 DHCP.
Backup DC | Add a second domain controller for redundancy.
Certificate Services | Stand up AD CS for internal PKI.
Monitoring | Extend Prometheus/Grafana monitoring to the domain controller.
