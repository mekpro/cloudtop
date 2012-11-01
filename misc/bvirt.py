import libvirt

uri = "qemu+ssh:///system"
conn = libvirt.openReadOnly(uri)
doms = conn.listDomainsID()
dom1 = conn.lookupByID(doms[0])
dom2 = conn.lookupByID(doms[1])
