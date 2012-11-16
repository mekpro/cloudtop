%include templates/header 

<div class="container-fluid">
  <h1>{{pagename}}</h1>
  <p>Last Update: {{dt}}</p>
  <div> 
    <ul id=hostinfo>
      <li id=hostname>Hostname: <span>h.info.hostname</span></li>
      <li id=cpus>CPU Core: <span>h.info.cpus</span></li>
      <li id=doms_count>Running VM: <span>h.info.doms_count</span></li>
    </ul>
    <div class=graph id=graph_cpu></div>
    <div class=graph id=graph_mem></div>
  </div>
</div>

%include templates/footer

<script>
  h = rpc('get_host_stats', ['{{start}}','{{end}}','{{hostname}}']);
  console.log(h)
  $("#hostinfo #hostname span").text(h.info.hostname)
  $("#hostinfo #cpus span").text(h.info.cpus)
  $("#hostinfo #doms_count span").text(h.info.doms_count)

  graph = Flotr.draw(graph_cpu, [ h.graph.cputime.data[0]], {yaxis : { max:1, min:0 }} );

</script>


