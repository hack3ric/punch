My NAT hole punching scripts, consisting of the following:

- **kvsh**: Key-value store. The script acts as a fake shell for system users and allows reading and writing simple key-value pairs through SSH. The storage is backed by a directory, and the inputs are sanitized to prevent access outside of that directory.

  To setup kvsh on a server (assuming SSH):

  ```console
  # useradd -m -s /path/to/kvsh <username>
  # passwd
  ```

  And to use it:

  ```console
  $ ssh <username>@<host> read <key>
  $ ssh <username>@<host> write <key> <value>
  ```

- **stun-client**: STUN client in Python without third-party dependencies. There is no STUN client in OpenWrt repository (as of 24.10) so I decided to just write one on my own. Currently only supports UDP.

  ```console
  $ ./stun-client [--server <host:port> ...] [--port <port>]
  ```

- **punch-wg**: Hole punching script for WireGuard

  ```console
  # ./punch-wg <interface> <username>@<host> <self_entry> <peer_entry> <peer_public_key>
  ```
