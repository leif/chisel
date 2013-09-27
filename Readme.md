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

## Hacking

These instructions are not entirely tested, but might get chisel running in a virtualenv. You should use virtualenv 1.9.1 or later.
```
virtualenv chisel
cd chisel
venv=$(pwd)
echo "export LD_LIBRARY_PATH=$venv" >> ./bin/activate
. ./bin/activate
mkdir src && cd src
tgz_url=https://download.libsodium.org/libsodium/releases/libsodium-0.4.2.tar.gz
hash=1a7901cdd127471724e854a8eb478247dc0ca67be549345c75fc6f2d4e05ed39
tgz=$(basename $tgz_url)
curl $tgz_url > $tgz
[ "`sha256sum $tgz`" == "$h  $tgz" ] &&
tar xf libsodium-0.4.2.tar.gz &&
cd libsodium-0.4.2
&& ./configure --prefix=$venv && make && make install && cd ..
git clone https://github.com/leif/chisel && cd chisel
pip install requirements.txt
trial chisel
```
