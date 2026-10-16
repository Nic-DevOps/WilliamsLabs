# Uptime monitoring (Uptime Kuma)

Self-hosted uptime checks for williamslabs.ca, with a public status page and
small badges embedded on the home page ("Droplet Uptime" panel under Monitoring).

## 1. Deploy (on the monitoring VM)
```bash
mkdir -p ~/uptime-kuma && cd ~/uptime-kuma
# copy docker-compose.yml here
docker compose up -d
# private admin access over your tailnet only:
sudo tailscale serve --bg 3001      # then open https://<vm>.<tailnet>.ts.net
```
Create the admin account immediately and enable 2FA (Settings → Security).

## 2. Create monitors — in this order (badge IDs in index.html assume monitor 1)
| ID | Name | Type | Target | Interval |
|----|------|------|--------|----------|
| 1 | williamslabs.ca | HTTP(s) – Keyword | https://williamslabs.ca (keyword: `Williams Labs`) | 60s |
| 2 | TLS cert | (tick "Certificate Expiry Notification" on monitor 1) | | |
| 3 | Monitoring VM | Ping / TCP | Prometheus port on the VM (internal only) | 60s |

If your IDs differ, edit the `/api/badge/<id>/` numbers in `html/index.html`.
Add a notification channel (Discord/ntfy/email) and attach it to every monitor.

## 3. Public status page
Status Pages → New → slug `status` → add monitor 1 only
(badges only work for monitors on a published status page). Don't add
internal-only monitors (VM, devices) to the public page.

## 4. Expose only the status page
Add the block from `cloudflared-ingress.yml` to your cloudflared config, add the
DNS route, restart cloudflared. Verify:
```bash
curl -I https://status.williamslabs.ca/status/status     # 200
curl -I https://status.williamslabs.ca/dashboard               # 404 (admin not exposed)
```
Optionally add a Cloudflare WAF rate-limit rule for the hostname.

## 5. Blind spot: Kuma lives in the homelab
If the homelab loses power/internet, Kuma can't alert you. Add one free external
check as a backstop (UptimeRobot, or a Kuma "Push" monitor pinged by healthchecks.io
that alerts when the heartbeat stops).

## Site behaviour
`html/js/uptime.js` hides the panel automatically if the badges can't load, so a
down tunnel never shows broken images.
