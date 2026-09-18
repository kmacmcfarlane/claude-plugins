# TODO

- [ ] **Script the qBittorrent add via WebUI API** (manual for the Judy Collins
      release). Creds live in the talos cluster (clustertool repo,
      `clusters/main/kubernetes/apps/qbittorrent/`). Needs:
  - add torrent from hooper, save path `incoming/movies`
  - tag `keep` (qbit_manage reaper only deletes untagged noHL torrents)
  - verify the PTP announce URL actually announces (tracker status in WebUI)
  - verify reaper behavior with a real PTP torrent
- [ ] Optional: auto-upload screenshots + poster to ptpimg.me
      (`PTPIMG_API_KEY` in `.env`; POST `https://ptpimg.me/upload.php`).
- [ ] Optional: automate the PTP coexistence check (search API with passkey)
      before encoding.
