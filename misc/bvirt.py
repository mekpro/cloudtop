import libvirt

uri = "qemu+ssh:///system"
conn = libvirt.openReadOnly(uri)
doms = conn.listDomainsID()
dom = conn.lookupByID(doms[0])
