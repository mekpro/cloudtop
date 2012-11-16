%include templates/header 

<div class="row">
  <div class="span4">
    <h1>{{hostname}}</h1>
    <p>Last Update: {{dt}}</p>
    <div> 
      <ul id=hostinfo>
        <li id=hostname>Hostname: <span>h.info.hostname</span></li>
        <li id=cpus>CPU Core: <span>h.info.cpus</span></li>
        <li id=doms_count>Running VM: <span>h.info.doms_count</span></li>
      </ul>
    </div>
  </div>
  <div class="span4">
    <p>CPU</p>
    <div class=graph id=graph_cpu></div>
  </div>
  <div class="span4">
    <p>MEM</p>
    <div class=graph id=graph_mem></div>
  </div>
  </div>
</div>

<h1>Virtual Machines</h1>
<div class="span12">
<table id=vmtable class="table">
  <tr>
    <th>Virtual Machine</th>
    <th>CPU</th>
    <th>RAM</th>
    <th>Net</th>
    <th>Disk</th>
  </tr>
</table>
</div>

%include templates/footer

<script>
  host = rpc('get_host_stats', ['{{start}}','{{end}}','{{hostname}}']);
  console.log(host)
  doms = rpc('get_doms_stats_from_host', ['{{start}}','{{end}}','{{hostname}}']);
  console.log(doms)

  $("#hostinfo #hostname span").text(host.info.hostname)
  $("#hostinfo #cpus span").text(host.info.cpus)
  $("#hostinfo #doms_count span").text(host.info.doms_count)

  Flotr.draw(graph_cpu, host.graph.cputime.data, 
    {yaxis : { max:100, min:0 }} );

  Flotr.draw(graph_mem, host.graph.mem.data, 
    {yaxis : {min:0 }} );

  for(var i=0; i<doms.length; i++) {
    console.log(doms[i])
    tr =  "<td>" + doms[i].info.domname + "</td>";
    tr += "<td><div class=minigraph domcpu></div></td>" ;
    tr += "<td><div class=minigraph dommem></div></td>" ;
    tr += "<td><div class=minigraph domnet></div></td>" ;
    tr += "<td><div class=minigraph domdisk></div></td>" ;
    $("#vmtable").append($('<tr>')
      .append($(tr)
      )
    );
    
    // Draw graphs for a newly inserted row
    Flotr.draw($("#vmtable tr :last td:eq(1) div"), [doms[i].graph.cpu.data], 
      {yaxis : {min:0 }} );

  } 

</script>
