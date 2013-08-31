Chisel will implement a decentralized add-only set.

It is intended to provide a highly-available censorship-resistant system for
storage and retrieval of both confidential and public data.

## Potential uses

* email hosting

* web publishing

* reliably logging anomalous events

* preventing forced git updates

## Glossary

* **Pool**: a content-addressable data store

* **Scroll**: an ordered set of hashes

* **ChiselSet**: an object combining a Pool, a Scroll, a write policy, and a collection of notaries

* **Notary**: maintains ChiselSets and services read and write operations on them
