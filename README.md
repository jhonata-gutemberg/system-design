# Key Value Store

## Requirements

### Functional
- [x] Should be able to put data on the storage
- [x] Should be able to retrieve data from the storage

### Non-functional
- [ ] The size of a key-value pair is small: less than 10 KB
- [ ] Ability to store big data
- [ ] High availability: The system responds quickly, even during failures
- [ ] High scalability: The system can be scaled to support large data set
- [ ] Automatic scaling: The addition/deletion of servers should be automatic based on traffic
- [ ] Tunable consistency
- [ ] Low latency

## Architecture
![Key-value-store](docs/key-value-store.excalidraw.png)
<!-- - Virtual nodes

### Inconsistency resolution
- Versioning
- Vector locks (vector clocks)

### Failure detection
- All-to-all multicast
- Gossip protocol

### Temporary failures
- Quorum approach
- Sloppy quorum
- Hinted handoff

### Permanent failures
- Anti-entropy protocol
- Merkle tree
-->