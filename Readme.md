Chisel will implement a decentralized add-only set.

It is intended to provide a censorship-resistant highly-available system for storage and retrieval of both confidential and public data.

## Potential uses

* email hosting

* web publishing

* reliably logging anomalous events

* auditable distribution of software updates

## Glossary

* **Pool**: a content-addressable data store

* **Scroll**: an ordered set of hashes

* **ChiselSet**: the decentralized writable resource. Combines a Pool, a Scroll, a write policy, and a collection of notaries

* **Notary**: maintains ChiselSets and services read and write operations on them

